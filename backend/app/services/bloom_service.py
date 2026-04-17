"""
Bloom's Taxonomy Classification Service — classify questions by cognitive level.

Responsibilities:
- Classify a question text into one of 6 Bloom's taxonomy levels
- Use DistilBERT-based classification from the trained model at models/blooms_classifier
- Fall back to keyword-based heuristic classification otherwise

Bloom's Levels: Remember, Understand, Apply, Analyze, Evaluate, Create
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Bloom's taxonomy levels in order
BLOOM_LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

# Map numeric LABEL_N → Bloom level (fallback if config.json still has generic labels)
LABEL_INDEX_MAP = {
    "LABEL_0": "Remember",
    "LABEL_1": "Understand",
    "LABEL_2": "Apply",
    "LABEL_3": "Analyze",
    "LABEL_4": "Evaluate",
    "LABEL_5": "Create",
}

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

# Auto-discover the model path relative to the project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # backend -> AQPG
_DEFAULT_MODEL_PATH = _PROJECT_ROOT / "models" / "bloom_classifier" / "kaggle" / "working" / "blooms_classifier"


class BloomClassifierService:
    """
    Classifies question text into Bloom's taxonomy levels.

    Attempts to use a fine-tuned DistilBERT model for classification.
    Falls back to keyword-based heuristics if no model is available.
    """

    def __init__(self, model_path: Optional[str] = None):
        self._classifier = None
        self._model_path = model_path or str(_DEFAULT_MODEL_PATH)
        self._load_attempted = False

    def _load_model(self):
        """Attempt to load the DistilBERT classifier."""
        if self._load_attempted:
            return
        self._load_attempted = True

        try:
            from transformers import pipeline

            if self._model_path and os.path.exists(self._model_path):
                logger.info(f"Loading Bloom's DistilBERT classifier from {self._model_path}")
                self._classifier = pipeline(
                    "text-classification",
                    model=self._model_path,
                    tokenizer=self._model_path,
                )
                logger.info("Bloom's DistilBERT classifier loaded successfully")
            else:
                logger.info(
                    f"No fine-tuned Bloom classifier found at {self._model_path}. "
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

    def classify_batch(self, question_texts: List[str]) -> List[str]:
        """
        Classify a batch of questions into Bloom's taxonomy levels.
        MUCH faster than individual calls on CPU.
        """
        if not question_texts:
            return []
            
        self._load_model()
        
        # If model is not loaded, fallback to keywords for each
        if self._classifier is None:
            return [self._classify_with_keywords(t) for t in question_texts]
            
        try:
            # transformers pipeline handles lists efficiently
            results = self._classifier(question_texts, batch_size=4)
            labels = []
            for i, res in enumerate(results):
                label = res["label"]
                
                # Mapping logic (extracted to helper)
                labels.append(self._map_label_to_bloom(label, question_texts[i]))
            return labels
        except Exception as e:
            logger.warning(f"Batch classification failed: {e}")
            return [self._classify_with_keywords(t) for t in question_texts]

    def _map_label_to_bloom(self, label: str, original_text: str) -> str:
        """Helper to map model labels to BLOOM_LEVELS."""
        # If the label is already a Bloom level name, return it
        for level in BLOOM_LEVELS:
            if level.lower() == label.lower():
                return level

        # If it's a generic LABEL_N, map it
        if label in LABEL_INDEX_MAP:
            return LABEL_INDEX_MAP[label]

        # Last resort: try substring matching
        for level in BLOOM_LEVELS:
            if level.lower() in label.lower():
                return level

        return self._classify_with_keywords(original_text)

    def _classify_with_model(self, question_text: str) -> str:
        """Classify using the DistilBERT pipeline."""
        try:
            result = self._classifier(question_text[:512])
            if result and len(result) > 0:
                return self._map_label_to_bloom(result[0]["label"], question_text)
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


# Module-level singleton — auto-discovers the model from the project's models/ directory
bloom_service = BloomClassifierService()

