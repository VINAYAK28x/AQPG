"""
Mapping API Router — endpoint for semantic topic-to-chunk mapping.
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
    Perform semantic mapping between syllabus topics and textbook chunks
    using the SBERT model.

    Requires that syllabus and textbook have been processed first.
    """
    syllabus_path = PROCESSED_DATA_DIR / "syllabus_topics.json"
    chunks_path = PROCESSED_DATA_DIR / "textbook_chunks.json"

    if not syllabus_path.exists():
        return {"error": "Syllabus not processed yet. Upload a syllabus first."}

    if not chunks_path.exists():
        return {"error": "Textbook not processed yet. Upload a textbook first."}

    # Load syllabus topics
    with open(syllabus_path, "r", encoding="utf-8") as f:
        modules = json.load(f)

    topics = []
    for topic_list in modules.values():
        topics.extend(topic_list)

    if not topics:
        return {"error": "No topics were extracted from the syllabus. Please check the uploaded syllabus PDF."}

    # Load textbook chunks
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not chunks:
        return {"error": "No text chunks were generated from the textbook. Please check the uploaded textbook PDF."}

    # Perform mapping using SBERT
    mapping = mapping_service.map_topics_to_chunks(topics, chunks)

    if not mapping:
        return {"error": "Semantic mapping failed to associate any topics with chunks. Please ensure the syllabus and textbook content are related."}

    # Persist mapping
    mapping_path = PROCESSED_DATA_DIR / "topic_chunk_mapping.json"
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=4)

    return {
        "message": "Semantic mapping completed successfully",
        "mapping": mapping,
    }
