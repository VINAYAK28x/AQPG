"""
Chunking Service — split extracted textbook text into chunks.

Responsibilities:
- Split page-level text into fixed-size word chunks
- Preserve page number metadata on each chunk
"""

import logging
from typing import List, Dict, Any, Tuple

from app.core.config import CHUNK_SIZE_WORDS, MIN_CHUNK_LENGTH

logger = logging.getLogger(__name__)


def chunk_text_by_page(
    pages_text: List[Tuple[int, str]],
    chunk_size: int = CHUNK_SIZE_WORDS,
    min_length: int = MIN_CHUNK_LENGTH,
) -> List[Dict[str, Any]]:
    """
    Split page-level text into word-based chunks with page metadata.

    Args:
        pages_text: List of (page_number, page_text) tuples.
        chunk_size: Number of words per chunk.
        min_length: Minimum character length for a chunk to be kept.

    Returns:
        List of chunk dicts with keys: chunk_id, page, text.
    """
    chunks = []
    chunk_id = 1

    for page_number, text in pages_text:
        words = text.split()

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i : i + chunk_size])

            if len(chunk.strip()) > min_length:
                chunks.append({
                    "chunk_id": chunk_id,
                    "page": page_number,
                    "text": chunk,
                })
                chunk_id += 1

    logger.info(f"Created {len(chunks)} chunks from {len(pages_text)} pages")
    return chunks
