"""
Mapping API Router — endpoint for semantic module-to-chunk mapping.
"""

import json
import logging

from typing import Optional, Dict, List
from pydantic import BaseModel
from fastapi import APIRouter

from app.services.mapping_service import mapping_service
from app.core.config import PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)
router = APIRouter(tags=["mapping"])

class MappingRequest(BaseModel):
    # selected_modules maps module names to a list of selected topic strings
    selected_modules: Optional[Dict[str, List[str]]] = None

@router.post("/semantic-mapping")
async def semantic_mapping(request: MappingRequest = None):
    """
    Perform semantic mapping between syllabus modules and textbook chunks
    using the SBERT model.

    If selected_modules is provided in the request payload, only those 
    topics will be mapped and saved.
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

    # Filter syllabus if the user passed specifically selected topics
    if request and request.selected_modules:
        filtered_modules = {}
        for mod_name, mod_data in modules.items():
            if mod_name in request.selected_modules:
                # Keep only selected topics
                selected = request.selected_modules[mod_name]
                if selected:
                    filtered_modules[mod_name] = {
                        "topics": [t for t in mod_data.get("topics", []) if t in selected]
                    }
        structured_syllabus["modules"] = filtered_modules

    # Save the selected/filtered topics to a new file so the question generator knows what to use
    selected_topics_path = PROCESSED_DATA_DIR / "selected_topics.json"
    with open(selected_topics_path, "w", encoding="utf-8") as f:
        json.dump(structured_syllabus, f, indent=4)

    # Load textbook chunks
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not chunks:
        return {"error": "No text chunks were generated from the textbook. Please check the uploaded textbook PDF."}

    # Perform module-level mapping using SBERT with the filtered syllabus
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
