"""
Mapping Service — semantic topic-to-chunk mapping using SBERT.

Responsibilities:
- Load the custom fine-tuned SBERT model (or fallback to HuggingFace)
- Encode syllabus topics and textbook chunks
- Map each topic to the most relevant chunks using cosine similarity
- Apply diversity filtering to avoid redundant chunk selection
"""

import os
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
    Encapsulates SBERT-based topic-to-chunk semantic mapping.

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

    def map_topics_to_chunks(
        self,
        topics: List[str],
        chunks: List[Dict[str, Any]],
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        diversity_threshold: float = DIVERSITY_THRESHOLD,
        max_chunks: int = MAX_CHUNKS_PER_TOPIC,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Map each syllabus topic to the most semantically relevant textbook chunks.

        Args:
            topics: List of topic strings from the syllabus.
            chunks: List of chunk dicts (must have 'text', 'chunk_id', optionally 'page').
            similarity_threshold: Minimum cosine similarity to consider a match.
            diversity_threshold: Maximum inter-chunk similarity for diversity filtering.
            max_chunks: Maximum number of chunks to map per topic.

        Returns:
            Dict mapping each topic string to a list of matched chunk metadata.
        """
        if not topics or not chunks:
            logger.warning("Empty topics or chunks — returning empty mapping")
            return {}

        # Encode topics and chunks
        topic_embeddings = self.model.encode(topics)
        chunk_texts = [c["text"] for c in chunks]
        chunk_embeddings = self.model.encode(chunk_texts)

        # Compute similarity matrix: topics × chunks
        from sklearn.metrics.pairwise import cosine_similarity

        similarity_matrix = cosine_similarity(topic_embeddings, chunk_embeddings)
        mapping: Dict[str, List[Dict[str, Any]]] = {}

        for i, topic in enumerate(topics):
            topic_key = str(topic).strip()
            scores = similarity_matrix[i]

            # Step 1: Filter by threshold
            candidates = [
                (idx, float(score))
                for idx, score in enumerate(scores)
                if score >= similarity_threshold
            ]

            # Fallback: if no candidates pass threshold, take the best one
            if not candidates:
                best_idx = int(scores.argmax())
                mapping[topic_key] = [{
                    "chunk_id": chunks[best_idx]["chunk_id"],
                    "page": chunks[best_idx].get("page"),
                    "score": float(scores[best_idx]),
                }]
                continue

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
