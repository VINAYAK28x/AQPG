"""
Syllabus Service — parse syllabus PDFs to extract module-wise topics.

Responsibilities:
- Extract text from syllabus PDFs
- Parse module headings and topic lists
- Return structured module → topics mapping
"""

import re
import logging
from typing import Dict, List

from app.services.ingestion_service import extract_text

logger = logging.getLogger(__name__)


def extract_syllabus_text(pdf_bytes: bytes) -> str:
    """
    Extract text content from a syllabus PDF.

    Args:
        pdf_bytes: Raw bytes of the syllabus PDF.

    Returns:
        Extracted text.
    """
    text = extract_text(pdf_bytes)
    logger.debug(f"Syllabus text length: {len(text)}")
    return text


def extract_module_topics(text: str) -> Dict[str, List[str]]:
    """
    Parse syllabus text to extract module-wise topics.

    Detects module headings like 'Module I', 'Module 1', etc.
    Splits topic lines on common delimiters and filters noise.

    Args:
        text: Raw syllabus text.

    Returns:
        Dict mapping module names to lists of topic strings.
    """
    modules: Dict[str, List[str]] = {}
    current_module = None

    ignore_keywords = [
        "course outcome", "course outcomes", "edition",
        "publisher", "textbook", "syllabus", "marks",
    ]

    lines = text.split("\n")
    logger.debug(f"Total syllabus lines: {len(lines)}")

    for line in lines:
        line = line.strip()

        # Stop parsing at References section
        if line.lower().startswith("references"):
            logger.debug("Stopped parsing at References")
            break

        # Detect module headings (handles both Roman and Arabic numerals)
        match = re.match(r"Module\s+([IVX0-9]+|[0-9]+)", line, re.IGNORECASE)
        if match:
            current_module = f"Module {match.group(1)}"
            modules[current_module] = []
            logger.debug(f"Found module: {current_module}")
            continue

        if not current_module or len(line) < 5:
            continue

        # Skip noise lines
        lower_line = line.lower()
        if any(word in lower_line for word in ignore_keywords):
            continue

        # Split topics on common delimiters
        parts = re.split(r"[.,;-]", line)
        for part in parts:
            topic = part.strip()
            if len(topic) > 5:
                modules[current_module].append(topic)

    # Fallback: if no "Module X" headings were found, put everything in "General Topics"
    if not modules:
        logger.warning("No explicit module headings found. Using generic topic grouping.")
        current_module = "General Topics"
        modules[current_module] = []
        for line in lines:
            line = line.strip()
            if line.lower().startswith("references"):
                break
            if len(line) < 5:
                continue
            lower_line = line.lower()
            if any(word in lower_line for word in ignore_keywords):
                continue
            parts = re.split(r"[.,;-]", line)
            for part in parts:
                topic = part.strip()
                if len(topic) > 5:
                    modules[current_module].append(topic)

    logger.debug(f"Extracted {len(modules)} modules")
    return modules
