"""
Question Generation Service — generate exam questions using Flan-T5 and Mistral.

Responsibility:
- Orchestrate the generation pipeline (Chunks -> Draft -> Evaluate/Refine -> Final).
- Manage model caching and loading (PyTorch, SentenceTransformers, spaCy).
- Provide the public API endpoint methods.
"""

import os
import re
import json
import random
import logging
import torch
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from app.core.config import (
    FLAN_T5_MODEL_PATH,
    FLAN_T5_FALLBACK_MODEL,
    SBERT_MODEL_PATH,
    SBERT_FALLBACK_MODEL,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
)

# --- Imported Utilities ---
from app.utils.question_constants import (
    BLOOM_VERBS,
    GENERIC_SUBJECT_NAMES,
    SCAFFOLD_TEMPLATE,
    CONTEXT_STOPWORDS
)

from app.utils.ollama_client import (
    ollama_generate,
    extract_generated_question,
    refine_with_ollama
)

from app.utils.context_utils import (
    compress_context,
    get_relevant_chunks,
    find_matching_key,
    normalize_subject_name,
    mark_bucket,
    extract_topic_tokens
)

from app.utils.question_validation import (
    validate_question,
    filter_hallucinations
)


logger = logging.getLogger(__name__)


class QuestionService:
    """
    Generates exam questions using a fine-tuned Flan-T5 model and Mistral refinement.
    """

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._model_loaded = False
        self._load_attempted = False
        # Cache for textbook data
        self._chunks_cache: Optional[List[Dict[str, Any]]] = None
        self._chunks_dict_cache: Optional[Dict[int, str]] = None
        self._syllabus_cache: Optional[Dict[str, Any]] = None
        # High-mark (>5) pipeline caches
        self._pyq_dataset: Optional[List[Dict[str, Any]]] = None
        self._sbert_model = None
        self._spacy_nlp = None

        # Best-effort warmup 
        try:
            self._load_pyq_dataset()
        except Exception as e:
            logger.warning(f"[HighMark] PYQ warmup failed: {e}")

        try:
            self._get_spacy_nlp()
        except Exception as e:
            logger.warning(f"[HighMark] spaCy warmup failed: {e}")

    def clear_caches(self):
        """Reset all data caches so the next generation reads fresh files."""
        self._chunks_cache = None
        self._chunks_dict_cache = None
        self._syllabus_cache = None

    @staticmethod
    def _load_json(filepath: str) -> Optional[Any]:
        """Utility to safely load a JSON file."""
        import os, json
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _get_sbert_model(self):
        if self._sbert_model is not None:
            return self._sbert_model

        from sentence_transformers import SentenceTransformer

        if os.path.exists(SBERT_MODEL_PATH):
            logger.info(f"[HighMark] Loading custom SBERT model from {SBERT_MODEL_PATH}")
            self._sbert_model = SentenceTransformer(SBERT_MODEL_PATH)
        else:
            logger.warning(
                f"[HighMark] Custom SBERT model not found at {SBERT_MODEL_PATH}. "
                f"Falling back to {SBERT_FALLBACK_MODEL}"
            )
            self._sbert_model = SentenceTransformer(SBERT_FALLBACK_MODEL)

        return self._sbert_model

    def _get_spacy_nlp(self):
        if self._spacy_nlp is not None:
            return self._spacy_nlp

        try:
            import spacy
            logger.info("[HighMark] Loading spacy model en_core_web_sm...")
            self._spacy_nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(f"[HighMark] spaCy not available (entity checks skipped): {e}")
            self._spacy_nlp = None
        return self._spacy_nlp

    def _load_pyq_dataset(self) -> List[Dict[str, Any]]:
        if self._pyq_dataset is not None:
            return self._pyq_dataset

        pyq_path = Path(PROJECT_ROOT) / "pyq_mistral_train.jsonl"
        if not pyq_path.exists():
            logger.warning(f"[HighMark] pyq_mistral_train.jsonl not found at {pyq_path}.")
            self._pyq_dataset = []
            return self._pyq_dataset

        loaded: List[Dict[str, Any]] = []
        with open(pyq_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    loaded.append(json.loads(line))
                except Exception:
                    continue

        self._pyq_dataset = loaded
        logger.info(f"[HighMark] Loaded {len(self._pyq_dataset)} PYQ dataset rows.")
        return self._pyq_dataset


    def _parse_pyq_metadata(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper for fetch_similar_pyqs."""
        input_text = row.get("input", "") or ""
        direct_subject = (row.get("subject") or "").strip()
        direct_module = (row.get("module") or "").strip()
        direct_marks = row.get("marks")
        direct_bloom = (row.get("bloom_level") or "").strip()

        subject_match = re.search(r"Subject:\s*(.+)", input_text)
        module_match = re.search(r"Module:\s*(.+)", input_text)
        marks_match = re.search(r"Marks:\s*(\d+)", input_text)
        bloom_match = re.search(r"Bloom\s+Level:\s*([^\n]+)", input_text)
        context_match = re.search(r"Context:\s*(.+?)\n\n", input_text, re.DOTALL)

        subject_raw = direct_subject or (subject_match.group(1).strip() if subject_match else "")
        module_raw = direct_module or (module_match.group(1).strip() if module_match else "")
        parsed_marks = None
        if direct_marks is not None:
            try:
                parsed_marks = int(direct_marks)
            except (TypeError, ValueError):
                parsed_marks = None
        if parsed_marks is None and marks_match:
            parsed_marks = int(marks_match.group(1))
            
        return {
            "subject": subject_raw,
            "normalized_subject": normalize_subject_name(subject_raw),
            "module": module_raw,
            "normalized_module": module_raw, # Handled externally
            "marks": parsed_marks,
            "mark_bucket": mark_bucket(parsed_marks) if parsed_marks is not None else "unknown",
            "bloom_level": direct_bloom or (bloom_match.group(1).strip() if bloom_match else ""),
            "context": context_match.group(1).strip() if context_match else "",
        }

    def fetch_similar_pyqs(
        self, topic: str, pyq_dataset: List[Dict[str, Any]], k: int = 3, subject: str = "", module: str = "", marks: Optional[int] = None,
    ) -> List[str]:
        candidates = []
        norm_subject = normalize_subject_name(subject)
        topic_tokens = extract_topic_tokens(topic)
        target_bucket = mark_bucket(marks)

        for row in pyq_dataset:
            output = (row.get("response") or row.get("output") or "").strip()
            if not output: continue

            meta = self._parse_pyq_metadata(row)
            haystack = " ".join([output.lower(), (meta.get("context") or "").lower(), (row.get("input") or "").lower()])
            token_overlap = sum(1 for token in topic_tokens if token in haystack)
            candidates.append({"output": output, "meta": meta, "token_overlap": token_overlap})

        if not candidates: return [""] * k

        filtered = [c for c in candidates if c["token_overlap"] > 0]
        if not filtered: filtered = candidates

        pyq_questions = [item["output"] for item in filtered]
        k = min(k, len(pyq_questions))
        sbert_model = self._get_sbert_model()
        from sentence_transformers import util

        topic_vec = sbert_model.encode(topic, convert_to_tensor=True)
        q_vecs = sbert_model.encode(pyq_questions, convert_to_tensor=True)
        scores = util.cos_sim(topic_vec, q_vecs)[0]
        top_indices = scores.topk(k).indices.tolist()
        return [pyq_questions[i] for i in top_indices]


    def generate_high_mark_question(
        self, topic: str, chunks: List[str], marks: int, subject: str = "Computer Science", module: str = "",
    ) -> str:
        try:
            sbert_model = self._get_sbert_model()
            context = compress_context(chunks, topic, max_tokens=400, sbert_model=sbert_model)
            expected_bloom = self._expected_bloom_for_marks(marks)
            
            # Fetch few-shot PYQ exemplars to improve stylistic quality
            if self._pyq_dataset:
                pyqs = self.fetch_similar_pyqs(topic, self._pyq_dataset, k=2, subject=subject, module=module, marks=marks)
            else:
                pyqs = []
                
            pyq_section = ""
            if pyqs:
                valid_pyqs = [q for q in pyqs if len(q.split()) > 10]
                if valid_pyqs:
                    formatted_pyqs = "\n".join([f"- {q}" for q in valid_pyqs])
                    pyq_section = f"Reference Stylistic Examples (do NOT copy content):\n{formatted_pyqs}\n"
            
            last_reason = ""
            for attempt in range(3):
                prompt = SCAFFOLD_TEMPLATE.format(
                    subject=subject, module=module or "Unknown", marks=marks,
                    bloom_level=expected_bloom, compressed_context=context, topic=topic,
                    pyq_section=pyq_section
                )

                if attempt > 0 and last_reason:
                    prompt += f"\nNote: Your previous attempt was rejected because: {last_reason}. Please correct this."

                full_output = ollama_generate(
                    prompt,
                    options={"num_predict": 120, "temperature": 0.65, "repeat_penalty": 1.3},
                    model="mistral-pyq"
                )

                question = extract_generated_question(full_output)
                question = (question or "").strip()
                if "?" in question: question = question[: question.index("?") + 1].strip()
                if question and not question.endswith("?"): question = question.rstrip(".") + "?"

                q_words = question.split() if question else []
                if len(q_words) > 60:
                    question = " ".join(q_words[:60]).rstrip(".")
                    if not question.endswith("?"): question = question.rstrip("?") + "?"

                spacy_nlp = self._get_spacy_nlp()
                valid, reason = validate_question(question, context, marks, sbert_model, spacy_nlp)
                if valid: return question

                last_reason = reason
                logger.info(f"[HighMark] Rejected attempt {attempt + 1}: {reason}")

            return self.fallback_t5_anchor_rewrite(topic, context, marks, subject)
        except Exception as e:
            logger.error(f"[HighMark] Generation crashed; falling back to template: {e}")
            context_str = locals().get("context")
            return self._generate_with_template(topic, context_str if isinstance(context_str, str) else None, marks=marks)

    def fallback_t5_anchor_rewrite(self, topic: str, context: str, marks: int, subject: str) -> str:
        try:
            t5_draft = self._generate_with_t5(topic, context, marks)
        except Exception as e:
            logger.warning(f"[HighMark] T5 draft failed; using template. Details: {e}")
            t5_draft = self._generate_with_template(topic, context, marks=marks)

        context_excerpt = (context or "").strip()
        if len(context_excerpt.split()) > 220:
            context_excerpt = " ".join(context_excerpt.split()[:220])

        rewrite_prompt = f"""\
You generate clean university exam questions from syllabus metadata and context.

### Instruction:
Rewrite the following draft into a clean, specific {marks}-mark exam question.
It must end with "?", be under 60 words, and be answerable from the provided context.
Do NOT reference any "book" or "lecture notes". Do NOT write an answer; write only the question.

### Input:
Context:
{context_excerpt}

Draft: {t5_draft}

### Response:
"""

        last_reason = ""
        sbert_model = self._get_sbert_model()
        spacy_nlp = self._get_spacy_nlp()
        
        for attempt in range(2):
            try:
                prompt = rewrite_prompt
                if attempt > 0 and last_reason:
                    prompt = prompt.rstrip() + f"\nNote: Your previous attempt was rejected because: {last_reason}. Please correct it.\n"

                full_output = ollama_generate(
                    prompt,
                    options={"num_predict": 100, "temperature": 0.5, "repeat_penalty": 1.2},
                    model="mistral"
                )
                result = extract_generated_question(full_output)
                result = (result or "").strip()
                if "?" in result: result = result[: result.index("?") + 1].strip()
                if result and not result.endswith("?"): result = result.rstrip(".") + "?"

                r_words = result.split() if result else []
                if len(r_words) > 60:
                    result = " ".join(r_words[:60]).rstrip(".")
                    if not result.endswith("?"): result = result.rstrip("?") + "?"

                valid, reason = validate_question(result, context, marks, sbert_model, spacy_nlp)
                if valid: return result

                last_reason = reason
                logger.info(f"[HighMark] Fallback attempt {attempt + 1} rejected: {reason}")
            except Exception as e:
                logger.error(f"[HighMark] Fallback rewrite failed: {e}")

        t5_draft_q = (t5_draft or "").strip()
        if t5_draft_q and not t5_draft_q.endswith("?"):
            t5_draft_q = t5_draft_q.rstrip(".") + "?"
        return t5_draft_q


    def _load_model(self):
        if self._load_attempted: return
        self._load_attempted = True

        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            model_path = FLAN_T5_MODEL_PATH
            if not os.path.exists(model_path):
                model_path = FLAN_T5_FALLBACK_MODEL
            logger.info(f"Loading T5 model from {model_path}...")
            self._tokenizer = AutoTokenizer.from_pretrained(model_path)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            self._model_loaded = True
            logger.info("T5 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load T5 model: {e}. Using template fallback.")
            self._model_loaded = False
            
        try:
            torch.set_num_threads(4) 
        except Exception:
            pass


    def generate_questions_from_pattern(
        self, exam_pattern: Any, processed_data_dir: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:

        if processed_data_dir is None: processed_data_dir = str(PROCESSED_DATA_DIR)

        topic_mapping = self._load_json(os.path.join(processed_data_dir, "topic_chunk_mapping.json")) or {}

        if self._chunks_cache is None:
            self._chunks_cache = self._load_json(os.path.join(processed_data_dir, "textbook_chunks.json")) or []
            self._chunks_dict_cache = {c["chunk_id"]: c["text"] for c in self._chunks_cache}
        
        chunks_dict = self._chunks_dict_cache

        syllabus_topics = self._load_json(os.path.join(processed_data_dir, "selected_topics.json"))
        if not syllabus_topics:
            syllabus_topics = self._load_json(os.path.join(processed_data_dir, "syllabus_topics.json")) or {}

        self._load_model()
        generated_questions: Dict[str, List[Dict[str, Any]]] = {}
        seen_topics: Dict[str, set] = {}

        for part in exam_pattern.parts:
            part_qs = []
            if part.questions:
                for question in part.questions:
                    gq = self._generate_single_question(
                        question=question, part=part, topic_mapping=topic_mapping,
                        chunks_dict=chunks_dict, syllabus_topics=syllabus_topics, seen_topics=seen_topics,
                    )
                    part_qs.append(gq)
            generated_questions[part.part_name] = part_qs

        return generated_questions

    def _resolve_course_subject(self, syllabus_topics: Optional[Dict[str, Any]]) -> str:
        if not syllabus_topics: return "Computer Science"
        course_title = str(syllabus_topics.get("course_title", "")).strip()
        if not course_title or normalize_subject_name(course_title) in GENERIC_SUBJECT_NAMES:
            return "Computer Science"
        return course_title

    def _generate_single_question(
        self, question: Any, part: Any, topic_mapping: Dict, chunks_dict: Dict, syllabus_topics: Dict, seen_topics: Dict
    ) -> Dict[str, Any]:
        subject = self._resolve_course_subject(syllabus_topics)
        topic = self._get_random_topic(question.module, syllabus_topics, seen_topics.get(question.module))
        
        if question.module not in seen_topics: seen_topics[question.module] = set()
        seen_topics[question.module].add(topic)

        chunk_text = get_relevant_chunks(str(question.module), topic, topic_mapping, chunks_dict or {})
        has_sub_qs = hasattr(question, 'sub_questions') and question.sub_questions

        question_text = ""
        if not has_sub_qs:
            question_text = self._generate_with_bloom_retry(topic=topic, context=chunk_text, marks=question.marks, module=str(question.module), subject=subject)

        base_q = {
            "question_no": question.question_no, "marks": question.marks, "module": question.module,
            "text": question_text, "has_internal_choice": question.has_internal_choice,
            "source_chunk": chunk_text[:80] if chunk_text else None,
        }

        if question.has_internal_choice and getattr(question, 'or_choice', None):
            or_marks = getattr(question.or_choice, 'marks', question.marks)
            or_module = getattr(question.or_choice, 'module', question.module)
            has_or_sub_qs = bool(getattr(question.or_choice, 'sub_questions', None))

            or_topic = self._get_random_topic(or_module, syllabus_topics, seen_topics.get(or_module))
            if or_module not in seen_topics: seen_topics[or_module] = set()
            seen_topics[or_module].add(or_topic)

            or_chunk_text = get_relevant_chunks(or_module, or_topic, topic_mapping, chunks_dict or {})
            
            or_question_text = ""
            if not has_or_sub_qs:
                or_question_text = self._generate_with_bloom_retry(topic=or_topic, context=or_chunk_text, marks=or_marks, module=str(or_module), subject=subject)
            
            base_q["or_question"] = {
                "marks": or_marks, "module": or_module, "text": or_question_text,
                "source_chunk": or_chunk_text[:80] if or_chunk_text else None,
            }

            if has_or_sub_qs:
                or_sub_qs = []
                for sq in question.or_choice.sub_questions:
                    sq_t = self._get_random_topic(or_module, syllabus_topics, seen_topics.get(or_module))
                    seen_topics[or_module].add(sq_t)
                    sq_m = getattr(sq, 'marks', or_marks)
                    sq_c = get_relevant_chunks(or_module, sq_t, topic_mapping, chunks_dict or {})
                    if self._model_loaded: sq_text = self._generate_with_bloom_retry(sq_t, sq_c, sq_m, str(or_module), subject)
                    else: sq_text = self._generate_with_template(sq_t, sq_c, sq_m)
                    or_sub_qs.append({"label": getattr(sq, 'label', '?'), "marks": sq_m, "text": sq_text, "source_chunk": sq_c[:80] if sq_c else None})
                base_q["or_question"]["sub_questions"] = or_sub_qs

        if has_sub_qs:
            sub_qs = []
            for sq in question.sub_questions:
                sq_t = self._get_random_topic(question.module, syllabus_topics, seen_topics.get(question.module))
                seen_topics[question.module].add(sq_t)
                sq_m = getattr(sq, 'marks', question.marks)
                sq_c = get_relevant_chunks(question.module, sq_t, topic_mapping, chunks_dict or {})
                if self._model_loaded: sq_text = self._generate_with_bloom_retry(sq_t, sq_c, sq_m, str(question.module), subject)
                else: sq_text = self._generate_with_template(sq_t, sq_c, sq_m)
                sub_qs.append({"label": getattr(sq, 'label', '?'), "marks": sq_m, "text": sq_text, "source_chunk": sq_c[:80] if sq_c else None})
            base_q["sub_questions"] = sub_qs

        return base_q


    @staticmethod
    def _expected_bloom_for_marks(marks: int) -> str:
        if marks <= 2: return "Remember"
        elif marks <= 5: return "Understand"
        return "Analyze"

    def _generate_with_bloom_retry(self, topic: str, context: Optional[str], marks: int, module: str = "", subject: str = "Computer Science") -> str:
        if marks > 5:
            try: return self.generate_high_mark_question(topic=topic, chunks=[context] if context else [], marks=marks, subject=subject, module=module)
            except Exception as e:
                logger.warning(f"[HighMark] Routing failed: {e}")
                return self._generate_with_template(topic, context, marks=marks)

        if not self._model_loaded: return self._generate_with_template(topic, context, marks=marks)

        expected = self._expected_bloom_for_marks(marks)
        for attempt in range(2):
            q = self._generate_with_t5(topic, context, marks, expected if attempt == 1 else None)
            from app.services.bloom_service import bloom_service
            predicted = bloom_service.classify(q)
            if predicted == expected: return q
        return q

    def _generate_with_t5(self, topic: str, context: Optional[str], marks: int, bloom_override: Optional[str] = None) -> str:
        styles = [
            f"Write a question about '{topic}'.",
            f"Ask a factual question on '{topic}'.",
        ]
        prompt = f"{random.choice(styles)}\n\nContext: {context[:600] if context else ''}\n\nQuestion:"
        
        if bloom_override:
            verbs = BLOOM_VERBS.get(bloom_override, [])
            prompt += f"\nIMPORTANT: Require: {bloom_override}. Use verbs like: {', '.join(verbs)}"

        if not self._tokenizer or not self._model:
            return self._generate_with_template(topic, context, marks)

        inputs = self._tokenizer(prompt, return_tensors="pt", truncation=True, max_length=768)
        with torch.inference_mode():
            outputs = self._model.generate(
                **inputs, max_new_tokens=80, do_sample=True, temperature=0.5,
                top_k=50, top_p=0.90, repetition_penalty=1.2, no_repeat_ngram_size=3,
            )
        
        ans = self._tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        ans = re.sub(r"^(Question|Output|Answer)[\s]*:[\s]*", "", ans, flags=re.IGNORECASE).strip()
        if ans and not ans.endswith("?"):
            if ' ' in ans: ans = ans.rsplit(' ', 1)[0]
            ans += "?"

        ans = filter_hallucinations(ans)
        
        # Pass extract_topic_tokens as lambda or function reference
        return refine_with_ollama(ans, marks, topic, extract_topic_tokens)

    def _generate_with_template(self, topic: str, context: Optional[str], marks: Optional[int] = None) -> str:
        words = re.findall(r"[A-Za-z]+", context or "")
        terms = [w.lower() for w in set(words) if len(w) > 4 and w.lower() not in set(extract_topic_tokens(topic))][:2]
        related = ", ".join(terms)

        if marks and marks <= 3: return f"What is {topic}, and how is it related to {related}?" if related else f"What is {topic}?"
        if marks and marks <= 5: return f"Explain {topic} with reference to {related}." if related else f"Explain how {topic} works."
        return f"Discuss {topic} in detail with reference to {related}." if related else f"Discuss {topic} in detail."

    def _get_random_topic(self, module: str, syllabus_topics: Optional[Dict], exclude_topics: Optional[set] = None) -> str:
        if not syllabus_topics: return module
        modules = syllabus_topics.get("modules", syllabus_topics)
        matched_key = find_matching_key(module, modules.keys())

        if matched_key:
            val = modules[matched_key]
            topics = val.get("topics", []) if isinstance(val, dict) else (val if isinstance(val, list) else [])
            if topics:
                available = [str(t) for t in topics if t not in (exclude_topics or set())]
                return random.choice(available if available else topics)
        return module


question_service = QuestionService()
