"""
Utility functions for image extraction from PDFs and
mapping images to text chunks by page number.
"""

import os
import fitz  # PyMuPDF
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def extract_images_from_pdf(
    pdf_bytes: bytes, output_dir: str
) -> List[Dict[str, Any]]:
    """
    Extract all images from a PDF and save them to the output directory.

    Args:
        pdf_bytes: Raw bytes of the PDF file.
        output_dir: Directory to save extracted images.

    Returns:
        List of image metadata dicts with keys: image_id, page, path.
    """
    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images_metadata = []

    for page_index, page in enumerate(doc, start=1):
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                image_name = f"page_{page_index}_img_{img_index + 1}.{image_ext}"
                image_path = os.path.join(output_dir, image_name)

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                images_metadata.append({
                    "image_id": image_name,
                    "page": page_index,
                    "path": image_path,
                })
            except Exception as e:
                logger.warning(
                    f"Failed to extract image {img_index} from page {page_index}: {e}"
                )

    logger.info(f"Extracted {len(images_metadata)} images from PDF")
    return images_metadata


def map_chunks_to_images(
    chunks: List[Dict[str, Any]], images: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Associate images with text chunks based on matching page numbers.

    Args:
        chunks: List of chunk dicts (must have 'page' key).
        images: List of image metadata dicts (must have 'page' key).

    Returns:
        The chunks list with an added 'images' key on each chunk.
    """
    image_map: Dict[int, List[Dict[str, Any]]] = {}
    for img in images:
        image_map.setdefault(img["page"], []).append(img)

    for chunk in chunks:
        chunk["images"] = image_map.get(chunk["page"], [])

    return chunks
