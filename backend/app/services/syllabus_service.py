"""
Syllabus Service — parse syllabus PDFs to extract module-wise topics.

Responsibilities:
- Extract text from syllabus PDFs
- Parse module headings and topic lists
- Extract course title and course code
- Return structured module → topics mapping with embedding-ready text
"""

import re
import logging
from typing import Dict, List, Optional

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


def extract_course_title(text: str) -> str:
    """
    Extract the course title from syllabus text using heuristics.

    Looks for common patterns like all-caps lines, lines after 'Course Title:',
    or the first substantial line.

    Args:
        text: Raw syllabus text.

    Returns:
        Extracted course title, or "Unknown" if not found.
    """
    lines = text.split("\n")

    # Pattern 1: Look for "Course Title:" or "Course Name:" label
    for line in lines[:30]:
        line = line.strip()
        match = re.match(
            r"(?:Course\s+(?:Title|Name))\s*[:\-–]\s*(.+)",
            line, re.IGNORECASE
        )
        if match:
            title = match.group(1).strip()
            if len(title) > 3:
                return _clean_title(title)

    # Pattern 2: Look for a prominent all-caps line (likely a title)
    for line in lines[:20]:
        line = line.strip()
        # Skip very short or very long lines
        if len(line) < 5 or len(line) > 100:
            continue
        # Skip lines that are clearly not titles
        lower = line.lower()
        if any(kw in lower for kw in [
            "module", "syllabus", "semester", "university", "department",
            "credit", "marks", "hours", "regulation", "scheme", "page",
            "textbook", "reference", "outcome"
        ]):
            continue
        # All-caps line with mostly alphabetic chars
        alpha_chars = sum(1 for c in line if c.isalpha())
        if alpha_chars > 5 and line == line.upper() and alpha_chars / max(len(line), 1) > 0.6:
            return _clean_title(line)

    # Pattern 3: Look for subject/course name patterns
    for line in lines[:30]:
        line = line.strip()
        match = re.match(
            r"(?:Subject|Program|Paper)\s*[:\-–]\s*(.+)",
            line, re.IGNORECASE
        )
        if match:
            title = match.group(1).strip()
            if len(title) > 3:
                return _clean_title(title)

    return "Unknown"


def _clean_title(title: str) -> str:
    """Clean and normalize a course title string."""
    # Remove trailing course codes
    title = re.sub(r"\s*[\(\[]\s*[\w\-]+\s*[\)\]]$", "", title)
    # Title case if all-caps
    if title == title.upper() and len(title) > 3:
        title = title.title()
    return title.strip()


def extract_course_code(text: str) -> str:
    """
    Extract the course code from syllabus text using regex patterns.

    Looks for patterns like XX-XXX-XXXX, CSXXX, 19CS301, etc.

    Args:
        text: Raw syllabus text.

    Returns:
        Extracted course code, or "Unknown" if not found.
    """
    lines = text.split("\n")

    # Pattern 1: Look for "Course Code:" label
    for line in lines[:30]:
        line = line.strip()
        match = re.match(
            r"(?:Course\s+Code|Subject\s+Code|Paper\s+Code|Code)\s*[:\-–]\s*(.+)",
            line, re.IGNORECASE
        )
        if match:
            code = match.group(1).strip().split()[0]  # Take first word
            if len(code) >= 3:
                return code

    # Pattern 2: Common course code formats
    # Examples: 19-202-0703, CS301, 19CS301, CSE-301, BCS-401
    code_patterns = [
        r"\b(\d{2}[\-]\d{3}[\-]\d{4})\b",           # 19-202-0703
        r"\b([A-Z]{2,4}[\-]?\d{3,4})\b",             # CS301, CSE-301, BCS-401
        r"\b(\d{2}[A-Z]{2,4}\d{3,4})\b",             # 19CS301
        r"\b([A-Z]{2,4}\d{2,3}[A-Z]?\d{0,2})\b",    # CS50, CS50A
    ]
    for line in lines[:30]:
        for pattern in code_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)

    return "Unknown"


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


def build_embedding_ready_text(topics: List[str]) -> str:
    """
    Create a cleaned, normalized text string from topics for semantic search
    and vector embeddings.

    Removes extra whitespace, special characters, and normalizes formatting.

    Args:
        topics: List of topic strings.

    Returns:
        Cleaned concatenated text ready for embedding.
    """
    # Join all topics, normalize whitespace
    combined = " ".join(topics)
    # Remove special / formatting characters
    combined = re.sub(r"[^\w\s]", " ", combined)
    # Collapse multiple spaces
    combined = re.sub(r"\s+", " ", combined).strip()
    # Title case for consistency
    combined = combined.title()
    return combined


def build_structured_syllabus(
    text: str,
    modules: Dict[str, List[str]],
) -> Dict:
    """
    Build the full structured syllabus output containing course metadata,
    modules with topics, raw text, and embedding-ready text.

    Args:
        text: Raw syllabus text (for course title/code extraction).
        modules: Dict mapping module names to topic lists.

    Returns:
        Structured dict with course_title, course_code, and modules.
    """
    course_title = extract_course_title(text)
    course_code = extract_course_code(text)

    structured_modules = {}
    for module_name, topics in modules.items():
        raw_text = ", ".join(topics)
        embedding_ready = build_embedding_ready_text(topics)
        structured_modules[module_name] = {
            "raw_text": raw_text,
            "topics": [t.strip().title() for t in topics],
            "embedding_ready_text": embedding_ready,
        }

    return {
        "course_title": course_title,
        "course_code": course_code,
        "modules": structured_modules,
    }
