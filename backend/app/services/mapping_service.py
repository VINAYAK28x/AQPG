"""
Mapping Service — semantic topic-to-chunk mapping using SBERT.

Responsibilities:
- Load the custom fine-tuned SBERT model (or fallback to HuggingFace)
- Encode syllabus topics and textbook chunks
- Map each module to the most relevant chunks using cosine similarity
- Apply diversity filtering to avoid redundant chunk selection
- Deduplicate near-identical content within each module
"""

import os
import re
import glob
import pickle
import hashlib
import logging
from typing import List, Dict, Any

from app.core.config import (
    SBERT_MODEL_PATH,
    SBERT_FALLBACK_MODEL,
    SIMILARITY_THRESHOLD,
    DIVERSITY_THRESHOLD,
    MAX_CHUNKS_PER_TOPIC,
    PROCESSED_DATA_DIR,
)

logger = logging.getLogger(__name__)


class MappingService:
    """
    Encapsulates SBERT-based module-to-chunk semantic mapping.

    Loads the custom SBERT model from the local models/ directory.
    Falls back to a HuggingFace model if the local model is not found.
    """

    # Maximum number of embedding cache files to keep on disk
    _MAX_CACHE_FILES = 3

    def __init__(self):
        self._model = None
        self._cache_dir = os.path.join(str(PROCESSED_DATA_DIR), "cache")
        os.makedirs(self._cache_dir, exist_ok=True)

    @property
    def model(self):
        """Lazy-load the SBERT model on first use."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            if os.path.exists(SBERT_MODEL_PATH):
                logger.info(f"Loading custom SBERT model from {SBERT_MODEL_PATH}")
                self._model = SentenceTransformer(SBERT_MODEL_PATH)
            else:
                logger.warning(
                    f"Custom SBERT model not found at {SBERT_MODEL_PATH}. "
                    f"Falling back to {SBERT_FALLBACK_MODEL}"
                )
                self._model = SentenceTransformer(SBERT_FALLBACK_MODEL)
        return self._model

    # =======================================================
    # Embedding Cache (hash-based with auto-cleanup)
    # =======================================================

    @staticmethod
    def _compute_hash(texts: List[str]) -> str:
        """Compute an MD5 hash of the concatenated text for cache keying."""
        text_blob = "".join(texts)
        return hashlib.md5(text_blob.encode()).hexdigest()

    def _encode_with_cache(self, texts: List[str], prefix: str = "emb"):
        """
        Encode texts with SBERT, using a hash-based disk cache.
        If embeddings for these exact texts already exist, load from pickle.
        Otherwise compute, save, and return.
        """
        import numpy as np  # noqa: local import to match existing pattern

        text_hash = self._compute_hash(texts)
        cache_path = os.path.join(self._cache_dir, f"{prefix}_{text_hash}.pkl")

        if os.path.exists(cache_path):
            logger.info(f"[Cache HIT] Loading embeddings from {cache_path}")
            with open(cache_path, "rb") as f:
                return pickle.load(f)

        logger.info(f"[Cache MISS] Computing embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts)

        with open(cache_path, "wb") as f:
            pickle.dump(embeddings, f)
        logger.info(f"[Cache SAVE] Saved embeddings to {cache_path}")

        self._cleanup_cache(prefix)
        return embeddings

    def _cleanup_cache(self, prefix: str = "emb"):
        """Keep only the most recent N cache files per prefix."""
        pattern = os.path.join(self._cache_dir, f"{prefix}_*.pkl")
        cache_files = sorted(glob.glob(pattern), key=os.path.getmtime)
        while len(cache_files) > self._MAX_CACHE_FILES:
            oldest = cache_files.pop(0)
            os.remove(oldest)
            logger.info(f"[Cache Cleanup] Removed old cache: {oldest}")

    def map_modules_to_chunks(
        self,
        structured_syllabus: Dict[str, Any],
        chunks: List[Dict[str, Any]],
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        diversity_threshold: float = DIVERSITY_THRESHOLD,
        chunks_per_topic: int = 4,
        dedup_threshold: float = 0.92,
    ) -> Dict[str, Any]:
        """
        Map each active syllabus topic directly to the most semantically relevant textbook chunks.
        
        This establishes strict, granular context bounds so large/hallucinated
        context mixing is prevented during question generation.
        """
        modules = structured_syllabus.get("modules", {})
        if not modules or not chunks:
            logger.warning("Empty modules or chunks — returning empty mapping")
            return {}

        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        # Encode all chunk texts (with caching)
        chunk_texts = [c["text"] for c in chunks]
        chunk_embeddings = self._encode_with_cache(chunk_texts, prefix="chunks")

        module_mapping: Dict[str, Any] = {}

        for module_name, module_data in modules.items():
            topics = module_data.get("topics", [])
            if not topics:
                continue

            topic_mappings = {}
            module_all_selected_indices = set()

            for topic in topics:
                # Fetch embedding per specific topic
                topic_emb = self._encode_with_cache([topic], prefix="topics")[0].reshape(1, -1)
                
                # Compare THIS specific topic to ALL chunks
                scores = cosine_similarity(topic_emb, chunk_embeddings)[0]

                # Filtering Candidates
                candidates = [
                    (idx, float(score))
                    for idx, score in enumerate(scores)
                    if score >= similarity_threshold
                ]

                # Fallback to top 4 if thresh fails to capture anything
                if not candidates:
                    top_indices = np.argsort(scores)[-4:][::-1]
                    candidates = [(int(idx), float(scores[idx])) for idx in top_indices]

                candidates.sort(key=lambda x: x[1], reverse=True)

                # Diversity filtering specifically for this topic
                selected_indices = []
                for idx, score in candidates:
                    if not selected_indices:
                        selected_indices.append(idx)
                        continue

                    # Assure diversity
                    is_diverse = all(
                        cosine_similarity(
                            [chunk_embeddings[idx]], [chunk_embeddings[sel_idx]]
                        )[0][0] < diversity_threshold
                        for sel_idx in selected_indices
                    )

                    if is_diverse:
                        selected_indices.append(idx)

                    if len(selected_indices) >= chunks_per_topic:
                        break

                # Deduplicate near-identical sentences within selected chunks
                selected_texts = [chunk_texts[idx] for idx in selected_indices]
                deduped_indices = self._deduplicate_chunks(
                    selected_indices, selected_texts, dedup_threshold
                )

                # Store deduplicated results for this specific topic
                topic_mappings[topic] = [
                    {
                        "chunk_id": chunks[idx]["chunk_id"],
                        "page": chunks[idx].get("page"),
                        "score": float(scores[idx]),
                    }
                    for idx in deduped_indices
                ]
                
                module_all_selected_indices.update(deduped_indices)

            # Build a generalized embedding_ready_text for the whole module just in case
            generalized_raw_text = " ".join([chunk_texts[idx] for idx in module_all_selected_indices])
            embedding_ready = self._build_embedding_text(generalized_raw_text)

            module_mapping[module_name] = {
                "topics": topics,
                "embedding_ready_text": embedding_ready,
                "topic_mappings": topic_mappings
            }

        logger.info(f"Mapped {len(module_mapping)} modules granularly by topics")
        return module_mapping

    def _deduplicate_chunks(
        self,
        indices: List[int],
        texts: List[str],
        threshold: float,
    ) -> List[int]:
        """
        Remove near-duplicate chunks based on text similarity.

        Args:
            indices: List of chunk indices.
            texts: Corresponding texts for those indices.
            threshold: Similarity above this = duplicate.

        Returns:
            Filtered list of indices with duplicates removed.
        """
        if len(indices) <= 1:
            return indices

        from sklearn.metrics.pairwise import cosine_similarity

        text_embeddings = self.model.encode(texts)
        sim_matrix = cosine_similarity(text_embeddings)

        keep = [0]  # Always keep the first (highest-scoring)
        for i in range(1, len(indices)):
            is_unique = all(
                sim_matrix[i][j] < threshold
                for j in keep
            )
            if is_unique:
                keep.append(i)

        return [indices[i] for i in keep]

    def _build_embedding_text(self, raw_text: str) -> str:
        """
        Clean raw text for use in semantic search / vector embeddings.

        Removes special characters, extra whitespace, and normalizes formatting.
        """
        # Remove special chars except basic punctuation
        cleaned = re.sub(r"[^\w\s]", " ", raw_text)
        # Collapse whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    # Keep the old method for backward compatibility
    def map_topics_to_chunks(
        self,
        topics: List[str],
        chunks: List[Dict[str, Any]],
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        diversity_threshold: float = DIVERSITY_THRESHOLD,
        max_chunks: int = MAX_CHUNKS_PER_TOPIC,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Legacy method: Map each syllabus topic to the most relevant chunks.
        Kept for backward compatibility.
        """
        if not topics or not chunks:
            logger.warning("Empty topics or chunks — returning empty mapping")
            return {}

        topic_embeddings = self.model.encode(topics)
        chunk_texts = [c["text"] for c in chunks]
        chunk_embeddings = self.model.encode(chunk_texts)

        from sklearn.metrics.pairwise import cosine_similarity

        similarity_matrix = cosine_similarity(topic_embeddings, chunk_embeddings)
        mapping: Dict[str, List[Dict[str, Any]]] = {}

        for i, topic in enumerate(topics):
            topic_key = str(topic).strip()
            scores = similarity_matrix[i]

            candidates = [
                (idx, float(score))
                for idx, score in enumerate(scores)
                if score >= similarity_threshold
            ]

            if not candidates:
                best_idx = int(scores.argmax())
                mapping[topic_key] = [{
                    "chunk_id": chunks[best_idx]["chunk_id"],
                    "page": chunks[best_idx].get("page"),
                    "score": float(scores[best_idx]),
                }]
                continue

            candidates.sort(key=lambda x: x[1], reverse=True)

            selected_indices = []
            for idx, score in candidates:
                if not selected_indices:
                    selected_indices.append(idx)
                    continue

                is_diverse = all(
                    cosine_similarity(
                        [chunk_embeddings[idx]], [chunk_embeddings[sel_idx]]
                    )[0][0] < diversity_threshold
                    for sel_idx in selected_indices
                )

                if is_diverse:
                    selected_indices.append(idx)

                if len(selected_indices) >= max_chunks:
                    break

            mapping[topic_key] = [
                {
                    "chunk_id": chunks[idx]["chunk_id"],
                    "page": chunks[idx].get("page"),
                    "score": float(scores[idx]),
                }
                for idx in selected_indices
            ]

        logger.info(f"Mapped {len(topics)} topics to chunks")
        return mapping


# Module-level singleton for reuse across requests
mapping_service = MappingService()
