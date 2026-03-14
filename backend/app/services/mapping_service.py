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
import logging
from typing import List, Dict, Any

from app.core.config import (
    SBERT_MODEL_PATH,
    SBERT_FALLBACK_MODEL,
    SIMILARITY_THRESHOLD,
    DIVERSITY_THRESHOLD,
    MAX_CHUNKS_PER_TOPIC,
)

logger = logging.getLogger(__name__)


class MappingService:
    """
    Encapsulates SBERT-based module-to-chunk semantic mapping.

    Loads the custom SBERT model from the local models/ directory.
    Falls back to a HuggingFace model if the local model is not found.
    """

    def __init__(self):
        self._model = None

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

    def map_modules_to_chunks(
        self,
        structured_syllabus: Dict[str, Any],
        chunks: List[Dict[str, Any]],
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        diversity_threshold: float = DIVERSITY_THRESHOLD,
        max_chunks_per_module: int = MAX_CHUNKS_PER_TOPIC * 3,
        dedup_threshold: float = 0.92,
    ) -> Dict[str, Any]:
        """
        Map each module to the most semantically relevant textbook chunks.

        This is a module-level mapping — instead of mapping individual topics,
        it creates a combined module embedding from all its topics and maps
        entire modules to relevant chunks.

        Args:
            structured_syllabus: The structured syllabus dict with 'modules' key.
            chunks: List of chunk dicts (must have 'text', 'chunk_id', optionally 'page').
            similarity_threshold: Minimum cosine similarity to consider a match.
            diversity_threshold: Maximum inter-chunk similarity for diversity filtering.
            max_chunks_per_module: Maximum number of chunks per module.
            dedup_threshold: Similarity threshold for deduplication (above this = duplicate).

        Returns:
            Dict mapping each module name to its mapping data:
            {
                "MODULE I": {
                    "topics": [...],
                    "raw_text": "concatenated chunk text",
                    "embedding_ready_text": "cleaned text",
                    "chunks": [{"chunk_id": ..., "page": ..., "score": ...}, ...]
                }
            }
        """
        modules = structured_syllabus.get("modules", {})
        if not modules or not chunks:
            logger.warning("Empty modules or chunks — returning empty mapping")
            return {}

        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        # Encode all chunk texts
        chunk_texts = [c["text"] for c in chunks]
        chunk_embeddings = self.model.encode(chunk_texts)

        module_mapping: Dict[str, Any] = {}

        for module_name, module_data in modules.items():
            topics = module_data.get("topics", [])
            if not topics:
                continue

            # Create module embedding as mean of all topic embeddings
            topic_embeddings = self.model.encode(topics)
            module_embedding = np.mean(topic_embeddings, axis=0, keepdims=True)

            # Compute similarity of module embedding against all chunks
            scores = cosine_similarity(module_embedding, chunk_embeddings)[0]

            # Step 1: Filter by threshold
            candidates = [
                (idx, float(score))
                for idx, score in enumerate(scores)
                if score >= similarity_threshold
            ]

            # Fallback: if no candidates pass threshold, take the top 3
            if not candidates:
                top_indices = np.argsort(scores)[-3:][::-1]
                candidates = [(int(idx), float(scores[idx])) for idx in top_indices]

            # Step 2: Sort by score descending
            candidates.sort(key=lambda x: x[1], reverse=True)

            # Step 3: Diversity-aware selection
            selected_indices = []
            for idx, score in candidates:
                if not selected_indices:
                    selected_indices.append(idx)
                    continue

                # Check diversity against already-selected chunks
                is_diverse = all(
                    cosine_similarity(
                        [chunk_embeddings[idx]], [chunk_embeddings[sel_idx]]
                    )[0][0] < diversity_threshold
                    for sel_idx in selected_indices
                )

                if is_diverse:
                    selected_indices.append(idx)

                if len(selected_indices) >= max_chunks_per_module:
                    break

            # Step 4: Deduplicate near-identical sentences within selected chunks
            selected_texts = [chunk_texts[idx] for idx in selected_indices]
            deduped_indices = self._deduplicate_chunks(
                selected_indices, selected_texts, dedup_threshold
            )

            # Build aggregated raw_text from unique chunks
            raw_text_parts = []
            for idx in deduped_indices:
                raw_text_parts.append(chunk_texts[idx])
            raw_text = " ".join(raw_text_parts)

            # Build embedding-ready text
            embedding_ready = self._build_embedding_text(raw_text)

            module_mapping[module_name] = {
                "topics": topics,
                "raw_text": raw_text,
                "embedding_ready_text": embedding_ready,
                "chunks": [
                    {
                        "chunk_id": chunks[idx]["chunk_id"],
                        "page": chunks[idx].get("page"),
                        "score": float(scores[idx]),
                    }
                    for idx in deduped_indices
                ],
            }

        logger.info(f"Mapped {len(module_mapping)} modules to chunks")
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
