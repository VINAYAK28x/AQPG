"""
Syllabus API Router — endpoint for syllabus PDF upload and topic extraction.
"""

import json
import logging

from fastapi import APIRouter, UploadFile, File

from app.services.syllabus_service import (
    extract_syllabus_text,
    extract_module_topics,
    build_structured_syllabus,
)
from app.core.config import PROCESSED_DATA_DIR
from app.services.question_service import question_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["syllabus"])


@router.post("/extract-syllabus")
async def extract_syllabus(file: UploadFile = File(...)):
    """
    Upload a syllabus PDF and extract module-wise topics.

    Returns the structured syllabus with course title, course code,
    and modules containing topics, raw text, and embedding-ready text.
    Saves the result to processed_data/syllabus_topics.json.
    """
    pdf_bytes = await file.read()

    text = extract_syllabus_text(pdf_bytes)
    modules = extract_module_topics(text)

    # Build the enriched structured output
    structured = build_structured_syllabus(text, modules)

    # Persist for downstream pipeline steps
    syllabus_path = PROCESSED_DATA_DIR / "syllabus_topics.json"
    with open(syllabus_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=4)

    # Clear stale caches so next generation reads fresh data
    question_service.clear_caches()

    return {
        "message": "Syllabus topics extracted successfully",
        **structured,
    }
