"""
Ingestion Service — PDF text extraction with OCR fallback.

Responsibilities:
- Extract text from uploaded PDFs using PyMuPDF
- Fall back to OCR (Tesseract) for scanned/image-based PDFs
- Validate extracted text quality
- Clean noise from extracted text (TOC, page numbers, preface, etc.)
"""

import re
import logging
from typing import List, Tuple
from collections import Counter

from app.utils.pdf_utils import extract_full_text, extract_text_by_page, is_valid_extracted_text
from app.core.config import TESSERACT_CMD, POPPLER_PATH

logger = logging.getLogger(__name__)

# =====================================================
# Section headers that signal end-of-content
# =====================================================
_STOP_HEADERS = re.compile(
    r"^\s*(references|bibliography|index|appendix\s+[a-z]?\s*$)",
    re.IGNORECASE,
)

# =====================================================
# Noise patterns
# =====================================================
_TOC_DOTS = re.compile(r"^.*\.{5,}.*$")            # Lines with ".........."
_STANDALONE_NUMBER = re.compile(r"^\s*\d{1,4}\s*$") # Isolated page numbers
_SECTION_PREFIXES = re.compile(
    r"^\s*(preface|foreword|acknowledgements?|table\s+of\s+contents|about\s+the\s+author)",
    re.IGNORECASE,
)


def clean_extracted_text(text: str) -> str:
    """
    Remove noise from extracted PDF text.

    Rules applied (from aqpg_final_upgrade_plan.md):
    - Drop TOC lines (lines with ".....")
    - Drop standalone page numbers
    - Drop lines < 5 words
    - Stop parsing at "References" / "Index" / "Bibliography"
    - Remove repeated header lines (appearing > 3 times)
    - Merge broken lines (line doesn't end with punctuation + next starts lowercase)
    """
    lines = text.split("\n")

    # ---- Pass 1: detect repeated headers ----
    stripped_counts = Counter(line.strip() for line in lines if line.strip())
    repeated_headers = {
        line for line, count in stripped_counts.items()
        if count > 3 and len(line.split()) < 10
    }

    # ---- Pass 2: filter lines ----
    cleaned_lines: List[str] = []
    for line in lines:
        stripped = line.strip()

        # Stop at reference/index sections
        if _STOP_HEADERS.match(stripped):
            logger.info(f"[Noise Removal] Stopped at section header: '{stripped}'")
            break

        # Skip TOC dot-leader lines
        if _TOC_DOTS.match(stripped):
            continue

        # Skip standalone page numbers
        if _STANDALONE_NUMBER.match(stripped):
            continue

        # Skip section prefixes (preface, TOC header, acknowledgements)
        if _SECTION_PREFIXES.match(stripped):
            continue

        # Skip repeated headers
        if stripped in repeated_headers:
            continue

        # Skip lines with fewer than 5 words
        if len(stripped.split()) < 5:
            continue

        cleaned_lines.append(stripped)

    # ---- Pass 3: merge broken lines ----
    merged: List[str] = []
    for line in cleaned_lines:
        if (
            merged
            and merged[-1]
            and merged[-1][-1] not in ".?!:;\""
            and line
            and line[0].islower()
        ):
            # Join with previous line
            merged[-1] = merged[-1] + " " + line
        else:
            merged.append(line)

    result = "\n".join(merged)
    logger.info(
        f"[Noise Removal] {len(lines)} raw lines → {len(merged)} cleaned lines"
    )
    return result


def extract_text(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF, falling back to OCR if the PyMuPDF
    extraction yields low-quality or insufficient text.

    Args:
        pdf_bytes: Raw bytes of the uploaded PDF.

    Returns:
        Extracted text content.
    """
    # Try PyMuPDF first (fast, works on text-based PDFs)
    text = extract_full_text(pdf_bytes)

    if is_valid_extracted_text(text):
        logger.info("Text extracted successfully via PyMuPDF")
        return clean_extracted_text(text)

    # Fallback to OCR for scanned PDFs
    logger.info("PyMuPDF text insufficient — falling back to OCR")
    return clean_extracted_text(_ocr_extract(pdf_bytes))


def extract_pages(pdf_bytes: bytes) -> List[Tuple[int, str]]:
    """
    Extract text page-by-page with page number metadata.

    Args:
        pdf_bytes: Raw bytes of the uploaded PDF.

    Returns:
        List of (page_number, page_text) tuples.
    """
    raw_pages = extract_text_by_page(pdf_bytes)
    # Clean each page individually
    cleaned_pages = []
    for page_num, page_text in raw_pages:
        cleaned = clean_extracted_text(page_text)
        if cleaned.strip():
            cleaned_pages.append((page_num, cleaned))
    return cleaned_pages


def _ocr_extract(pdf_bytes: bytes) -> str:
    """
    Perform OCR on a PDF using Tesseract + pdf2image.
    Only called when PyMuPDF extraction fails quality checks.
    """
    try:
        import pytesseract
        from pdf2image import convert_from_bytes

        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

        convert_kwargs = {"dpi": 200}
        if POPPLER_PATH:
            convert_kwargs["poppler_path"] = POPPLER_PATH

        images = convert_from_bytes(pdf_bytes, **convert_kwargs)

        ocr_text = ""
        for i, img in enumerate(images):
            logger.debug(f"OCR processing page {i + 1}/{len(images)}")
            ocr_text += pytesseract.image_to_string(img, lang="eng") + "\n"

        return ocr_text

    except ImportError:
        logger.warning(
            "pytesseract or pdf2image not installed. "
            "OCR fallback unavailable — returning raw PyMuPDF text."
        )
        return extract_full_text(pdf_bytes)
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return extract_full_text(pdf_bytes)


def extract_syllabus_raw(pdf_bytes: bytes) -> str:
    """
    Extract text from a syllabus PDF WITHOUT noise removal.

    The syllabus service has its own filtering (course outcomes, ignore keywords)
    in extract_module_topics(). Applying the textbook noise cleaner here would
    destroy short topic lines like 'Iris Scan', 'Palm Print', etc.

    Args:
        pdf_bytes: Raw bytes of the syllabus PDF.

    Returns:
        Raw extracted text content.
    """
    text = extract_full_text(pdf_bytes)

    if is_valid_extracted_text(text):
        logger.info("Syllabus text extracted successfully via PyMuPDF (raw)")
        return text

    logger.info("PyMuPDF text insufficient for syllabus — falling back to OCR")
    return _ocr_extract(pdf_bytes)
