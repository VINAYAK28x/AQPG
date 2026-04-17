"""
Question validation & hallucination filtering helpers.

Extracted from question_service.py to keep the service file focused on orchestration.
"""

import re
import logging
from typing import Tuple, Optional

from app.utils.question_constants import VALID_OPENERS

logger = logging.getLogger(__name__)


def validate_question(
    question: str,
    context: str,
    marks: int,
    sbert_model=None,
    spacy_nlp=None,
) -> Tuple[bool, str]:
    """
    Validate a generated question for length, structure, hallucination,
    and semantic coherence against the source context.
    """
    q = (question or "").strip()
    context = context or ""

    # 1. Length gate (10-65 words)
    words = q.split()
    if not (10 <= len(words) <= 65):
        return False, f"length {len(words)} out of range 10-65"

    # 2. Must end with "?"
    if not q.endswith("?"):
        return False, "does not end with ?"

    # 3. Opening verb whitelist
    if not words:
        return False, "empty question"

    if words[0].lower() not in VALID_OPENERS:
        return False, f"invalid opening word: {words[0]}"

    # 3b. Reject meta-answer / lecture-note references (common failure mode).
    lowered = q.lower()
    banned_phrases = [
        "example answer",
        "lecture notes",
        "in the book",
        "earlier in the book",
        "university lecture notes",
        "supported by relevant concepts",
        "answer should be",
        "provide an answer",
        "support your analysis",
        "show all steps of your calculations",
    ]
    for phrase in banned_phrases:
        if phrase in lowered:
            return False, f"banned meta phrase: {phrase}"

    # 4. Hallucination probe — check named entities against context vocab
    if spacy_nlp is not None:
        doc = spacy_nlp(q)
        normalized_context = re.sub(r"[^a-z0-9\s\-]+", " ", context.lower())
        context_vocab = set(normalized_context.split())
        alien_entities = [
            ent.text
            for ent in doc.ents
            if ent.text
            and not (
                re.sub(r"[^a-z0-9\s\-]+", " ", ent.text.lower()).strip() in normalized_context
                or all(
                    token in context_vocab
                    for token in re.findall(r"[a-z0-9\-]+", ent.text.lower())
                )
            )
        ]
        if len(alien_entities) > 2:
            return False, f"hallucinated entities: {alien_entities}"

    # 5. Semantic coherence — cosine similarity between question and context
    if sbert_model is not None:
        try:
            from sklearn.metrics.pairwise import cosine_similarity

            q_vec = sbert_model.encode([q])
            c_vec = sbert_model.encode([context])
            sim = float(cosine_similarity(q_vec, c_vec)[0][0])
            if sim < 0.55:
                return False, f"low coherence: cosine_sim={sim:.2f}"
        except Exception as e:
            return False, f"coherence_check_failed: {e}"

    return True, "ok"


def filter_hallucinations(text: str) -> str:
    """
    Regex-based safety net to remove suspected code or mathematical
    hallucinations that Flan-T5 occasionally generates.
    """
    # Patterns for code-like assignments and loops
    hallucination_patterns = [
        r"[\w\)]+\s?=\s?[\w\)]+\s?[-\+]\s?[\w\d]+;?",  # Assignments like x = y + 1
        r"for\s+\w+\s+in\s+range.*",       # Python loops
        r"\w+\[\w+\]\s?=\s?.*",            # Array assignments
        r"printf\(.*\);?",                 # C-style print
        r"print\(.*\)",                    # Python print
        r"import\s+\w+",                   # Imports
        r"def\s+\w+\(.*\):",              # Function defs
    ]

    filtered = text
    for pattern in hallucination_patterns:
        filtered = re.sub(pattern, "", filtered, flags=re.IGNORECASE).strip()

    # Clean up any resulting double spaces or hanging semicolons
    filtered = re.sub(r"\s+", " ", filtered).strip()
    filtered = filtered.rstrip(";").strip()

    # If the filter nuked too much of the text, return original
    if len(filtered.split()) < 3:
        return text

    return filtered
