"""
Syllabus Service — parse syllabus PDFs to extract module-wise topics.

Responsibility:
- Delegate metadata extraction (title, code, outcomes) to utils.
- Extract text from syllabus PDFs using ingestion service.
- Parse module headings and run semantic topic extraction via Mistral.
- Return structured module → topics mapping.
"""

import re
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.services.ingestion_service import extract_syllabus_raw
from app.core.config import OLLAMA_BASE_URL, LLM_MODEL

from app.utils.syllabus_extractors import (
    extract_course_title,
    extract_course_code,
    extract_course_outcomes
)

logger = logging.getLogger(__name__)


def extract_syllabus_text(pdf_bytes: bytes) -> str:
    """Extract text content from a syllabus PDF."""
    text = extract_syllabus_raw(pdf_bytes)
    logger.debug(f"Syllabus text length: {len(text)}")
    return text


# =====================================================
# Semantic Topic Extraction via Mistral
# =====================================================

class SyllabusTopicsList(BaseModel):
    topics: List[str] = Field(description="List of substantive technical topics extracted from the module")


def _extract_topics_from_module_text(module_text: str) -> List[str]:
    """Semantic extraction of topics using a local Mistral model via Ollama."""
    try:
        llm = ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=LLM_MODEL,
            temperature=0.0
        )
        parser = JsonOutputParser(pydantic_object=SyllabusTopicsList)
        prompt = PromptTemplate(
            template="""You are an expert academic taxonomy parser parsing a university syllabus.
Your task is to extract a clean, substantive list of topics from the provided raw text for a single syllabus module.

Rules:
1. Preserve technical terms and hyphenated names (e.g. keep "Diffie-Hellman" and "SHA-1" and "Secure e-mail" intact).
2. If a topic is listed as a sub-attribute (like "Characteristics", "Advantages", "Technical Description") of a parent technology, prefix it with the parent name (e.g. "Fingerprint Scanner Characteristics" instead of just "Characteristics").
3. Omit any administrative noise (e.g. "course outcomes", "12 marks", "students will learn").
4. Formulate the topics perfectly capitalized and ready to be used as embeddings for semantic search.
5. Return the result strictly in valid JSON matching the format instructions.

Format Instructions:
{format_instructions}

Raw Module Text:
"{text}"
""",
            input_variables=["text"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | llm | parser

        logger.info("[Semantic Extractor] Initiating LLM syllabus parsing...")
        result = chain.invoke({"text": module_text})
        
        extracted_topics = []
        if isinstance(result, dict):
            extracted_topics = result.get("topics", [])
        elif isinstance(result, list):
            extracted_topics = result
        else:
            logger.warning(f"[Semantic Extractor] Unexpected response type: {type(result)}")
            
        logger.info(f"[Semantic Extractor] Successfully extracted {len(extracted_topics)} topics")
        return extracted_topics

    except Exception as e:
        logger.error(f"[Semantic Extractor] LLM generation failed: {e}")
        logger.warning("[Semantic Extractor] Falling back to returning full module block.")
        return [module_text.strip()]


def extract_module_topics(text: str) -> Dict[str, List[str]]:
    """Parse syllabus text to extract module-wise topics with context-aware parent-prefix grouping."""
    ignore_keywords = [
        "course outcome", "course outcomes", "edition",
        "publisher", "textbook", "syllabus", "marks",
        "on completion", "student will be able",
    ]

    lines = text.split("\n")
    logger.debug(f"Total syllabus lines: {len(lines)}")

    module_lines: Dict[str, List[str]] = {}
    current_module: Optional[str] = None

    for line in lines:
        line = line.strip()

        if line.lower().startswith("references"):
            logger.debug("Stopped parsing at References")
            break

        match = re.match(r"Module\s+([IVX0-9]+|[0-9]+)", line, re.IGNORECASE)
        if match:
            current_module = f"Module {match.group(1)}"
            module_lines[current_module] = []
            logger.debug(f"Found module: {current_module}")
            remainder = line[match.end():].strip()
            if remainder and len(remainder) > 5:
                module_lines[current_module].append(remainder)
            continue

        if not current_module or len(line) < 5:
            continue

        lower_line = line.lower()
        if any(kw in lower_line for kw in ignore_keywords):
            continue

        module_lines[current_module].append(line)

    modules: Dict[str, List[str]] = {}

    for module_name, raw_lines in module_lines.items():
        full_text = " ".join(raw_lines)
        topics = _extract_topics_from_module_text(full_text)
        modules[module_name] = [t for t in topics if len(t.strip()) > 3]

    if not modules:
        logger.warning("No explicit module headings found. Using generic topic grouping.")
        all_lines = []
        for line in lines:
            line = line.strip()
            if line.lower().startswith("references"):
                break
            if len(line) < 5:
                continue
            lower_line = line.lower()
            if any(kw in lower_line for kw in ignore_keywords):
                continue
            all_lines.append(line)
        full_text = " ".join(all_lines)
        topics = _extract_topics_from_module_text(full_text)
        modules["General Topics"] = [t for t in topics if len(t.strip()) > 3]

    logger.debug(f"Extracted {len(modules)} modules")
    return modules


def build_embedding_ready_text(topics: List[str]) -> str:
    """Create a cleaned, normalized text string from topics for semantic search."""
    combined = " ".join(topics)
    combined = re.sub(r"[^\w\s]", " ", combined)
    combined = re.sub(r"\s+", " ", combined).strip()
    return combined.title()


def build_structured_syllabus(text: str, modules: Dict[str, List[str]]) -> Dict:
    """Build the full structured syllabus output containing course metadata, modules with topics."""
    course_title = extract_course_title(text)
    course_code = extract_course_code(text)
    course_outcomes = extract_course_outcomes(text)

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
        "course_outcomes": course_outcomes,
        "modules": structured_modules,
    }
