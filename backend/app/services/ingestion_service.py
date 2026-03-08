"""
Ingestion Service — PDF text extraction with OCR fallback.

Responsibilities:
- Extract text from uploaded PDFs using PyMuPDF
- Fall back to OCR (Tesseract) for scanned/image-based PDFs
- Validate extracted text quality
"""

import logging
from typing import List, Tuple

from app.utils.pdf_utils import extract_full_text, extract_text_by_page, is_valid_extracted_text
from app.core.config import TESSERACT_CMD, POPPLER_PATH

logger = logging.getLogger(__name__)


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
        return text

    # Fallback to OCR for scanned PDFs
    logger.info("PyMuPDF text insufficient — falling back to OCR")
    return _ocr_extract(pdf_bytes)


def extract_pages(pdf_bytes: bytes) -> List[Tuple[int, str]]:
    """
    Extract text page-by-page with page number metadata.

    Args:
        pdf_bytes: Raw bytes of the uploaded PDF.

    Returns:
        List of (page_number, page_text) tuples.
    """
    return extract_text_by_page(pdf_bytes)


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
