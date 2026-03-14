# Backend — Services Layer (`backend/app/services/`)

> **For developers & agents:** This document describes the `services/` directory — the core business logic layer containing all NLP processing, ML model inference, and question generation.

---

## Directory Overview

```
backend/app/services/
├── __init__.py            # Package init (empty)
├── syllabus_service.py    # Syllabus PDF parsing → module-wise topics
├── ingestion_service.py   # PDF text extraction with OCR fallback
├── chunking_service.py    # Text chunking with page metadata
├── mapping_service.py     # SBERT semantic topic–chunk mapping
├── question_service.py    # Flan-T5 question generation (+template fallback)
└── bloom_service.py       # Bloom's taxonomy classification
```

---

## `__init__.py`

Empty package initializer.

---

## `syllabus_service.py`

Parses uploaded syllabus PDFs to produce a structured `Dict[module_name, List[topic]]` mapping.

### Functions

#### `extract_syllabus_text(pdf_bytes: bytes) → str`
Thin wrapper around `ingestion_service.extract_text()`. Returns raw text from the syllabus PDF.

#### `extract_module_topics(text: str) → Dict[str, List[str]]`
Parses raw syllabus text into module-wise topic lists.

**Algorithm:**
1. Iterates lines looking for module headings (`Module I`, `Module 1`, etc.) using regex `r"Module\s+([IVX0-9]+|[0-9]+)"`.
2. Under each heading, splits lines on delimiters (`. , ; -`) to extract individual topics.
3. Filters out noise lines containing keywords like `"course outcome"`, `"textbook"`, `"marks"`, etc.
4. Stops parsing at `"references"` section.
5. **Fallback:** If no module headings are found, groups all topics under `"General Topics"`.

**Minimum topic length:** 5 characters (shorter strings are discarded).

**Dependencies:** `ingestion_service.extract_text`

---

## `ingestion_service.py`

Handles PDF text extraction with a two-tier strategy: fast native extraction first, OCR fallback second.

### Functions

#### `extract_text(pdf_bytes: bytes) → str`
Primary text extraction entry point.
1. Tries `pdf_utils.extract_full_text()` (PyMuPDF — fast, zero-dependency).
2. Validates result via `pdf_utils.is_valid_extracted_text()`.
3. If validation fails (low quality/insufficient text), falls back to `_ocr_extract()`.

#### `extract_pages(pdf_bytes: bytes) → List[Tuple[int, str]]`
Extracts text page-by-page with page number metadata. Delegates to `pdf_utils.extract_text_by_page()`.

#### `_ocr_extract(pdf_bytes: bytes) → str`  *(private)*
OCR fallback using Tesseract + pdf2image.
- Converts PDF to images at 200 DPI.
- Runs `pytesseract.image_to_string()` on each page.
- Handles `ImportError` (pytesseract/pdf2image not installed) gracefully — returns raw PyMuPDF text instead.

**Dependencies:** `pdf_utils`, `app.core.config` (TESSERACT_CMD, POPPLER_PATH)

---

## `chunking_service.py`

Splits extracted textbook text into fixed-size word chunks, preserving page number metadata.

### Functions

#### `chunk_text_by_page(pages_text, chunk_size=200, min_length=50) → List[Dict]`

| Parameter | Type | Default | Source |
|-----------|------|---------|--------|
| `pages_text` | `List[Tuple[int, str]]` | required | From `ingestion_service.extract_pages()` |
| `chunk_size` | `int` | `CHUNK_SIZE_WORDS` (200) | `config.py` |
| `min_length` | `int` | `MIN_CHUNK_LENGTH` (50) | `config.py` |

**Output:** List of dicts:
```python
{
    "chunk_id": 1,    # Sequential, 1-based
    "page": 3,        # Source page number
    "text": "..."     # Chunk text (≈200 words)
}
```

**Algorithm:** Simple sliding window — splits each page's text by whitespace, groups into `chunk_size`-word segments. Chunks shorter than `min_length` characters are discarded.

---

## `mapping_service.py`

The SBERT-powered semantic mapping engine. This is the core ML component.

### Class: `MappingService`

**Singleton instance:** `mapping_service` (module-level, shared across all requests).

#### `model` (property, lazy-loaded)
Loads the SBERT model on first access:
1. Checks `SBERT_MODEL_PATH` for a local custom model.
2. Falls back to `SBERT_FALLBACK_MODEL` (`all-MiniLM-L6-v2`) from HuggingFace if not found.

#### `map_modules_to_chunks(structured_syllabus, chunks, ...) → Dict[str, Any]`

Maps entire modules to the most semantically relevant textbook chunks, rather than mapping individual topics separately.

