"""
Bloom's Taxonomy Classification Service — classify questions by cognitive level.

Responsibilities:
- Classify a question text into one of 6 Bloom's taxonomy levels
- Use DistilBERT-based classification if a fine-tuned model is available
- Fall back to keyword-based heuristic classification otherwise

Bloom's Levels: Remember, Understand, Apply, Analyze, Evaluate, Create
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Bloom's taxonomy levels in order
BLOOM_LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

# Keyword heuristics for fallback classification
BLOOM_KEYWORDS = {
    "Remember": [
        "define", "list", "state", "identify", "name", "recall",
        "recognize", "describe", "what is", "enumerate", "mention",
    ],
    "Understand": [
        "explain", "summarize", "paraphrase", "interpret", "classify",
        "discuss", "illustrate", "describe how", "distinguish",
    ],
    "Apply": [
        "apply", "demonstrate", "calculate", "solve", "use",
        "implement", "execute", "compute", "show how", "determine",
    ],
    "Analyze": [
        "analyze", "compare", "contrast", "differentiate", "examine",
        "break down", "categorize", "distinguish between", "investigate",
    ],
    "Evaluate": [
        "evaluate", "justify", "assess", "critique", "judge",
        "argue", "defend", "support", "recommend", "prioritize",
    ],
    "Create": [
        "design", "create", "develop", "propose", "construct",
        "formulate", "invent", "compose", "plan", "devise",
    ],
}


class BloomClassifierService:
    """
    Classifies question text into Bloom's taxonomy levels.

    Attempts to use a fine-tuned DistilBERT model for classification.
    Falls back to keyword-based heuristics if no model is available.
    """

    def __init__(self, model_path: Optional[str] = None):
        self._classifier = None
        self._model_path = model_path
        self._load_attempted = False

    def _load_model(self):
        """Attempt to load the DistilBERT classifier."""
        if self._load_attempted:
            return
        self._load_attempted = True

        try:
            from transformers import pipeline

            if self._model_path and os.path.exists(self._model_path):
                logger.info(f"Loading Bloom classifier from {self._model_path}")
                self._classifier = pipeline(
                    "text-classification",
                    model=self._model_path,
                    tokenizer=self._model_path,
                )
            else:
                logger.info(
                    "No fine-tuned Bloom classifier found. "
                    "Using keyword-based classification."
                )
        except Exception as e:
            logger.warning(f"Failed to load Bloom classifier model: {e}")

    def classify(self, question_text: str) -> str:
        """
        Classify a question into a Bloom's taxonomy level.

        Args:
            question_text: The text of the question.

        Returns:
            One of: Remember, Understand, Apply, Analyze, Evaluate, Create.
        """
        self._load_model()

        # Try model-based classification
        if self._classifier is not None:
            return self._classify_with_model(question_text)

        # Fallback to keyword heuristics
        return self._classify_with_keywords(question_text)

    def _classify_with_model(self, question_text: str) -> str:
        """Classify using the DistilBERT pipeline."""
        try:
            result = self._classifier(question_text[:512])
            if result and len(result) > 0:
                label = result[0]["label"]
                # Map model output to standard Bloom level
                for level in BLOOM_LEVELS:
                    if level.lower() in label.lower():
                        return level
                return label
        except Exception as e:
            logger.warning(f"Model classification failed: {e}")

        return self._classify_with_keywords(question_text)

    def _classify_with_keywords(self, question_text: str) -> str:
        """
        Classify using keyword matching heuristics.
        Checks from highest-order (Create) to lowest (Remember).
        """
        text_lower = question_text.lower()

        # Check from highest to lowest Bloom level
        for level in reversed(BLOOM_LEVELS):
            keywords = BLOOM_KEYWORDS[level]
            for keyword in keywords:
                if keyword in text_lower:
                    return level

        # Default to Remember if no keywords match
        return "Remember"


# Module-level singleton
bloom_service = BloomClassifierService()
