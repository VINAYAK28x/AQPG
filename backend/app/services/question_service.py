"""
Question Generation Service — generate exam questions using Flan-T5.
"""

import os
import re
import json
import random
import logging
import torch
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
        # Cache for textbook data to avoid redundant Disk I/O per request
        self._chunks_cache: Optional[List[Dict[str, Any]]] = None
        self._chunks_dict_cache: Optional[Dict[int, str]] = None
        self._syllabus_cache: Optional[Dict[str, Any]] = None

    def clear_caches(self):
        """Reset all data caches so the next generation reads fresh files."""
        self._chunks_cache = None
        self._chunks_dict_cache = None
        self._syllabus_cache = None

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
            
        # VERY IMPORTANT FIX: Cap PyTorch CPU threads out of the box. 
        # By default PyTorch tries to use 100% of logical cores which causes catastrophic 
        # context switching overhead and artificial 90%+ CPU spikes.
        # Set to 4 to balance throughput vs background responsiveness.
        try:
            torch.set_num_threads(4) 
        except Exception:
            pass

    def generate_questions_from_pattern(
        self, exam_pattern: Any, processed_data_dir: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:

        if processed_data_dir is None:
            processed_data_dir = str(PROCESSED_DATA_DIR)

        topic_mapping = self._load_json(
            os.path.join(processed_data_dir, "topic_chunk_mapping.json")
        ) or {}

        # Use cached textbook chunks if available to slash I/O time
        if self._chunks_cache is None:
            self._chunks_cache = self._load_json(
                os.path.join(processed_data_dir, "textbook_chunks.json")
            ) or []
            self._chunks_dict_cache = {
                chunk["chunk_id"]: chunk["text"] for chunk in self._chunks_cache
            }
        
        textbook_chunks = self._chunks_cache
        chunks_dict = self._chunks_dict_cache

        syllabus_topics = self._load_json(
            os.path.join(processed_data_dir, "syllabus_topics.json")
        ) or {}

        self._load_model()

        generated_questions: Dict[str, List[Dict[str, Any]]] = {}
        # Track seen topics to prevent duplicates
        seen_topics: Dict[str, set] = {}

        for part in exam_pattern.parts:

            part_questions = []

            if part.questions:

                for question in part.questions:

                    generated_q = self._generate_single_question(
                        question=question,
                        part=part,
                        topic_mapping=topic_mapping,
                        chunks_dict=chunks_dict,
                        syllabus_topics=syllabus_topics,
                        seen_topics=seen_topics,
                    )

                    part_questions.append(generated_q)

            generated_questions[part.part_name] = part_questions

        return generated_questions

    def _generate_single_question(
        self, question: Any, part: Any, topic_mapping: Dict, chunks_dict: Dict, syllabus_topics: Dict, seen_topics: Dict
    ) -> Dict[str, Any]:

        topic = self._get_random_topic(question.module, syllabus_topics, seen_topics.get(question.module))
        
        # Mark topic as seen
        if question.module not in seen_topics:
            seen_topics[question.module] = set()
        seen_topics[question.module].add(topic)

        # Ensure chunks_dict is not None for downstream calls
        safe_chunks_dict = chunks_dict if chunks_dict is not None else {}

        chunk_text = self._get_relevant_chunks(
            module=str(question.module),
            topic_mapping=topic_mapping,
            chunks_dict=safe_chunks_dict,
        )

        # Check if we have sub-questions configured
        has_sub_qs = hasattr(question, 'sub_questions') and question.sub_questions

        question_text = ""
        # Only generate a main question text if there are NO sub-questions
        if not has_sub_qs:
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

        source_chunk = None
        if chunk_text:
            source_chunk = chunk_text[:80]

        base_q = {
            "question_no": question.question_no,
            "marks": question.marks,
            "module": question.module,
            "text": question_text,
            "has_internal_choice": question.has_internal_choice,
            "source_chunk": source_chunk,
        }

        # If an internal choice is requested, recursively generate the alternative question
        if question.has_internal_choice and question.or_choice:
            or_marks = getattr(question.or_choice, 'marks', question.marks)
            or_module = getattr(question.or_choice, 'module', question.module)
            or_sub_qs_config = getattr(question.or_choice, 'sub_questions', None)
            has_or_sub_qs = bool(or_sub_qs_config)

            or_chunk_text = self._get_relevant_chunks(
                module=or_module,
                topic_mapping=topic_mapping,
                chunks_dict=safe_chunks_dict,
            )
            or_source_chunk = None
            if or_chunk_text:
                or_source_chunk = or_chunk_text[:80]

            or_topic = self._get_random_topic(or_module, syllabus_topics, seen_topics.get(or_module))
            # Mark OR topic as seen
            if or_module not in seen_topics:
                seen_topics[or_module] = set()
            seen_topics[or_module].add(or_topic)

            or_question_text = ""
            if not has_or_sub_qs:
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
                "source_chunk": or_source_chunk,
            }

            if has_or_sub_qs:
                or_sub_qs = []
                for sq in or_sub_qs_config:
                    sq_topic = self._get_random_topic(or_module, syllabus_topics, seen_topics.get(or_module))
                    if or_module not in seen_topics:
                        seen_topics[or_module] = set()
                    seen_topics[or_module].add(sq_topic)

                    sq_marks = getattr(sq, 'marks', or_marks)
                    sq_label = getattr(sq, 'label', '?')

                    if self._model_loaded:
                        sq_text = self._generate_with_t5(
                            topic=sq_topic, context=or_chunk_text, marks=sq_marks
                        )
                    else:
                        sq_text = self._generate_with_template(
                            topic=sq_topic, context=or_chunk_text
                        )

                    or_sub_qs.append({
                        "label": sq_label,
                        "marks": sq_marks,
                        "text": sq_text,
                        "source_chunk": or_source_chunk,
                    })
                base_q["or_question"]["sub_questions"] = or_sub_qs

        # Generate sub-questions if configured
        if has_sub_qs:
            sub_qs = []
            for sq in question.sub_questions:
                sq_topic = self._get_random_topic(question.module, syllabus_topics, seen_topics.get(question.module))
                if question.module not in seen_topics:
                    seen_topics[question.module] = set()
                seen_topics[question.module].add(sq_topic)

                sq_marks = sq.marks if hasattr(sq, 'marks') else sq.get('marks', question.marks)
                sq_label = sq.label if hasattr(sq, 'label') else sq.get('label', '?')

                if self._model_loaded:
                    sq_text = self._generate_with_t5(
                        topic=sq_topic, context=chunk_text, marks=sq_marks
                    )
                else:
                    sq_text = self._generate_with_template(
                        topic=sq_topic, context=chunk_text
                    )

                sub_qs.append({
                    "label": sq_label,
                    "marks": sq_marks,
                    "text": sq_text,
                    "source_chunk": source_chunk,
                })
            base_q["sub_questions"] = sub_qs

        return base_q

    # =====================================================
    # Improved T5 Generation Function (complexity control)
    # =====================================================

    def _generate_with_t5(
        self, topic: str, context: Optional[str], marks: int
    ) -> str:
        if marks <= 2:
            ctx_summary = "No context provided."
            if context:
                ctx_summary = context[:400]
            short_instructions = [
                "Write a short, direct university exam question about the topic. Do not generate code.",
                "Write a one-line recall question asking the student to define or identify the topic.",
                "Ask the student to name or identify a key concept related to the topic.",
                "Write a brief factual question testing recall of the topic.",
            ]
            instruction = random.choice(short_instructions)
            prompt = f"{instruction}\nTopic: {topic}\nContext: {ctx_summary}\nQuestion (Short):"
            max_tokens = 40
        elif marks <= 5:
            ctx_summary = "No context provided."
            if context:
                ctx_summary = context[:600]
            medium_instructions = [
                "Write a formal university exam question asking to explain how the topic works. Avoid code.",
                "Write a question asking the student to describe the working principle of the topic. Avoid code.",
                "Write a question that requires comparing or contrasting the topic with related concepts. Avoid code.",
                "Write a question asking about the significance or role of the topic in its field. Avoid code.",
                "Write a question asking the student to illustrate the topic with a relevant example. Avoid code.",
                "Write a question asking the student to summarize the key characteristics of the topic. Avoid code.",
                "Ask a question about the advantages and limitations of the topic. Avoid code.",
            ]
            instruction = random.choice(medium_instructions)
            prompt = f"{instruction}\nTopic: {topic}\nContext: {ctx_summary}\nQuestion (Medium):"
            max_tokens = 80
        else:
            # High-mark complexity enhancement
            ctx_summary = "No context provided."
            if context:
                ctx_summary = context[:1000]
            instruction = (
                "Provide a comprehensive, multi-layered academic discussion question. "
                "Analyze architectural components, security implications, and practical integration in detail. "
                "The question must demand deep analysis and factual evaluation of the provided context. "
                "Do not generate simple definitions or internal code logs."
            )
            prompt = f"{instruction}\n\nTOPIC: {topic}\nCONTEXT:\n{ctx_summary}\n\nComplex Discussion Question ({marks} Marks):"
            max_tokens = 150

        if not self._tokenizer or not self._model:
            logger.error("Attempted to generate with T5 but model/tokenizer not loaded.")
            return self._generate_with_template(topic, context)

        inputs = self._tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=768
        )

        with torch.inference_mode():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.3,        # Reduced temperature significantly to prevent hallucinated code/math
                top_k=40,               # Tighter nucleus sampling
                top_p=0.90,
                repetition_penalty=1.2, # Stronger penalty for repeating words
                no_repeat_ngram_size=3, # Ban repeating the same 3 words (fixes the "Illustrate the concept" loop)
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

        # FINAL HALLUCINATION FILTER: Strip code-like snippets (e.g., Algamal = q-1, for i in, etc.)
        generated_text = self._filter_hallucinations(generated_text)

        return generated_text

    def _filter_hallucinations(self, text: str) -> str:
        """
        Regex-based safety net to remove suspected code or mathematical 
        hallucinations that Flan-T5 occasionally generates.
        """
        # Patterns for code-like assignments and loops
        hallucination_patterns = [
            r"[\w\)]+\s?=\s?[\w\)]+\s?[-\+]\s?[\w\d]+;?", # Assignments like x = y + 1 or Algamal) = q - 1
            r"for\s+\w+\s+in\s+range.*",       # Python loops
            r"\w+\[\w+\]\s?=\s?.*",            # Array assignments
            r"printf\(.*\);?",                 # C-style print
            r"print\(.*\)",                    # Python print
            r"import\s+\w+",                   # Imports
            r"def\s+\w+\(.*\):",               # Function defs
        ]
        
        filtered = text
        for pattern in hallucination_patterns:
            filtered = re.sub(pattern, "", filtered, flags=re.IGNORECASE).strip()
            
        # Clean up any resulting double spaces or hanging semicolons
        filtered = re.sub(r"\s+", " ", filtered).strip()
        filtered = filtered.rstrip(";").strip()
        
        # If the filter nuked too much of the text, return original or a fallback
        if len(filtered.split()) < 3:
            return text
            
        return filtered

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
            ctx_summary = (context[:100] if context else "")
            question_text += f"\n\n[Based on: {ctx_summary}...]"

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
        self, module: str, topic_mapping: Dict, chunks_dict: Dict[int, str]
    ) -> Optional[str]:
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
        self, module: str, syllabus_topics: Optional[Dict], exclude_topics: Optional[set] = None
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
            topics_list = []
            
            # New format: value is dict with 'topics' key
            if isinstance(value, dict) and "topics" in value:
                topics_list = value["topics"]
            # Legacy format: value is list of topics
            elif isinstance(value, list):
                topics_list = value

            if topics_list:
                # Deduplication logic: prioritize topics not in exclude_topics
                available = [str(t) for t in topics_list if t not in (exclude_topics or set())]
                if available:
                    return random.choice(available)
                # If all exhausted, fallback to random from full list
                return str(random.choice(topics_list))

        # Fallback to the module name itself. No cross-module contamination.
        return module

    @staticmethod
    def _load_json(filepath: str) -> Optional[Any]:

        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)


question_service = QuestionService()