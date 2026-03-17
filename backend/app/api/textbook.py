"""
Textbook API Router — endpoint for textbook PDF upload, chunking, and image extraction.
"""

import json
import re
import shutil
import logging
from typing import Optional, Set

from fastapi import APIRouter, UploadFile, File, Form

from app.services.ingestion_service import extract_pages
from app.services.chunking_service import chunk_text_by_page
from app.utils.image_utils import extract_images_from_pdf, map_chunks_to_images
from app.core.config import PROCESSED_DATA_DIR
from app.services.question_service import question_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["textbook"])


def parse_page_range(page_range: str) -> Set[int]:
    """
    Parse an iLovePDF-style page range string into a set of page numbers.

    Supports formats like: "1-5, 8, 10-20"

    Args:
        page_range: Comma-separated ranges (e.g., "1-5, 8, 10-20").

    Returns:
        Set of page numbers.
    """
    pages = set()
    parts = page_range.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        range_match = re.match(r"(\d+)\s*-\s*(\d+)", part)
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            pages.update(range(start, end + 1))
        elif part.isdigit():
            pages.add(int(part))
    return pages


@router.post("/chunk-textbook")
async def chunk_textbook(
    file: UploadFile = File(...),
    page_range: Optional[str] = Form(None),
):
    """
    Upload a textbook PDF, extract text, chunk it, extract images,
    and map images to chunks by page number.

    Optionally accepts a page_range parameter (e.g., "1-5, 8, 10-20")
    to process only specific pages.

    Returns the total number of chunks and images created.
    """
    # Clear old images
    image_dir = PROCESSED_DATA_DIR / "images"
    if image_dir.exists():
        shutil.rmtree(image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)

    # Read PDF bytes once
    pdf_bytes = await file.read()

    # Text extraction with page metadata
    pages_text = extract_pages(pdf_bytes)
    total_pdf_pages = len(pages_text)

    # Filter pages if a range is specified
    if page_range and page_range.strip():
        requested_pages = parse_page_range(page_range)
        if requested_pages:
            pages_text = [
                (page_num, text) for page_num, text in pages_text
                if page_num in requested_pages
            ]
            logger.info(
                f"Page range filter applied: {len(pages_text)} of {total_pdf_pages} pages selected"
            )

    # Chunking with page metadata
    chunks = chunk_text_by_page(pages_text)

    # Image extraction
    images = extract_images_from_pdf(pdf_bytes, str(image_dir))

    # Filter images to only include pages in range
    if page_range and page_range.strip():
        requested_pages = parse_page_range(page_range)
        if requested_pages:
            images = [img for img in images if img.get("page") in requested_pages]

    # Map chunks ↔ images using page number
    final_chunks = map_chunks_to_images(chunks, images)

    # Save output
    output_path = PROCESSED_DATA_DIR / "textbook_chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, indent=4)

    # Clear stale caches so next generation reads fresh data
    question_service.clear_caches()

    return {
        "message": "Textbook processed successfully",
        "total_chunks": len(final_chunks),
        "total_images": len(images),
        "total_pdf_pages": total_pdf_pages,
        "pages_processed": len(pages_text),
    }
