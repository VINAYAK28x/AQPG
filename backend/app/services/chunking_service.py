"""
Chunking Service — split extracted textbook text into semantic chunks.

Responsibilities:
- Split page-level text into character-based chunks using LangChain's
  RecursiveCharacterTextSplitter (respects sentence boundaries)
- Filter out low-quality chunks via technical density and sentence count
- Preserve page number metadata on each chunk
"""

import re
import logging
from typing import List, Dict, Any, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS, MIN_CHUNK_LENGTH

logger = logging.getLogger(__name__)


# =====================================================
# Quality Filters (Step 5 from upgrade plan)
# =====================================================

def technical_density(text: str) -> float:
    """
    Measure the ratio of 'technical' words in a text.

    A word is considered technical if it:
    - Contains digits (e.g., SHA-256, AES-128)
    - Contains uppercase letters (e.g., RSA, DES)
    - Is longer than 6 characters (e.g., cryptography, authentication)

    Returns:
        Float between 0.0 and 1.0.
    """
    words = text.split()
    if not words:
        return 0.0
    technical_words = [
        w for w in words
        if (
            any(c.isdigit() for c in w)
            or any(c.isupper() for c in w)
            or len(w) > 6
        )
    ]
    return len(technical_words) / len(words)


def sentence_count(text: str) -> int:
    """Count the number of sentences in a text block."""
    # Split on sentence-ending punctuation followed by whitespace or end-of-string
    sentences = re.split(r'[.!?]+(?:\s|$)', text.strip())
    # Filter out empty strings from the split
    return len([s for s in sentences if s.strip()])


def _is_quality_chunk(text: str) -> bool:
    """
    Reject a chunk if:
    - sentence_count < 2
    - technical_density < 0.1
    """
    sc = sentence_count(text)
    td = technical_density(text)
    if sc < 2:
        return False
    if td < 0.1:
        return False
    return True


# =====================================================
# Main Chunking Function
# =====================================================

def chunk_text_by_page(
    pages_text: List[Tuple[int, str]],
    chunk_size: int = CHUNK_SIZE_CHARS,
    chunk_overlap: int = CHUNK_OVERLAP_CHARS,
    min_length: int = MIN_CHUNK_LENGTH,
) -> List[Dict[str, Any]]:
    """
    Split page-level text into character-based chunks using LangChain's
    RecursiveCharacterTextSplitter, with quality filtering.

    Args:
        pages_text: List of (page_number, page_text) tuples.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between consecutive chunks in characters.
        min_length: Minimum character length for a chunk to be kept.

    Returns:
        List of chunk dicts with keys: chunk_id, page, text.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks: List[Dict[str, Any]] = []
    chunk_id = 1
    rejected = 0

    for page_number, text in pages_text:
        if not text or not text.strip():
            continue

        # Split the page text into character-based chunks
        page_chunks = splitter.split_text(text)

        for chunk_text in page_chunks:
            chunk_text = chunk_text.strip()

            # Reject chunks that are too short
            if len(chunk_text) < min_length:
                rejected += 1
                continue

            # Reject chunks that fail quality filters
            if not _is_quality_chunk(chunk_text):
                rejected += 1
                continue

            chunks.append({
                "chunk_id": chunk_id,
                "page": page_number,
                "text": chunk_text,
            })
            chunk_id += 1

    logger.info(
        f"Created {len(chunks)} chunks from {len(pages_text)} pages "
        f"(rejected {rejected} low-quality chunks)"
    )
    return chunks
