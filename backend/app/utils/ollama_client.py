"""
Ollama API client — standalone HTTP caller for local LLM inference.

Extracted from question_service.py to isolate network I/O from business logic.
"""

import json
import re
import logging
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"


def ollama_generate(
    prompt: str,
    options: dict,
    timeout_s: int = 60,
    model: str = "mistral",
) -> str:
    """Send a prompt to the local Ollama server and return the raw response text."""
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": options,
    }

    req = urllib.request.Request(
        OLLAMA_GENERATE_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as response:
        result_data = json.loads(response.read().decode("utf-8"))
        return result_data.get("response", "")


def extract_generated_question(full_output: str) -> str:
    """Strip the prompt echo from Mistral output.
    Handles both [INST]...[/INST] format and Alpaca ### Response: format.
    """
    # Alpaca format: the response comes after ### Response:
    if "### Response:" in full_output:
        return full_output.split("### Response:")[-1].strip()
    # Legacy [INST] format
    if "[/INST]" in full_output:
        return full_output.split("[/INST]")[-1].strip()
    return full_output.strip()


def refine_with_ollama(question: str, marks: int, topic: str = "", extract_topic_tokens_fn=None) -> str:
    """
    Send the generated question to the local Ollama mistral model to polish it into
    a strict, mark-aware university exam format. The original topic name is provided
    so Mistral can correct any garbled proper nouns from T5.
    """
    try:
        # Topic anchoring instruction
        topic_anchor = ""
        if topic:
            topic_anchor = (
                f"\nIMPORTANT: The correct topic name is '{topic}'. "
                f"If the draft contains a misspelling or garbled version of this topic name, "
                f"fix it to use exactly '{topic}'.\n"
            )

        if marks <= 3:
            style_guide = (
                "Keep the question very short, direct, and specific to the draft topic. "
                "Preserve the technical scope of the draft instead of broadening it into a generic theory question. "
                "Prefer one focused ask. Avoid filler phrases such as 'importance', 'real-world applications', "
                "'where appropriate', or 'with suitable examples' unless the draft already requires them."
            )
        else:
            style_guide = (
                "Make the question sound like it was written naturally by a human professor while keeping the exact "
                "technical focus of the draft. Vary sentence structure without changing the core concept being tested. "
                "Avoid generic expansions such as applications, advantages, limitations, or examples unless they are "
                "already implied by the draft. Use plain academic English and keep the question focused."
            )

        prompt = (
            f"You are an engineering professor finalizing an exam. Rewrite the following draft question into a natural, human-sounding exam question for a {marks}-mark allocation.\n\n"
            f"{topic_anchor}"
            f"STYLE RULES:\n"
            f"{style_guide}\n\n"
            f"Preserve technical terms from the draft. Do not introduce concepts from unrelated subjects.\n"
            f"DO NOT include any introductory text, conversational parts, or meta-commentary like 'Here is the question'. "
            f"Output ONLY the refined question text.\n\n"
            f"Draft: {question}\n\nFinal Question:"
        )

        data = {
            "model": "mistral",
            "prompt": prompt,
            "system": "You are a human engineering professor writing varied, practical exam questions. You avoid repetitive, robotic templates and never use flowery vocabulary.",
            "stream": False,
            "options": {
                "temperature": 0.45
            }
        }

        req = urllib.request.Request(
            OLLAMA_GENERATE_URL, data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        # Using 60s timeout to accommodate longer inference on lower-spec hardware
        with urllib.request.urlopen(req, timeout=60) as response:
            result_data = json.loads(response.read().decode("utf-8"))
            refined = result_data.get("response", "").strip()
            # Clean up occasional hallucinated prefixes from Mistral
            refined = re.sub(r"^(Question|Output|Refined Question|Draft Question|Final Question)[\s]*:[\s]*", "", refined, flags=re.IGNORECASE).strip()
            # Strip wrapping quotes that Mistral occasionally adds
            refined = refined.strip('"').strip("'")
            refined = re.sub(r"\s+", " ", refined).strip()
            if "?" in refined:
                refined = refined[: refined.index("?") + 1].strip()
            if refined and not refined.endswith("?"):
                refined = refined.rstrip(".") + "?"
            if topic and extract_topic_tokens_fn:
                topic_tokens = extract_topic_tokens_fn(topic)
                refined_lower = refined.lower()
                if topic_tokens and not any(token in refined_lower for token in topic_tokens):
                    return question
            if refined:
                logger.info(f"\n[Mistral] Original: {question}\n[Mistral] Refined : {refined}\n")
                return refined
    except urllib.error.URLError as e:
        logger.warning(f"Ollama refinement failed (is Ollama running?): {e}")
    except Exception as e:
        logger.error(f"Unexpected error during Ollama refinement: {e}")

    # Fall back to the original question if Ollama fails
    return question
