"""
Question Generation Service — generate exam questions using Flan-T5.
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

        if processed_data_dir is None:
            processed_data_dir = str(PROCESSED_DATA_DIR)

        topic_mapping = self._load_json(
            os.path.join(processed_data_dir, "topic_chunk_mapping.json")
        ) or {}

        textbook_chunks = self._load_json(
            os.path.join(processed_data_dir, "textbook_chunks.json")
        ) or []

        syllabus_topics = self._load_json(
            os.path.join(processed_data_dir, "syllabus_topics.json")
        ) or {}

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

        chunk_text = self._get_relevant_chunks(
            module=question.module,
            topic_mapping=topic_mapping,
            textbook_chunks=textbook_chunks,
        )

        topic = self._get_random_topic(question.module, syllabus_topics)

        if self._model_loaded:
            question_text = self._generate_with_t5(
                topic=topic,
                context=chunk_text,
                marks=question.marks,
            )
        else:
            question_text = self._generate_with_template(
                topic=topic,
                context=chunk_text,
            )

        base_q = {
            "question_no": question.question_no,
            "marks": question.marks,
            "module": question.module,
            "text": question_text,
            "has_internal_choice": question.has_internal_choice,
            "source_chunk": chunk_text[:80] if chunk_text else None,
        }

        # If an internal choice is requested, recursively generate the alternative question
        if question.has_internal_choice and question.or_choice:
            or_marks = question.or_choice.get("marks", question.marks)
            or_module = question.or_choice.get("module", question.module)

            or_chunk_text = self._get_relevant_chunks(
                module=or_module,
                topic_mapping=topic_mapping,
                textbook_chunks=textbook_chunks,
            )

            or_topic = self._get_random_topic(or_module, syllabus_topics)

            if self._model_loaded:
                or_question_text = self._generate_with_t5(
                    topic=or_topic, context=or_chunk_text, marks=or_marks
                )
            else:
                or_question_text = self._generate_with_template(
                    topic=or_topic, context=or_chunk_text
                )
            
            base_q["or_question"] = {
                "marks": or_marks,
                "module": or_module,
                "text": or_question_text,
                "source_chunk": or_chunk_text[:80] if or_chunk_text else None,
            }

        return base_q

    # =====================================================
    # Improved T5 Generation Function (complexity control)
    # =====================================================

    def _generate_with_t5(
        self, topic: str, context: Optional[str], marks: int
    ) -> str:
        # Extract larger context
        context_snippet = context[:600] if context else "No context provided."

        # Extreme simplification of prompt to stop the LLM from trying to build instructions
        if marks <= 2:
            prompt = f"Topic: {topic}\nContext: {context_snippet}\nWrite a short, formal university exam question about what this topic is:"
            max_tokens = 80
        elif marks <= 5:
            prompt = f"Topic: {topic}\nContext: {context_snippet}\nWrite a medium-length, formal university exam question asking how this topic works:"
            max_tokens = 160
        else:
            prompt = f"Topic: {topic}\nContext: {context_snippet}\nWrite a long, complex, formal university discussion question exploring this topic for {marks} marks:"
            max_tokens = 250

        inputs = self._tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=768
        )

        outputs = self._model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.8,        # Increased temperature for diversity
            top_k=50,               # Nucleus sampling
            top_p=0.95,
            repetition_penalty=1.2, # Stronger penalty for repeating words
            no_repeat_ngram_size=3, # Ban repeating the same 3 words (fixes the "Illustrate the concept" loop)
            early_stopping=True
        )

        generated_text = self._tokenizer.decode(
            outputs[0], skip_special_tokens=True
        ).strip()

        generated_text = re.sub(
            r"^(Question|Output|Answer|Task)[\s]*:[\s]*",
            "",
            generated_text,
            flags=re.IGNORECASE
        ).strip()

        # Aggressively strip trailing instructional LLM bleed (e.g., "Provide a clear and concise definition...")
        instruction_bleed_patterns = [
            r"Provide a clear.*",
            r"Describe its significance.*",
            r"Ensure your answer.*",
            r"Support your explanation.*",
            r"Highlight the key.*",
        ]
        for pattern in instruction_bleed_patterns:
            generated_text = re.sub(pattern, "", generated_text, flags=re.IGNORECASE).strip()

        # Punctuation fallback to prevent hanging cutoffs
        if generated_text and generated_text[-1] not in ['.', '?', '!']:
            # Strip trailing incomplete word/sentence chunks after the last space to simulate cleanliness
            if ' ' in generated_text:
                generated_text = generated_text.rsplit(' ', 1)[0]
            generated_text += "?"

        if len(generated_text.split()) < 3:
            return self._generate_with_template(topic, context)

        return generated_text

    # =====================================================
    # Template fallback
    # =====================================================

    def _generate_with_template(
        self, topic: str, context: Optional[str]
    ) -> str:

        templates = [
            "Explain the concept of {}.",
            "Describe how {} works.",
            "Illustrate with examples: {}.",
            "Summarize the key ideas of {}.",
            "Analyze the components of {}.",
            "What factors influence {}?",
            "Examine the relationship between {} and related concepts.",
        ]

        question_text = random.choice(templates).format(topic)

        if context:
            question_text += f"\n\n[Based on: {context[:100]}...]"

        return question_text

    @staticmethod
    def _normalize_module_name(name: str) -> str:
        """
        Normalize a module name so that both Arabic and Roman numeral
        variants map to the same canonical form.
        e.g. "Module 1" -> "module_1", "Module I" -> "module_1",
             "Module IV" -> "module_4", "Module 4" -> "module_4"
        """
        roman_to_arabic = {
            "i": "1", "ii": "2", "iii": "3", "iv": "4",
            "v": "5", "vi": "6", "vii": "7", "viii": "8",
        }
        text = name.strip().lower()
        # Try to extract "module <token>" pattern
        m = re.match(r"^module\s+(.+)$", text)
        if m:
            token = m.group(1).strip()
            # If the token is a Roman numeral, convert it
            if token in roman_to_arabic:
                return f"module_{roman_to_arabic[token]}"
            # If it's already an Arabic numeral, use it
            if token.isdigit():
                return f"module_{token}"
            # Otherwise, return a cleaned version
            return f"module_{token}"
        return text.replace(" ", "_")

    def _find_matching_key(self, module: str, keys) -> Optional[str]:
        """Find the dictionary key that matches the given module name exactly
        after normalization. Returns the original key or None."""
        norm = self._normalize_module_name(module)
        for key in keys:
            if self._normalize_module_name(key) == norm:
                return key
        return None

    def _get_relevant_chunks(
        self, module: str, topic_mapping: Dict, textbook_chunks: List[Dict]
    ) -> Optional[str]:

        chunks_dict = {
            chunk["chunk_id"]: chunk["text"] for chunk in textbook_chunks
        }

        relevant_chunks = []

        # First, try exact normalized matching (handles Roman ↔ Arabic)
        matched_key = self._find_matching_key(module, topic_mapping.keys())

        if matched_key:
            value = topic_mapping[matched_key]
            if isinstance(value, dict) and "chunks" in value:
                for chunk_info in value["chunks"]:
                    chunk_id = chunk_info.get("chunk_id")
                    if chunk_id in chunks_dict:
                        relevant_chunks.append(chunks_dict[chunk_id])
            elif isinstance(value, list):
                for chunk_info in value:
                    chunk_id = (
                        chunk_info
                        if isinstance(chunk_info, int)
                        else chunk_info.get("chunk_id")
                    )
                    if chunk_id in chunks_dict:
                        relevant_chunks.append(chunks_dict[chunk_id])
        else:
            logger.warning(
                f"No matching module found for '{module}' in topic_mapping keys: "
                f"{list(topic_mapping.keys())}"
            )

        return random.choice(relevant_chunks) if relevant_chunks else None

    def _get_random_topic(
        self, module: str, syllabus_topics: Optional[Dict]
    ) -> str:
        if not syllabus_topics:
            return module

        # Handle new structured syllabus format
        modules = syllabus_topics
        if "modules" in syllabus_topics:
            modules = syllabus_topics["modules"]

        matched_key = self._find_matching_key(module, modules.keys())

        if matched_key:
            value = modules[matched_key]
            # New format: value is dict with 'topics' key
            if isinstance(value, dict) and "topics" in value:
                topics = value["topics"]
                if topics:
                    return random.choice(topics)
            # Legacy format: value is list of topics
            elif isinstance(value, list) and value:
                return random.choice(value)

        # Fallback to the module name itself. No cross-module contamination.
        return module

    @staticmethod
    def _load_json(filepath: str) -> Optional[Any]:

        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)


question_service = QuestionService()