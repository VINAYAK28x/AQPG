"""
Mapping API Router — endpoint for semantic module-to-chunk mapping.
"""

import json
import logging

from fastapi import APIRouter

from app.services.mapping_service import mapping_service
from app.core.config import PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)
router = APIRouter(tags=["mapping"])


@router.post("/semantic-mapping")
async def semantic_mapping():
    """
    Perform semantic mapping between syllabus modules and textbook chunks
    using the SBERT model.

    Uses module-level mapping: each module is mapped to relevant chunks
    as a whole, rather than mapping individual topics separately.

    Requires that syllabus and textbook have been processed first.
    """
    syllabus_path = PROCESSED_DATA_DIR / "syllabus_topics.json"
    chunks_path = PROCESSED_DATA_DIR / "textbook_chunks.json"

    if not syllabus_path.exists():
        return {"error": "Syllabus not processed yet. Upload a syllabus first."}

    if not chunks_path.exists():
        return {"error": "Textbook not processed yet. Upload a textbook first."}

    # Load structured syllabus
    with open(syllabus_path, "r", encoding="utf-8") as f:
        structured_syllabus = json.load(f)

    modules = structured_syllabus.get("modules", {})
    if not modules:
        return {"error": "No modules were extracted from the syllabus. Please check the uploaded syllabus PDF."}

    # Load textbook chunks
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not chunks:
        return {"error": "No text chunks were generated from the textbook. Please check the uploaded textbook PDF."}

    # Perform module-level mapping using SBERT
    module_mapping = mapping_service.map_modules_to_chunks(
        structured_syllabus, chunks
    )

    if not module_mapping:
        return {"error": "Semantic mapping failed to associate any modules with chunks. Please ensure the syllabus and textbook content are related."}

    # Persist mapping
    mapping_path = PROCESSED_DATA_DIR / "topic_chunk_mapping.json"
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(module_mapping, f, indent=4)

    return {
        "message": "Semantic mapping completed successfully",
        "mapping": module_mapping,
    }
