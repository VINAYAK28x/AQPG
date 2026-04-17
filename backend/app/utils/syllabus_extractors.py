"""
Syllabus metadata extractors — course title, code, and outcomes.

Extracted from syllabus_service.py to keep the service file focused on
module parsing and structured output assembly.
"""

import re
import logging
from typing import List

logger = logging.getLogger(__name__)


# =====================================================
# Course Title Extraction
# =====================================================

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

    # Pattern 2b: Line starting with a course code followed by all-caps title
    # e.g. "19-202-0504 OPERATING SYSTEM" or "CS301 DATA STRUCTURES"
    for line in lines[:20]:
        line = line.strip()
        if len(line) < 10:
            continue
        m = re.match(
            r"^(?:[A-Z]{0,4}\s*)?(\d{2}[\-]\d{3}[\-]\d{4}|\d{2}[A-Z]{2,4}\d{3,4}|[A-Z]{2,4}[\-]?\d{3,4})\s+(.+)$",
            line
        )
        if m:
            title_part = m.group(2).strip()
            # Must be mostly alphabetic and look like a title
            alpha_chars = sum(1 for c in title_part if c.isalpha())
            if alpha_chars > 5 and title_part == title_part.upper():
                return _clean_title(title_part)

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


# =====================================================
# Course Code Extraction
# =====================================================

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


# =====================================================
# Course Outcomes Extraction
# =====================================================

def extract_course_outcomes(text: str) -> List[str]:
    """
    Extract course outcomes from the raw syllabus text.

    Handles multiple formats:
    - Numbered lists:  ``1.  Familiarize with …``
    - CO-prefix:       ``CO1:  Design a minimized …``
    - Bullet points:   ``•  Design a minimized …``
    - Plain sentences after "On completion … able to:"

    Stops when it hits a Module heading, References, or a blank-line gap
    after collecting at least one outcome.
    """
    lines = text.split("\n")
    outcomes: List[str] = []
    in_outcomes_section = False
    # Track intro line ("On completion...") so we skip it
    saw_intro = False
    blank_count = 0

    for line in lines:
        stripped = line.strip()

        lower_line = stripped.lower()

        # ---- Detect start of the section ----
        if not in_outcomes_section:
            if "course outcome" in lower_line:
                in_outcomes_section = True
            continue

        # ---- We are inside Course Outcomes now ----

        # Skip the intro sentence ("On completion of this course …")
        if not saw_intro and ("on completion" in lower_line or "will be able to" in lower_line):
            saw_intro = True
            continue

        # Handle blank lines – allow 1; 2 consecutive blanks → end section
        if not stripped:
            blank_count += 1
            if blank_count >= 2 and outcomes:
                break
            continue
        blank_count = 0

        # ---- Stop markers ----
        if re.match(r"^module\s+[ivx0-9]+", lower_line, re.IGNORECASE):
            break
        if lower_line.startswith("references"):
            break
        if lower_line.startswith("textbook"):
            break

        # ---- Capture patterns ----
        # Pattern A: numbered list  "1. Familiarize …" / "1) Familiarize …"
        m_num = re.match(r"^(\d+)\s*[.)]\s*(.+)", stripped)
        # Pattern B: CO-prefix  "CO1: …" / "CO 1 - …"
        m_co = re.match(r"^CO\s*(\d+)\s*[:\-.)]\s*(.+)", stripped, re.IGNORECASE)

        if m_co:
            idx = m_co.group(1)
            body = m_co.group(2).strip()
            outcomes.append(f"CO{idx}:  {body}")
        elif m_num:
            idx = m_num.group(1)
            body = m_num.group(2).strip()
            outcomes.append(f"CO{idx}:  {body}")
        elif re.match(r"^[•\-\*]\s+", stripped):
            # Bullet point without a number
            body = re.sub(r"^[•\-\*]\s+", "", stripped)
            outcomes.append(f"CO{len(outcomes)+1}:  {body}")
        elif outcomes:
            prev = outcomes[-1]
            prev_ends_sentence = prev.rstrip().endswith(".")
            starts_with_cap = stripped[0].isupper() if stripped else False
            looks_like_new_sentence = prev_ends_sentence and starts_with_cap and len(stripped) > 15

            if looks_like_new_sentence:
                # Previous CO ended with period, this starts a new sentence → new CO
                outcomes.append(f"CO{len(outcomes)+1}:  {stripped}")
            elif len(stripped) > 10 and not stripped.isupper():
                # Genuine continuation of a wrapped line
                outcomes[-1] = f"{prev} {stripped}"

    return outcomes
