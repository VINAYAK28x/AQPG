"""
Questions API Router — endpoints for exam pattern configuration and question generation.
"""

import json
import logging

from fastapi import APIRouter

from app.models.schemas import ExamPattern
from app.services.question_service import question_service
from app.services.bloom_service import bloom_service
from app.core.config import PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)
router = APIRouter(tags=["questions"])


@router.post("/set-question-pattern")
async def set_question_pattern(pattern: ExamPattern):
    """
    Save the exam question pattern configuration.

    Converts the pattern into a flat generation plan and persists it.
    """
    generation_plan = []

    for part in pattern.parts:
        if part.questions:
            for question in part.questions:
                generation_plan.append({
                    "question_no": question.question_no,
                    "part": part.part_name,
                    "marks": question.marks,
                    "module": question.module,
                    "bloom_level": question.bloom_level,
                    "answer_type": part.answer_type,
                    "has_internal_choice": question.has_internal_choice,
                })

    pattern_path = PROCESSED_DATA_DIR / "question_pattern.json"
    with open(pattern_path, "w", encoding="utf-8") as f:
        json.dump(generation_plan, f, indent=4)

    return {
        "message": "Question pattern saved successfully",
        "generation_plan": generation_plan,
    }


@router.post("/generate-questions")
async def generate_questions(pattern: ExamPattern):
    """
    Generate exam questions based on the given pattern.

    Uses the Flan-T5 model for question generation and the Bloom's
    classifier to verify/classify the cognitive level of each question.
    """
    try:
        generated = question_service.generate_questions_from_pattern(
            pattern, str(PROCESSED_DATA_DIR)
        )

        # Enrich each question with Bloom's classification
        for part_name, questions in generated.items():
            for q in questions:
                classified_level = bloom_service.classify(q.get("text", ""))
                q["classified_bloom_level"] = classified_level

        # Persist output
        questions_path = PROCESSED_DATA_DIR / "generated_questions.json"
        with open(questions_path, "w", encoding="utf-8") as f:
            json.dump(generated, f, indent=4)

        return {
            "message": "Questions generated successfully",
            "questions": generated,
        }

    except Exception as e:
        logger.error(f"Question generation failed: {e}")
        return {
            "error": str(e),
            "message": "Question generation failed. Please ensure syllabus and textbook have been uploaded.",
        }