| Parameter | Default (from config) | Purpose |
|-----------|----------------------|---------|
| `similarity_threshold` | `0.45` | Minimum cosine similarity to consider a match |
| `diversity_threshold` | `0.85` | Max inter-chunk similarity for diversity filtering |
| `max_chunks_per_module` | `18` | Max chunks per module (3x per topic) |
| `dedup_threshold` | `0.92` | Similarity above this is considered duplicate content |

**Algorithm:**
1. SBERT encodes all module topics and all chunk texts. Computes a mean embedding for each module.
2. Computes full similarity matrix (modules × chunks).
3. For each module:
   - Filters candidates by `similarity_threshold` (fallback: top 3 if none pass).
   - Sorts candidates by score descending.
   - Applies **diversity-aware selection**: added only if cosine similarity to previous chunks < `diversity_threshold`.
   - **Deduplication**: Runs `_deduplicate_chunks()` to remove near-identical sentences among selected chunks.
4. Generates a cleaned `embedding_ready_text` from the unique chunks for full-scale search and AI context ingestion.

---

## `question_service.py`

Generates exam questions using a fine-tuned Flan-T5 model (with template fallback).

### Class: `QuestionService`

**Singleton instance:** `question_service` (module-level).

#### Model Loading: `_load_model()` *(private)*
- Attempts to load Flan-T5 from `FLAN_T5_MODEL_PATH` / `FLAN_T5_FALLBACK_MODEL`.

#### `generate_questions_from_pattern(exam_pattern, processed_data_dir) → Dict[str, List[Dict]]`
1. Loads mapping and chunks.
2. Calls `_generate_single_question()`.

#### `_generate_single_question(...)` *(private)*
1. Retrieves relevant text via `_get_relevant_chunks()`.
2. Picks random topic via `_get_random_topic()`.
3. If Flan-T5 loaded → `_generate_with_t5()`.
4. **Internal Choice (OR):** If `has_internal_choice` is true, recursively generates a second question based on the `or_choice` config and embeds it as `or_question`.

#### `_generate_with_t5(topic, context, marks) → str` *(private)*
Generates questions using Flan-T5. 
- Prompt complexity scales based on marks (≤2: short, ≤5: medium, >5: long complex form).
- Generation settings: `max_new_tokens` (80/160/250 based on marks), `temperature=0.8`, `repetition_penalty=1.2`, `no_repeat_ngram_size=3`.
- **Post-processing:** Aggressively strips instruction bleed (e.g., "Provide a clear and concise..."). Adds punctuation fallback if the sentence got cut off.

#### `_normalize_module_name(name: str) → str` *(private static)*
Key fix for context bleeding. Normalizes both "Module 1" (Arabic) and "Module I" (Roman) into a robust canonical `module_1` format to ensure exact matching between frontend selections and syllabus mapping keys.

---

## `bloom_service.py`

Classifies generated questions into Bloom's taxonomy levels using a custom-trained DistilBERT model.

### Class: `BloomClassifierService`

**Singleton instance:** `bloom_service` (module-level). Auto-discovers the DistilBERT model relative to the project root (`models/blooms_classifier/kaggle/working/blooms_classifier`).

#### `classify(question_text: str) → str`
Returns one of: `"Remember"`, `"Understand"`, `"Apply"`, `"Analyze"`, `"Evaluate"`, `"Create"`.

#### `_classify_with_model(question_text) → str` *(private)*
Uses the DistilBERT model. Maps generic `LABEL_0`-`LABEL_5` outputs to proper Bloom's levels via `LABEL_INDEX_MAP`.

#### `_classify_with_keywords(question_text) → str` *(private)*
Fallback heuristic if model loading fails. Checks keywords from Create down to Remember.

---

## Service Dependencies Graph

```
syllabus_service
└── ingestion_service → pdf_utils

chunking_service
└── config (CHUNK_SIZE_WORDS, MIN_CHUNK_LENGTH)

mapping_service
├── config (SBERT_MODEL_PATH, thresholds)
└── sentence_transformers, sklearn

question_service
├── config (FLAN_T5_MODEL_PATH, PROCESSED_DATA_DIR)
└── transformers (AutoTokenizer, AutoModelForSeq2SeqLM)

bloom_service
└── transformers (pipeline) [optional]
```

---

## Agent Notes

- **Lazy loading:** All ML models (SBERT, Flan-T5, Bloom classifier) use lazy loading with load-once semantics. First request will be slow; subsequent requests are fast.
- **Singletons:** `mapping_service`, `question_service`, and `bloom_service` are module-level singletons shared across all requests.
- **Randomness:** `question_service` uses `random.choice()` for topic and chunk selection, so generated questions are non-deterministic.
- **No GPU required:** All models run on CPU by default.
- **Template fallback is robust:** If any ML model fails to load, the system degrades gracefully to template-based question generation and keyword-based Bloom's classification.
