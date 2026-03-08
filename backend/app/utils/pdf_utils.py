"""
Utility functions for PDF reading and text extraction.
Shared by ingestion and syllabus services.
"""

import fitz  # PyMuPDF
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def extract_full_text(pdf_bytes: bytes) -> str:
    """
    Extract all text from a PDF using PyMuPDF.

    Args:
        pdf_bytes: Raw bytes of the PDF file.

    Returns:
        Concatenated text from all pages.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text


def extract_text_by_page(pdf_bytes: bytes) -> List[Tuple[int, str]]:
    """
    Extract text from a PDF page-by-page with page number metadata.

    Args:
        pdf_bytes: Raw bytes of the PDF file.

    Returns:
        List of (page_number, page_text) tuples.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text = []
    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")
        pages_text.append((page_number, text))
    return pages_text


def is_valid_extracted_text(text: str) -> bool:
    """
    Detect and reject fake/hidden text layers commonly found in scanned textbooks.

    Args:
        text: Extracted text to validate.

    Returns:
        True if the text appears to be genuine content.
    """
    if not text or len(text.strip()) < 300:
        return False

    lower_text = text.lower()

    garbage_patterns = [
        "hidden page",
        "this page intentionally left blank",
        "digitized by",
        "scanned by",
        "copyright",
    ]

    for pattern in garbage_patterns:
        if lower_text.count(pattern) > 3:
            return False

    words = text.split()
    unique_words = set(words)
    diversity_ratio = len(unique_words) / max(len(words), 1)

    if diversity_ratio < 0.25:
        return False

    return True
