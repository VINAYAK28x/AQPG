"""
Context compression, module normalisation, and topic-token extraction helpers.

Extracted from question_service.py to keep the service file focused on orchestration.
"""

import re
import logging
from typing import List, Dict, Optional

from app.utils.question_constants import CONTEXT_STOPWORDS

logger = logging.getLogger(__name__)


# =====================================================
# Module Name Normalisation
# =====================================================

def normalize_module_name(name: str) -> str:
    """
    Normalize a module name so that both Arabic and Roman numeral
    variants map to the same canonical form.
    e.g. "Module 1" -> "module_1", "Module I" -> "module_1",
         "Module IV" -> "module_4", "Module 4" -> "module_4"
    """
    roman_to_arabic = {
        "i": "1", "ii": "2", "iii": "3", "iv": "4",
        "v": "5", "vi": "6", "vii": "7", "viii": "8",
    }
    text = name.strip().lower()
    # Try to extract "module <token>" pattern
    m = re.match(r"^module\s+(.+)$", text)
    if m:
        token = m.group(1).strip()
        # If the token is a Roman numeral, convert it
        if token in roman_to_arabic:
            return f"module_{roman_to_arabic[token]}"
        # If it's already an Arabic numeral, use it
        if token.isdigit():
            return f"module_{token}"
        # Otherwise, return a cleaned version
        return f"module_{token}"
    return text.replace(" ", "_")


def find_matching_key(module: str, keys) -> Optional[str]:
    """Find the dictionary key that matches the given module name exactly
    after normalization. Returns the original key or None."""
    norm = normalize_module_name(module)
    for key in keys:
        if normalize_module_name(key) == norm:
            return key
    return None


# =====================================================
# Subject & Topic Helpers
# =====================================================

def normalize_subject_name(subject: Optional[str]) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", (subject or "").strip().lower())
    return " ".join(normalized.split())


def mark_bucket(marks: Optional[int]) -> str:
    if marks is None:
        return "unknown"
    if marks <= 5:
        return "short"
    if marks <= 8:
        return "medium"
    return "long"


def extract_topic_tokens(topic: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]+", (topic or "").lower())
    return [
        token for token in tokens
        if len(token) > 2 and token not in CONTEXT_STOPWORDS
    ]


# =====================================================
# Context Compression (SBERT + BM25)
# =====================================================

def compress_context(
    chunks: List[str],
    topic: str,
    max_tokens: int = 400,
    sbert_model=None,
) -> str:
    """
    Re-rank input chunks by combined SBERT + BM25 relevance, then extract highest-scoring
    sentences within a token budget.
    """
    if not chunks:
        return ""

    if sbert_model is None:
        return " ".join(chunks)[:max_tokens * 5]  # rough fallback

    from sentence_transformers import util

    # nltk sent_tokenize
    try:
        from nltk.tokenize import sent_tokenize
    except Exception:
        sent_tokenize = None

    tokenized_chunks = [c.lower().split() for c in chunks]
    bm25_scores = None
    try:
        from rank_bm25 import BM25Okapi

        bm25 = BM25Okapi(tokenized_chunks)
        bm25_scores = bm25.get_scores(topic.lower().split())
    except Exception:
        # If rank_bm25 is missing, degrade to SBERT-only scoring.
        bm25_scores = [0.0 for _ in chunks]

    topic_vec = sbert_model.encode(topic, convert_to_tensor=True)
    chunk_vecs = sbert_model.encode(chunks, convert_to_tensor=True)
    sbert_scores = util.cos_sim(topic_vec, chunk_vecs)[0].cpu().numpy()

    scored = [
        (float(sbert_scores[i]) * 0.6 + float(bm25_scores[i]) * 0.4, chunks[i])
        for i in range(len(chunks))
    ]
    scored.sort(reverse=True, key=lambda x: x[0])

    selected_sentences: List[str] = []
    budget = 0
    for _, chunk in scored:
        if sent_tokenize is not None:
            try:
                sents = sent_tokenize(chunk)
            except Exception:
                sents = [
                    s.strip()
                    for s in re.split(r"(?<=[.!?])\s+", chunk.strip())
                    if s.strip()
                ]
        else:
            sents = [
                s.strip()
                for s in re.split(r"(?<=[.!?])\s+", chunk.strip())
                if s.strip()
            ]

        for sent in sents:
            tok_count = len(sent.split())
            if budget + tok_count <= max_tokens:
                selected_sentences.append(sent)
                budget += tok_count

    return " ".join(selected_sentences)


# =====================================================
# Chunk Retrieval
# =====================================================

def get_relevant_chunks(
    module: str, topic: str, topic_mapping: Dict, chunks_dict: Dict[int, str]
) -> Optional[str]:
    """Retrieve only the highest-scoring chunks mapped to the requested topic."""
    relevant_chunk_ids = []

    # First, try exact normalized matching (handles Roman <-> Arabic)
    matched_key = find_matching_key(module, topic_mapping.keys())

    if matched_key:
        value = topic_mapping[matched_key]

        # 1. NEW LOGIC: Granular topic-level chunks
        if isinstance(value, dict) and "topic_mappings" in value and topic in value["topic_mappings"]:
            sorted_topic_chunks = sorted(
                value["topic_mappings"][topic],
                key=lambda item: float(item.get("score", 0.0)),
                reverse=True,
            )
            for chunk_info in sorted_topic_chunks[:3]:
                chunk_id = chunk_info.get("chunk_id")
                if chunk_id in chunks_dict and chunk_id not in relevant_chunk_ids:
                    relevant_chunk_ids.append(chunk_id)

        # 2. LEGACY LOGIC: Module-level average chunks (fallback for unstructured JSONs)
        elif isinstance(value, dict) and "chunks" in value:
            for chunk_info in value["chunks"][:3]:
                chunk_id = chunk_info.get("chunk_id")
                if chunk_id in chunks_dict and chunk_id not in relevant_chunk_ids:
                    relevant_chunk_ids.append(chunk_id)

        # 3. LEGACY LOGIC: List of chunks directly
        elif isinstance(value, list):
            for chunk_info in value[:3]:
                chunk_id = (
                    chunk_info
                    if isinstance(chunk_info, int)
                    else chunk_info.get("chunk_id")
                )
                if chunk_id in chunks_dict and chunk_id not in relevant_chunk_ids:
                    relevant_chunk_ids.append(chunk_id)
    else:
        logger.warning(
            f"No matching module found for '{module}' in topic_mapping keys: "
            f"{list(topic_mapping.keys())}"
        )

    if not relevant_chunk_ids:
        return None

    # Preserve the score-ranked insertion order from the selection logic above.
    parts = [chunks_dict[cid] for cid in relevant_chunk_ids if cid in chunks_dict]

    context = " ".join(parts)
    logger.debug(
        f"[Context Window] topic '{topic}': "
        f"stitched {len(parts)} mapped chunks ({len(context)} chars)"
    )
    return context
