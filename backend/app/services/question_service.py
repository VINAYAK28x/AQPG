"""
Question Generation Service — generate exam questions using Flan-T5.

Responsibilities:
- Load the fine-tuned Flan-T5 model (or fallback to templates)
- Generate questions based on exam pattern, topic mappings, and textbook content
- Support different Bloom's taxonomy levels in question prompts
"""

import os
import re
import json
import random
import logging
from typing import List, Dict, Any, Optional

from app.core.config import (
    FLAN_T5_MODEL_PATH,
    FLAN_T5_FALLBACK_MODEL,
    PROCESSED_DATA_DIR,
)

logger = logging.getLogger(__name__)


class QuestionService:
    """
    Generates exam questions using a fine-tuned Flan-T5 model.
    Falls back to template-based generation if the model cannot be loaded.
    """

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._model_loaded = False
        self._load_attempted = False

    def _load_model(self):
        """Attempt to load the Flan-T5 model. Only tries once."""
        if self._load_attempted:
            return
        self._load_attempted = True

        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

            model_path = FLAN_T5_MODEL_PATH
            if not os.path.exists(model_path):
                logger.warning(
                    f"Fine-tuned T5 model not found at {model_path}. "
                    f"Falling back to {FLAN_T5_FALLBACK_MODEL}"
                )
                model_path = FLAN_T5_FALLBACK_MODEL

            logger.info(f"Loading T5 model from {model_path}...")
            self._tokenizer = AutoTokenizer.from_pretrained(model_path)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            self._model_loaded = True
            logger.info("T5 model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load T5 model: {e}. Using template fallback.")
            self._model_loaded = False

    def generate_questions_from_pattern(
        self, exam_pattern, processed_data_dir: str = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate questions for each part of the exam pattern.

        Works with whatever data is available:
        - Best: syllabus + chunks + mapping (full context for T5)
        - OK:   syllabus only (template-based generation)
        - Min:  no data at all (generates generic questions from module names)
        """
        if processed_data_dir is None:
            processed_data_dir = str(PROCESSED_DATA_DIR)

        # Load data files — all optional, service degrades gracefully
        topic_mapping = self._load_json(
            os.path.join(processed_data_dir, "topic_chunk_mapping.json")
        ) or {}
        textbook_chunks = self._load_json(
            os.path.join(processed_data_dir, "textbook_chunks.json")
        ) or []
        syllabus_topics = self._load_json(
            os.path.join(processed_data_dir, "syllabus_topics.json")
        ) or {}

        if not syllabus_topics:
            logger.warning("No syllabus data found — generating from module names only")
        if not topic_mapping:
            logger.warning("No topic-chunk mapping found — generating without textbook context")

        # Ensure model is loaded
        self._load_model()

        generated_questions: Dict[str, List[Dict[str, Any]]] = {}

        for part in exam_pattern.parts:
            part_questions = []

            if part.questions:
                for question in part.questions:
                    generated_q = self._generate_single_question(
                        question=question,
                        part=part,
                        topic_mapping=topic_mapping,
                        textbook_chunks=textbook_chunks,
                        syllabus_topics=syllabus_topics,
                    )
                    part_questions.append(generated_q)

            generated_questions[part.part_name] = part_questions

        return generated_questions

    def _generate_single_question(
        self, question, part, topic_mapping, textbook_chunks, syllabus_topics
    ) -> Dict[str, Any]:
        """Generate a single question using T5 or template fallback."""

        # Get relevant context
        chunk_text = self._get_relevant_chunks(
            module=question.module,
            topic_mapping=topic_mapping,
            textbook_chunks=textbook_chunks,
        )

        topic = self._get_random_topic(question.module, syllabus_topics)
        bloom_level = question.bloom_level or "Remember"

        # Try T5 generation first
        if self._model_loaded:
            question_text = self._generate_with_t5(
                topic=topic,
                context=chunk_text,
                bloom_level=bloom_level,
                marks=question.marks,
            )
        else:
            question_text = self._generate_with_template(
                topic=topic,
                bloom_level=bloom_level,
                context=chunk_text,
            )

        return {
            "question_no": question.question_no,
            "marks": question.marks,
            "module": question.module,
            "bloom_level": bloom_level,
            "text": question_text,
            "has_internal_choice": question.has_internal_choice,
            "source_chunk": chunk_text[:80] if chunk_text else None,
        }

    def _generate_with_t5(
        self, topic: str, context: Optional[str], bloom_level: str, marks: int
    ) -> str:
        """Generate a question using the Flan-T5 model."""
        context_snippet = context[:1200] if context else "No context provided."

        # Define few-shot examples and explicit structural guidelines based on marks
        if marks <= 2:
            structure_guide = "Must be a single, direct sentence asking for a definition, concept, or brief explanation."
            example = (
                "Example Format:\n"
                "Topic: Database Normalization\n"
                "Marks: 2\n"
                "Output: Define First Normal Form (1NF) in the context of relational databases."
            )
        elif marks <= 6:
            structure_guide = "Must be a multi-sentence question that asks the student to explain, compare, or apply a concept to a scenario."
            example = (
                "Example Format:\n"
                "Topic: Database Normalization\n"
                "Marks: 5\n"
                "Output: Explain the differences between Second Normal Form (2NF) and Third Normal Form (3NF). Provide a brief example to illustrate your comparison."
            )
        else:
            structure_guide = "Must be a complex, multi-part analytical essay question requiring detailed evaluation or architectural discussion."
            example = (
                "Example Format:\n"
                "Topic: Database Normalization\n"
                "Marks: 10\n"
                "Output: Discuss the process of database normalization from 1NF up to BCNF. Evaluate the trade-offs between a highly normalized database and a denormalized database in terms of read and write performance."
            )

        # Build an enterprise-grade prompt using pseudo-XML tags to logically separate instructions from context
        prompt = (
            f"You are an expert university professor setting a strict examination paper.\n"
            f"Your task is to write EXACTLY ONE exam question. Do NOT provide the answer. Do NOT provide explanations.\n\n"
            f"<requirements>\n"
            f"- Topic: {topic}\n"
            f"- Cognitive Level: {bloom_level} (Bloom's Taxonomy)\n"
            f"- Marks Assigned: {marks}\n"
            f"- Required Structure: {structure_guide}\n"
            f"</requirements>\n\n"
            f"<textbook_context>\n"
            f"{context_snippet}\n"
            f"</textbook_context>\n\n"
            f"<instructions>\n"
            f"Write the question directly based ONLY on the requirements and context above. Output NOTHING except the question text.\n"
            f"{example}\n"
            f"</instructions>\n\n"
            f"Output:"
        )

        inputs = self._tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=1536
        )

        # Highly restrictive decoding parameters to force compliance and prevent looping
        outputs = self._model.generate(
            **inputs,
            max_new_tokens=180,
            temperature=0.7,
            do_sample=True,
            top_k=50,
            top_p=0.9,
            repetition_penalty=1.4,
            no_repeat_ngram_size=3,
            early_stopping=True
        )

        generated_text = self._tokenizer.decode(
            outputs[0], skip_special_tokens=True
        )

        # Aggressive cleanup of hallucinated tags or prefixes
        generated_text = re.sub(r"^(Output|Question|Task|Example)[\s]*:[\s]*", "", generated_text, flags=re.IGNORECASE)
        generated_text = generated_text.replace("<requirements>", "").replace("</textbook_context>", "").strip()
        
        # Fallback if generation failed entirely or generated a tiny fragment
        if len(generated_text.split()) < 3:
            return self._generate_with_template(topic, bloom_level, context)

        return generated_text

    def _generate_with_template(
        self, topic: str, bloom_level: str, context: Optional[str]
    ) -> str:
        """Fallback: generate a question using templates."""
        templates = {
            "Remember": [
                "Define {}.",
                "What is {}?",
                "State the meaning of {}.",
                "List the main points of {}.",
            ],
            "Understand": [
                "Explain the concept of {}.",
                "Describe how {} works.",
                "Illustrate with examples: {}.",
                "Summarize the key ideas of {}.",
            ],
            "Apply": [
                "Apply the concept of {} to solve a practical problem.",
                "How would you use {} in a real-world scenario?",
                "Demonstrate the application of {} with an example.",
            ],
            "Analyze": [
                "Analyze the components of {}.",
                "What factors influence {}?",
                "Examine the relationship between {} and related concepts.",
            ],
            "Evaluate": [
                "Evaluate the effectiveness of {}.",
                "Critically assess the merits and drawbacks of {}.",
                "Compare the advantages and disadvantages of {}.",
            ],
            "Create": [
                "Design a solution using the principles of {}.",
                "Propose a new approach to {}.",
                "Develop a strategy for improving {}.",
            ],
        }

        level_templates = templates.get(bloom_level, templates["Remember"])
        question_text = random.choice(level_templates).format(topic)

        if context:
            question_text += f"\n\n[Based on: {context[:100]}...]"

        return question_text

    def _get_relevant_chunks(
        self, module: str, topic_mapping: Dict, textbook_chunks: List[Dict]
    ) -> Optional[str]:
        """Get a relevant textbook chunk for a given module."""
        chunks_dict = {
            chunk["chunk_id"]: chunk["text"] for chunk in textbook_chunks
        }

        relevant_chunks = []
        for topic, chunks in topic_mapping.items():
            if module.lower() in topic.lower() or module.lower() in str(chunks).lower():
                if isinstance(chunks, list):
                    for chunk_info in chunks:
                        chunk_id = chunk_info if isinstance(chunk_info, int) else chunk_info.get("chunk_id")
                        if chunk_id in chunks_dict:
                            relevant_chunks.append(chunks_dict[chunk_id])

        return random.choice(relevant_chunks) if relevant_chunks else None

    def _get_random_topic(
        self, module: str, syllabus_topics: Optional[Dict]
    ) -> str:
        """Get a random topic from the specified module."""
        if not syllabus_topics:
            return module

        module_key = module.lower()

        # Try exact match first
        for key, topics in syllabus_topics.items():
            if module_key in key.lower():
                if isinstance(topics, list) and topics:
                    return random.choice(topics)

        # Fallback: random topic from any module
        all_topics = []
        for topics in syllabus_topics.values():
            if isinstance(topics, list):
                all_topics.extend(topics)

        return random.choice(all_topics) if all_topics else module

    @staticmethod
    def _load_json(filepath: str) -> Optional[Any]:
        """Safely load a JSON file."""
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)


# Module-level singleton
question_service = QuestionService()
