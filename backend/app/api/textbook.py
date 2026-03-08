"""
Textbook API Router — endpoint for textbook PDF upload, chunking, and image extraction.
"""

import json
import shutil
import logging

from fastapi import APIRouter, UploadFile, File

from app.services.ingestion_service import extract_pages
from app.services.chunking_service import chunk_text_by_page
from app.utils.image_utils import extract_images_from_pdf, map_chunks_to_images
from app.core.config import PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)
router = APIRouter(tags=["textbook"])


@router.post("/chunk-textbook")
async def chunk_textbook(file: UploadFile = File(...)):
    """
    Upload a textbook PDF, extract text, chunk it, extract images,
    and map images to chunks by page number.

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

    # Chunking with page metadata
    chunks = chunk_text_by_page(pages_text)

    # Image extraction
    images = extract_images_from_pdf(pdf_bytes, str(image_dir))

    # Map chunks ↔ images using page number
    final_chunks = map_chunks_to_images(chunks, images)

    # Save output
    output_path = PROCESSED_DATA_DIR / "textbook_chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, indent=4)

    return {
        "message": "Textbook processed successfully",
        "total_chunks": len(final_chunks),
        "total_images": len(images),
    }
