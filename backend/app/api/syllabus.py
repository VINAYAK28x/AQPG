"""
Syllabus API Router — endpoint for syllabus PDF upload and topic extraction.
"""

import json
import logging

from fastapi import APIRouter, UploadFile, File

from app.services.syllabus_service import extract_syllabus_text, extract_module_topics
from app.core.config import PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)
router = APIRouter(tags=["syllabus"])


@router.post("/extract-syllabus")
async def extract_syllabus(file: UploadFile = File(...)):
    """
    Upload a syllabus PDF and extract module-wise topics.

    Returns the extracted modules with their topic lists,
    and saves the result to processed_data/syllabus_topics.json.
    """
    pdf_bytes = await file.read()

    text = extract_syllabus_text(pdf_bytes)
    modules = extract_module_topics(text)

    # Persist for downstream pipeline steps
    syllabus_path = PROCESSED_DATA_DIR / "syllabus_topics.json"
    with open(syllabus_path, "w", encoding="utf-8") as f:
        json.dump(modules, f, indent=4)

    return {
        "message": "Syllabus topics extracted successfully",
        "modules": modules,
    }
