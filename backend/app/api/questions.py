"""
Questions API Router — endpoints for exam pattern configuration and question generation.
"""

import json
import logging

from fastapi import APIRouter

from app.models.schemas import ExamPattern, RegenerateRequest
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

        # 1. Collect all question texts for batch processing
        all_q_texts = []
        for part_name, part_questions in generated.items():
            for q in part_questions:
                all_q_texts.append(q.get("text", ""))
                if "or_question" in q:
                    all_q_texts.append(q["or_question"].get("text", ""))
                    if "sub_questions" in q["or_question"] and q["or_question"]["sub_questions"]:
                        for sq in q["or_question"]["sub_questions"]:
                            all_q_texts.append(sq.get("text", ""))
                if "sub_questions" in q and q["sub_questions"]:
                    for sq in q["sub_questions"]:
                        all_q_texts.append(sq.get("text", ""))

        # 2. Batch classify
        all_levels = bloom_service.classify_batch(all_q_texts)

        # 3. Assign back
        level_idx = 0
        for part_name, part_questions in generated.items():
            for q in part_questions:
                q["classified_bloom_level"] = all_levels[level_idx]
                level_idx += 1
                if "or_question" in q:
                    q["or_question"]["classified_bloom_level"] = all_levels[level_idx]
                    level_idx += 1
                    if "sub_questions" in q["or_question"] and q["or_question"]["sub_questions"]:
                        for sq in q["or_question"]["sub_questions"]:
                            sq["classified_bloom_level"] = all_levels[level_idx]
                            level_idx += 1
                if "sub_questions" in q and q["sub_questions"]:
                    for sq in q["sub_questions"]:
                        sq["classified_bloom_level"] = all_levels[level_idx]
                        level_idx += 1

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


@router.post("/regenerate-question")
async def regenerate_question(req: RegenerateRequest):
    """
    Regenerate a single question for a given module and mark allocation.

    Reuses the existing T5/template pipeline via _generate_single_question,
    then classifies the result with the Bloom's classifier.
    """
    import os
    from types import SimpleNamespace

    try:
        processed = str(PROCESSED_DATA_DIR)

        # Load required data files
        topic_mapping = question_service._load_json(
            os.path.join(processed, "topic_chunk_mapping.json")
        ) or {}

        if question_service._chunks_cache is None:
            question_service._chunks_cache = question_service._load_json(
                os.path.join(processed, "textbook_chunks.json")
            ) or []
            question_service._chunks_dict_cache = {
                chunk["chunk_id"]: chunk["text"]
                for chunk in question_service._chunks_cache
            }

        chunks_dict = question_service._chunks_dict_cache or {}

        syllabus_topics = question_service._load_json(
            os.path.join(processed, "selected_topics.json")
        )
        if not syllabus_topics:
            syllabus_topics = question_service._load_json(
                os.path.join(processed, "syllabus_topics.json")
            ) or {}

        question_service._load_model()

        # Build lightweight objects matching the interface _generate_single_question expects
        mock_question = SimpleNamespace(
            question_no=req.question_no,
            marks=req.marks,
            module=req.module,
            has_internal_choice=False,
            or_choice=None,
            sub_questions=req.sub_questions,
        )
        mock_part = SimpleNamespace(
            part_name="",
            answer_type="ALL",
        )

        generated_q = question_service._generate_single_question(
            question=mock_question,
            part=mock_part,
            topic_mapping=topic_mapping,
            chunks_dict=chunks_dict,
            syllabus_topics=syllabus_topics,
            seen_topics={},
        )

        # Classify with Bloom's
        # Classify with Bloom's
        q_texts = []
        if generated_q.get("text"):
            q_texts.append(generated_q["text"])
            
        sq_count = len(generated_q.get("sub_questions", []))
        if sq_count > 0:
            for sq in generated_q["sub_questions"]:
                q_texts.append(sq.get("text", ""))

        if q_texts:
            levels = bloom_service.classify_batch(q_texts)
            
            level_idx = 0
            if generated_q.get("text"):
                generated_q["classified_bloom_level"] = levels[level_idx]
                level_idx += 1
                
            if sq_count > 0:
                for sq in generated_q["sub_questions"]:
                    sq["classified_bloom_level"] = levels[level_idx]
                    level_idx += 1

        return {"question": generated_q}

    except Exception as e:
        logger.error(f"Question regeneration failed: {e}")
        return {
            "error": str(e),
            "message": "Question regeneration failed.",
        }
