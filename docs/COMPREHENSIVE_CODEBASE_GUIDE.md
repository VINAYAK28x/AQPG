# AQPG Comprehensive Codebase Guide

This document is the one-shot, end-to-end guide to the AQPG codebase.

It is written to answer four questions clearly:

1. What the system does.
2. How data flows through it from upload to generated paper.
3. What each major model/library does and why it is present.
4. What every important source file and function is responsible for.

This guide focuses on the real, current code in the repository. It does not describe `frontend/node_modules/`, `frontend/build/`, or Python `__pycache__` files because those are generated/vendor artifacts rather than authored application code.

---

## 1. What This System Is

AQPG stands for Automated Question Paper Generation.

At a high level, the system:

1. Accepts a syllabus PDF.
2. Extracts structured modules and topics from that syllabus.
3. Accepts a textbook PDF.
4. Extracts and chunks textbook content.
5. Semantically maps syllabus topics to textbook chunks.
6. Lets the user configure an exam pattern.
7. Generates questions using local ML/LLM components.
8. Classifies the generated questions by Bloom’s taxonomy.
9. Displays the final paper in the frontend and allows per-question regeneration.

The system is designed to run locally rather than relying on hosted LLM APIs.

---

## 2. Big-Picture Architecture

The project has two main applications:

- `backend/`: FastAPI service that handles PDF processing, semantic mapping, question generation, and Bloom classification.
- `frontend/`: React single-page app that guides the user through the workflow.

It also has supporting assets:

- `processed_data/`: runtime artifacts produced by the pipeline.
- `models/`: local model directories if present.
- `pyq_dataset.jsonl`: prior-year-question style/examples used by the high-mark generation pipeline.
- `docs/`: engineering documentation.

### End-to-end flow

```text
Syllabus PDF
  -> backend/app/api/syllabus.py
  -> ingestion_service + syllabus_service
  -> processed_data/syllabus_topics.json

Textbook PDF
  -> backend/app/api/textbook.py
  -> ingestion_service + chunking_service + image_utils
  -> processed_data/textbook_chunks.json

Selected topics
  -> backend/app/api/mapping.py
  -> mapping_service (SBERT)
  -> processed_data/selected_topics.json
  -> processed_data/topic_chunk_mapping.json

Exam pattern
  -> backend/app/api/questions.py
  -> question_service
  -> bloom_service
  -> processed_data/generated_questions.json

Frontend
  -> renders results
  -> allows regeneration of individual questions
```

---

## 3. ML / NLP / LLM Stack Explained

This project uses several different model families. They solve different problems.

### 3.1 Flan-T5

Used in: `backend/app/services/question_service.py`

Role:
- Main local text-to-text model for low-mark question drafting.
- Generates concise questions from topic + context prompts.

Why it exists:
- T5-style models are good at prompt-based transformation tasks.
- It is lighter than running a large instruction model for every question.

How this codebase uses it:
- Loads a custom local model if present at `FLAN_T5_MODEL_PATH`.
- Falls back to Hugging Face model `google/flan-t5-small`.
- Used mainly for `<= 5` mark questions and as part of fallback flows.

Important limitation:
- For higher-mark questions, T5 tends to drift into generic or hallucinated patterns, which is why the code now routes `> 5` mark generation through a different path.

### 3.2 SBERT

Used in:
- `backend/app/services/mapping_service.py`
- `backend/app/services/question_service.py`

Role:
- Semantic similarity model.
- Converts text into embeddings so the system can compare meaning, not just keywords.

Why it exists:
- Syllabus topics and textbook chunks rarely match word-for-word.
- SBERT allows “topic X” to find the most semantically related textbook passages.

How this codebase uses it:
- Main topic-to-chunk mapping engine.
- Also used inside high-mark question generation for:
  - context compression relevance scoring,
  - few-shot prior-question retrieval,
  - semantic validation/coherence checks.

Fallback model:
- `all-MiniLM-L6-v2` if no custom local SBERT model is present.

### 3.3 DistilBERT / Transformers Classification Pipeline

Used in: `backend/app/services/bloom_service.py`

Role:
- Classifies generated questions into Bloom’s taxonomy categories:
  `Remember`, `Understand`, `Apply`, `Analyze`, `Evaluate`, `Create`.

Why it exists:
- Generation alone does not guarantee the intended cognitive level.
- The backend annotates each question with a classified Bloom level for visibility and validation.

Fallback behavior:
- If no trained classifier is available, the service uses keyword heuristics.

### 3.4 Mistral via Ollama

Used in:
- `backend/app/services/syllabus_service.py`
- `backend/app/services/question_service.py`

Role:
- Local instruction-following LLM accessed over HTTP through Ollama.

Why it exists:
- The project needs a stronger instruction model than T5 for:
  - structured syllabus topic extraction,
  - high-mark question generation,
  - final polishing/refinement of drafted questions.

Why Ollama is used instead of loading Mistral directly in PyTorch:
- Lower operational complexity in this repo.
- Avoids the memory burden of loading another large model into the Python process.
- Keeps the backend as an orchestrator while Ollama hosts the model.

Where it is used:
- `syllabus_service.py`: extracts clean topic lists from module text using `ChatOllama`.
- `question_service.py`: uses direct HTTP calls to `http://localhost:11434/api/generate` for high-mark question generation and rewriting/refinement.

### 3.5 LangChain

Used in:
- `backend/app/services/chunking_service.py`
- `backend/app/services/syllabus_service.py`

Role in this repo:
- Not used as a full agent framework.
- Used selectively as utility infrastructure.

Specifically:
- `RecursiveCharacterTextSplitter` from `langchain_text_splitters` splits textbook pages into chunk-sized pieces while preserving readable boundaries.
- `PromptTemplate` and `JsonOutputParser` help structure the syllabus-extraction prompt/response flow with `ChatOllama`.

Important point:
- LangChain here is a helper library, not the system’s core architecture.

### 3.6 OCR Tooling

Used in: `backend/app/services/ingestion_service.py`

Components:
- `pytesseract`
- `pdf2image`
- `Tesseract`
- `Poppler` on Windows

Role:
- Fallback extraction path for scanned PDFs or image-based documents where PyMuPDF cannot recover valid text.

### 3.7 PyMuPDF

Used in:
- `backend/app/utils/pdf_utils.py`
- `backend/app/utils/image_utils.py`

Role:
- Fast native PDF text extraction.
- Page-level text extraction.
- Embedded image extraction.

This is the first-line PDF parser before OCR fallback.

### 3.8 scikit-learn

Used in:
- `mapping_service.py`
- `question_service.py`

Role:
- Mainly for cosine similarity computations during semantic matching and validation.

### 3.9 spaCy

Used in: `question_service.py`

Role:
- Named-entity check in question validation.
- Used to detect “alien” entities that do not appear in the source context.

### 3.10 BM25 / NLTK

Used in: `question_service.py`

Role:
- BM25 helps re-rank chunks by lexical relevance during context compression.
- NLTK sentence tokenization helps build compact, sentence-level context summaries for high-mark generation.

---

## 4. Runtime Data Files and Their Meaning

Generated under `processed_data/`:

- `syllabus_topics.json`
  - structured syllabus extraction result.
- `selected_topics.json`
  - syllabus filtered down to only the topics chosen in the frontend.
- `textbook_chunks.json`
  - processed textbook chunk inventory with page metadata and attached images.
- `topic_chunk_mapping.json`
  - SBERT mapping output that links topics/modules to relevant chunks.
- `question_pattern.json`
  - flattened record of the configured exam pattern.
- `generated_questions.json`
  - final generated paper returned by the backend.
- `images/`
  - extracted PDF images.
- `cache/`
  - SBERT embedding caches.

These files make the pipeline stateful across steps without requiring a database.

---

## 5. Root-Level Important Files

### `README.md`

Purpose:
- Basic project intro and setup instructions.

Current state:
- Useful for initial setup, but high level and slightly behind the latest codebase behavior.

### `requirements.txt`

Purpose:
- Python dependency list for the backend.

Important packages:
- `fastapi`, `uvicorn`, `pydantic`, `python-multipart`
- `PyMuPDF`
- `sentence-transformers`, `transformers`, `torch`, `scikit-learn`
- `nltk`, `rank_bm25`, `spacy`
- `langchain-text-splitters`
- `pytesseract`, `pdf2image`, `Pillow`

### `frontend/package.json`

Purpose:
- Frontend dependency and script manifest.

Important packages:
- `react`
- `react-dom`
- `react-scripts`

### `pyq_dataset.jsonl`

Purpose:
- Prior-year-question style corpus used by the high-mark generator.

Why it matters:
- The high-mark pipeline uses it for style grounding and exemplar retrieval.

### `implementation_plan.md`

Purpose:
- Historical planning note for migrating the 12-mark generation path.

### `12mark_generation_fix.md`

Purpose:
- Design note/spec for the high-mark generation fix.

These two markdown files are reference/history documents, not runtime code.

---

## 6. Backend Codebase: File-by-File and Function-by-Function

## 6.1 `backend/main.py`

Purpose:
- Minimal backend entrypoint.

What it contains:
- Imports `create_app` from `app.factory`.
- Instantiates the FastAPI app.
- Supports direct `python main.py` launch.

Functions / objects:
- `app`
  - The FastAPI application instance created by `create_app()`.

Why it exists:
- Keeps entrypoint logic thin and pushes app construction into a factory.

---

## 6.2 `backend/app/factory.py`

Purpose:
- Central FastAPI application assembly.

Main function:
- `create_app() -> FastAPI`
  - Builds the app.
  - Configures CORS.
  - Registers routers.
  - Adds a root health-check route.

Key imports:
- `CORS_ORIGINS` from config.
- Routers from `app.api`.

Why it matters:
- This is the backend’s composition root.

---

## 6.3 `backend/app/core/config.py`

Purpose:
- Centralized constants and paths.

What it defines:
- project paths:
  - `PROJECT_ROOT`
  - `BACKEND_ROOT`
  - `PROCESSED_DATA_DIR`
- model paths:
  - `SBERT_MODEL_PATH`
  - `FLAN_T5_MODEL_PATH`
  - `SBERT_FALLBACK_MODEL`
  - `FLAN_T5_FALLBACK_MODEL`
- Ollama settings:
  - `OLLAMA_BASE_URL`
  - `LLM_MODEL`
- mapping thresholds:
  - `SIMILARITY_THRESHOLD`
  - `DIVERSITY_THRESHOLD`
  - `MAX_CHUNKS_PER_TOPIC`
- chunking constants:
  - `CHUNK_SIZE_CHARS`
  - `CHUNK_OVERLAP_CHARS`
  - `MIN_CHUNK_LENGTH`
- frontend access control:
  - `CORS_ORIGINS`
- OCR platform settings:
  - `TESSERACT_CMD`
  - `POPPLER_PATH`

Why it matters:
- This is where operational tuning happens.

---

## 6.4 `backend/app/models/schemas.py`

Purpose:
- Request/response shape definitions used by the question-generation APIs.

Classes:

- `SubQuestionPattern`
  - fields:
    - `label`
    - `marks`
  - meaning:
    - describes one sub-question such as `(a)` or `(b)`.

- `OrChoicePattern`
  - fields:
    - `marks`
    - `module`
    - `sub_questions`
  - meaning:
    - defines the alternate `OR` branch of a main question.

- `QuestionPattern`
  - fields:
    - `question_no`
    - `marks`
    - `module`
    - `has_internal_choice`
    - `or_choice`
    - `sub_questions`
  - meaning:
    - describes one question slot in the exam pattern.

- `PartPattern`
  - fields:
    - `part_name`
    - `answer_type`
    - `marks_per_question`
    - `total_questions`
    - `questions_to_answer`
    - `questions`
  - meaning:
    - describes a section like `PART A` or `PART B`.

- `ExamPattern`
  - fields:
    - `exam_name`
    - `parts`
  - meaning:
    - top-level paper configuration posted by the frontend.

- `RegenerateRequest`
  - fields:
    - `module`
    - `marks`
    - `question_no`
    - `sub_questions`
  - meaning:
    - used when the user regenerates a single question.

---

## 6.5 `backend/app/utils/pdf_utils.py`

Purpose:
- Low-level PDF text extraction helpers.

Functions:

- `extract_full_text(pdf_bytes: bytes) -> str`
  - extracts all text from the whole PDF.
  - used by ingestion flows.

- `extract_text_by_page(pdf_bytes: bytes) -> List[Tuple[int, str]]`
  - returns `(page_number, page_text)` pairs.
  - used by textbook chunking.

- `is_valid_extracted_text(text: str) -> bool`
  - checks whether PyMuPDF output looks like meaningful text.
  - rejects likely garbage OCR layers, repeated copyright noise, and low-diversity text.

Why it matters:
- This file decides whether the system trusts native PDF extraction or falls back to OCR.

---

## 6.6 `backend/app/utils/image_utils.py`

Purpose:
- Handles textbook image extraction and association with chunks.

Functions:

- `extract_images_from_pdf(pdf_bytes: bytes, output_dir: str) -> List[Dict[str, Any]]`
  - extracts embedded images from each PDF page.
  - saves them to disk and returns image metadata.

- `map_chunks_to_images(chunks, images) -> List[Dict[str, Any]]`
  - matches images to chunks by page number.
  - adds an `images` list to each chunk.

Why it matters:
- Even though the current question generator is text-first, the chunk structure is prepared to carry visual context.

---

## 6.7 `backend/app/services/ingestion_service.py`

Purpose:
- Main PDF ingestion logic with OCR fallback and text cleanup.

Functions:

- `clean_extracted_text(text: str) -> str`
  - textbook-oriented cleanup pass.
  - removes noise such as:
    - table-of-contents dot leaders,
    - standalone page numbers,
    - repetitive headers,
    - preface/acknowledgment noise,
    - short junk lines.
  - also merges broken lines when appropriate.

- `extract_text(pdf_bytes: bytes) -> str`
  - generic entrypoint for extracting text from a PDF.
  - tries PyMuPDF first, then OCR if needed.

- `extract_pages(pdf_bytes: bytes) -> List[Tuple[int, str]]`
  - page-by-page extraction for textbooks.
  - cleans each page individually.

- `_ocr_extract(pdf_bytes: bytes) -> str`
  - internal OCR fallback using `pdf2image` + `pytesseract`.

- `extract_syllabus_raw(pdf_bytes: bytes) -> str`
  - syllabus-specific extraction.
  - intentionally does not run the aggressive textbook cleanup because syllabus topics are often short lines that would otherwise be lost.

Why it matters:
- This service is the gatekeeper for text quality.
- Bad extraction here will degrade every later stage.

---

## 6.8 `backend/app/services/chunking_service.py`

Purpose:
- Splits textbook text into chunk objects suitable for semantic mapping and generation.

Functions:

- `technical_density(text: str) -> float`
  - estimates how “technical” a chunk is based on digits, uppercase tokens, and long words.

- `sentence_count(text: str) -> int`
  - rough sentence counter.

- `_is_quality_chunk(text: str) -> bool`
  - rejects chunks with:
    - too few sentences,
    - too little technical density.

- `chunk_text_by_page(pages_text, chunk_size, chunk_overlap, min_length) -> List[Dict[str, Any]]`
  - main chunking function.
  - uses LangChain’s `RecursiveCharacterTextSplitter`.
  - preserves page metadata.
  - applies quality filtering.

Output chunk shape:

```json
{
  "chunk_id": 1,
  "page": 12,
  "text": "...",
  "images": []
}
```

Why it matters:
- Chunk granularity strongly affects mapping quality and downstream question quality.

---

## 6.9 `backend/app/services/syllabus_service.py`

Purpose:
- Turns raw syllabus PDFs into structured course/module/topic data.

Functions:

- `extract_syllabus_text(pdf_bytes: bytes) -> str`
  - wrapper around syllabus extraction.

- `extract_course_title(text: str) -> str`
  - heuristic title extraction from syllabus text.

- `_clean_title(title: str) -> str`
  - cleans formatting and normalizes all-caps titles.

- `extract_course_code(text: str) -> str`
  - regex-based course code extraction.

- `SyllabusTopicsList`
  - Pydantic model used for structured output parsing from Mistral.

- `_extract_topics_from_module_text(module_text: str) -> List[str]`
  - uses local Mistral via `ChatOllama`.
  - prompt asks the model to:
    - preserve technical names,
    - prefix subattributes with parent topics,
    - remove syllabus noise,
    - return strict JSON.

- `extract_module_topics(text: str) -> Dict[str, List[str]]`
  - scans the syllabus for module headings.
  - groups lines by module.
  - passes each module block to `_extract_topics_from_module_text`.
  - has fallback behavior if no module headings are found.

- `build_embedding_ready_text(topics: List[str]) -> str`
  - normalizes topic text for embedding/search purposes.

- `build_structured_syllabus(text, modules) -> Dict`
  - assembles the final structured syllabus payload:
    - `course_title`
    - `course_code`
    - `modules`

Why it matters:
- This is the source of truth for topic boundaries.
- If topic extraction is poor, mapping and generation will both drift.

---

## 6.10 `backend/app/services/mapping_service.py`

Purpose:
- Semantic link builder between syllabus topics and textbook chunks.

Class:
- `MappingService`

Important members and methods:

- `__init__`
  - sets up embedding cache directory.

- `model` property
  - lazy-loads SBERT.

- `_compute_hash(texts)`
  - creates stable cache keys for embedding inputs.

- `_encode_with_cache(texts, prefix="emb")`
  - computes or loads cached embeddings from disk.

- `_cleanup_cache(prefix="emb")`
  - trims old cache files.

- `map_modules_to_chunks(structured_syllabus, chunks, similarity_threshold, diversity_threshold, chunks_per_topic, dedup_threshold)`
  - primary mapping algorithm.
  - for each topic:
    - encodes the topic,
    - compares it against all chunk embeddings,
    - filters by similarity threshold,
    - falls back to top-ranked chunks if needed,
    - applies diversity filtering,
    - deduplicates near-identical chunks.
  - returns a nested `topic_mappings` structure per module.

- `_deduplicate_chunks(indices, texts, threshold)`
  - removes semantically near-duplicate chunks among selected candidates.

- `_build_embedding_text(raw_text)`
  - cleans aggregate module text for future semantic use.

- `map_topics_to_chunks(...)`
  - legacy mapping method kept for backward compatibility.

Singleton:
- `mapping_service = MappingService()`

Why it matters:
- This service creates the context boundary that question generation depends on.

---

## 6.11 `backend/app/services/bloom_service.py`

Purpose:
- Bloom taxonomy classification layer.

Constants:
- `BLOOM_LEVELS`
- `LABEL_INDEX_MAP`
- `BLOOM_KEYWORDS`

Class:
- `BloomClassifierService`

Methods:

- `__init__(model_path=None)`
  - sets the candidate model path.

- `_load_model()`
  - loads a Hugging Face text-classification pipeline if the trained model exists.

- `classify(question_text: str) -> str`
  - classifies a single question.

- `classify_batch(question_texts: List[str]) -> List[str]`
  - batch version for performance.

- `_map_label_to_bloom(label, original_text) -> str`
  - converts raw model labels like `LABEL_3` into human-readable Bloom levels.

- `_classify_with_model(question_text: str) -> str`
  - model-backed classification path.

- `_classify_with_keywords(question_text: str) -> str`
  - heuristic fallback.

Singleton:
- `bloom_service = BloomClassifierService()`

Why it matters:
- This is not the generator.
- It is the “quality annotation / classification” layer after generation.

---

## 6.12 `backend/app/services/question_service.py`

Purpose:
- Core question generation orchestrator.

This is the most complex file in the backend.

### High-level responsibilities

- Manage question generation model state.
- Load runtime artifacts from `processed_data/`.
- Select topics and relevant chunk context.
- Route by mark band.
- Generate questions using T5, Mistral, templates, and validation loops.
- Support full-paper generation and single-question regeneration.

### Important module-level constants

- `BLOOM_VERBS`
  - expected verbs by Bloom level.
- `GENERIC_SUBJECT_NAMES`
  - prevents subject matching from overfitting on generic course names.
- `CONTEXT_STOPWORDS`
  - used when extracting useful context terms and topic tokens.

### Class: `QuestionService`

#### Initialization and cache management

- `__init__`
  - initializes model/tokenizer/cache fields.
  - warms up PYQ and spaCy dependencies best-effort.

- `clear_caches()`
  - clears cached runtime JSON structures so new uploads are picked up.

#### High-mark pipeline support

- `extract_generated_question(full_output: str) -> str`
  - trims prompt echoes from Mistral output.

- `_get_sbert_model()`
  - loads SBERT for question-service internal semantic work.

- `_get_spacy_nlp()`
  - loads spaCy model for entity validation.

- `_load_pyq_dataset()`
  - loads `pyq_dataset.jsonl`.

- `_ollama_generate(prompt, options, timeout_s=60) -> str`
  - low-level HTTP client for Ollama generation requests.

- `compress_context(chunks, topic, max_tokens=400) -> str`
  - compresses candidate context into a smaller sentence budget using SBERT + BM25 scoring.

- `_normalize_subject_name(subject)`
  - normalizes course/subject strings.

- `_mark_bucket(marks)`
  - buckets marks into short/medium/long bands for exemplar selection.

- `_extract_topic_tokens(topic)`
  - pulls meaningful tokens from topic strings.

- `_parse_pyq_metadata(row)`
  - extracts subject/module/marks/context info from a PYQ JSONL row.

- `fetch_similar_pyqs(topic, pyq_dataset, k=3, subject="", module="", marks=None)`
  - retrieves the most relevant prior questions for few-shot grounding.
  - now filters candidates progressively instead of drawing from the entire corpus blindly.

- `validate_question(question, context, marks) -> Tuple[bool, str]`
  - validates generated questions using:
    - length,
    - punctuation,
    - opening-word rules,
    - banned phrase checks,
    - spaCy entity consistency,
    - semantic coherence.

- `generate_high_mark_question(topic, chunks, marks, subject="Computer Science", module="")`
  - main `> 5` mark pipeline.
  - compresses context.
  - pulls few-shot PYQs.
  - calls Ollama.
  - validates and retries.
  - falls back if needed.

- `fallback_t5_anchor_rewrite(topic, context, marks, subject)`
  - hybrid fallback path:
    - draft with T5,
    - rewrite with Mistral,
    - validate the result.

#### T5 loading and global paper generation

- `_load_model()`
  - lazy-loads Flan-T5 model/tokenizer.
  - sets Torch CPU thread cap.

- `generate_questions_from_pattern(exam_pattern, processed_data_dir=None)`
  - top-level orchestration for full paper generation.
  - loads:
    - topic mapping,
    - textbook chunks,
    - selected or full syllabus topics.
  - iterates through all parts and question slots.

- `_resolve_course_subject(syllabus_topics)`
  - derives course subject string for prompt conditioning.

- `_generate_single_question(question, part, topic_mapping, chunks_dict, syllabus_topics, seen_topics)`
  - generates one question or sub-question block.
  - handles:
    - topic selection,
    - context retrieval,
    - OR choice generation,
    - sub-question generation.

#### Bloom-aware routing for low/high mark generation

- `_expected_bloom_for_marks(marks)`
  - heuristic expected Bloom level by mark band.

- `_refine_prompt_for_bloom(base_prompt, expected_bloom)`
  - appends Bloom guidance to prompts when retrying.

- `_generate_with_bloom_retry(topic, context, marks, module="", subject="Computer Science")`
  - routes high-mark generation to the high-mark path.
  - for low-mark questions:
    - generates,
    - classifies,
    - retries once with stronger Bloom constraints.

#### T5 drafting and output cleanup

- `_generate_with_t5(topic, context, marks, bloom_override=None)`
  - low-mark T5 generation path.
  - uses different prompt styles by mark band.
  - cleans generated text.
  - filters hallucinations.
  - optionally refines with Ollama.

- `_filter_hallucinations(text)`
  - regex-based cleanup for code/math-like garbage generations.

- `_refine_with_ollama(question, marks, topic="")`
  - final rewrite/polishing pass.
  - now designed to preserve technical scope and avoid unrelated generic expansions.

#### Template fallback and context helpers

- `_extract_context_terms(context, topic, limit=3)`
  - extracts a few useful context terms for fallback prompt generation.

- `_generate_with_template(topic, context, marks=None)`
  - last-resort fallback question generator.
  - now produces more contextual and mark-aware templates than before.

#### Module/topic/chunk utilities

- `_normalize_module_name(name)`
  - canonicalizes module names like `Module I` and `Module 1`.

- `_find_matching_key(module, keys)`
  - finds normalized matches across runtime JSONs.

- `_get_relevant_chunks(module, topic, topic_mapping, chunks_dict)`
  - retrieves only the highest-scoring mapped chunks for the topic.
  - avoids previous random adjacent-chunk expansion behavior.

- `_get_random_topic(module, syllabus_topics, exclude_topics=None)`
  - chooses a topic within a module while trying not to repeat already-used topics.

- `_load_json(filepath)`
  - simple JSON file loader.

Singleton:
- `question_service = QuestionService()`

Why it matters:
- This file is the heart of the application.

---

## 6.13 `backend/app/api/syllabus.py`

Purpose:
- API endpoint for syllabus upload and structured extraction.

Endpoint:
- `POST /extract-syllabus`

Function:
- `extract_syllabus(file: UploadFile = File(...))`
  - reads uploaded syllabus bytes,
  - extracts text,
  - extracts module topics,
  - builds structured syllabus,
  - writes `processed_data/syllabus_topics.json`,
  - clears question-service caches.

---

## 6.14 `backend/app/api/textbook.py`

Purpose:
- API endpoint for textbook upload, chunking, and image extraction.

Functions:

- `parse_page_range(page_range: str) -> Set[int]`
  - parses page-range strings like `1-5, 8, 10-20`.

- `chunk_textbook(file, page_range=None)`
  - endpoint:
    - reads textbook PDF,
    - extracts page text,
    - optionally filters to selected pages,
    - chunks text,
    - extracts images,
    - maps images to chunks,
    - saves `processed_data/textbook_chunks.json`,
    - clears caches.

Endpoint:
- `POST /chunk-textbook`

---

## 6.15 `backend/app/api/mapping.py`

Purpose:
- API endpoint for semantic mapping.

Class:
- `MappingRequest`
  - payload shape for optionally selected modules/topics.

Function:
- `semantic_mapping(request: MappingRequest = None)`
  - endpoint:
    - loads syllabus and textbook chunks,
    - optionally filters to selected topics,
    - saves `selected_topics.json`,
    - runs SBERT mapping,
    - saves `topic_chunk_mapping.json`.

Endpoint:
- `POST /semantic-mapping`

---

## 6.16 `backend/app/api/questions.py`

Purpose:
- API endpoints for pattern persistence, full generation, and regeneration.

Functions:

- `set_question_pattern(pattern: ExamPattern)`
  - endpoint:
    - flattens the configured pattern,
    - saves `question_pattern.json`.

- `generate_questions(pattern: ExamPattern)`
  - endpoint:
    - generates questions through `question_service`,
    - classifies all generated text with `bloom_service`,
    - saves `generated_questions.json`.

- `regenerate_question(req: RegenerateRequest)`
  - endpoint:
    - reconstructs a lightweight question object,
    - reuses the same service path to regenerate only one question,
    - reclassifies the result.

Endpoints:
- `POST /set-question-pattern`
- `POST /generate-questions`
- `POST /regenerate-question`

---

## 6.17 `backend/app/__init__.py`, `backend/app/api/__init__.py`, `backend/app/core/__init__.py`, `backend/app/models/__init__.py`, `backend/app/services/__init__.py`, `backend/app/utils/__init__.py`

Purpose:
- Package initializers.

Current behavior:
- No business logic.

---

## 7. Frontend Codebase: File-by-File and Component-by-Component

## 7.1 `frontend/src/index.js`

Purpose:
- React entrypoint.

Behavior:
- Mounts `<App />` into the DOM.

---

## 7.2 `frontend/src/index.css`

Purpose:
- Global CSS entry file.

Current behavior:
- Minimal; most styling lives in `App.css`.

---

## 7.3 `frontend/src/App.css`

Purpose:
- Main design system and UI styling for the whole frontend.

Contains styling for:
- cards,
- stepper,
- upload buttons,
- mapping result views,
- pattern configuration layout,
- generated paper print styles.

Why it matters:
- Most frontend polish and print output behavior lives here.

---

## 7.4 `frontend/src/App.js`

Purpose:
- Root React component and workflow coordinator.

Responsibilities:
- Owns the step state.
- Owns cross-step application state.
- Makes main API calls.
- Decides which component to render at each step.

State groups:

- Step/navigation:
  - `step`

- Syllabus/topic selection:
  - `topics`
  - `syllabusLoading`
  - `selectedTopics`

- Textbook processing:
  - `chunkCount`
  - `textbookLoading`
  - `totalPdfPages`
  - `pagesProcessed`

- Pattern configuration:
  - `examName`
  - `parts`
  - `expandedParts`
  - `patternLoading`

- Generation:
  - `generationLoading`
  - `generatedQuestions`
  - `generationError`

Derived value:
- `availableModules`
  - extracted from parsed syllabus modules.

Functions:

- `uploadSyllabus(e)`
  - posts syllabus file to `/extract-syllabus`.

- `uploadTextbook(file, pageRange)`
  - posts textbook file and optional page range to `/chunk-textbook`.

- `savePattern()`
  - posts configured exam pattern to `/set-question-pattern`.

- `generateQuestions()`
  - posts the full exam pattern to `/generate-questions`.
  - on success moves the UI to step 6.

- `defaultPattern()`
  - factory for the initial paper structure.
  - creates:
    - Part A: eight 3-mark questions.
    - Part B: four 12-mark questions with OR choices.

Step sequence:

1. Syllabus upload
2. Textbook upload
3. Topic selection
4. Semantic mapping
5. Pattern configuration
6. Generated paper

---

## 7.5 `frontend/src/components/Stepper.js`

Purpose:
- Visual progress bar for the six-step workflow.

Component:
- `Stepper({ currentStep, onStepClick })`

Behavior:
- Renders six steps.
- Supports clicking a step to jump directly.
- Marks completed steps with checkmarks.

---

## 7.6 `frontend/src/components/SyllabusUpload.js`

Purpose:
- UI for syllabus upload and display of extracted module/topic output.

Component:
- `SyllabusUpload({ topics, syllabusLoading, onUpload, onNext })`

Behavior:
- File upload button.
- Shows processing state.
- Displays:
  - course title,
  - course code,
  - module cards,
  - topic lists.
- Provides “continue” button after extraction.

---

## 7.7 `frontend/src/components/TextbookUpload.js`

Purpose:
- UI for textbook upload and optional page-range restriction.

Component:
- `TextbookUpload({ chunkCount, textbookLoading, onUpload, onNext, totalPdfPages, pagesProcessed })`

Internal state:
- `selectedFile`
- `allPages`
- `pageRange`

Functions:

- `handleFileSelect(e)`
  - stores selected file locally.

- `handleUpload()`
  - calls parent `onUpload` with file + page range.

Behavior:
- Lets the user process:
  - all pages, or
  - a custom page range.
- Shows resulting chunk count and processed-page stats.

---

## 7.8 `frontend/src/components/TopicSelection.js`

Purpose:
- Lets the user select either:
  - automatic full-syllabus processing, or
  - manual topic restriction by module.

Component:
- `TopicSelection({ topics, selectedTopics, setSelectedTopics, onNext })`

Internal state:
- `isAutomatic`

Key behavior:
- When switching to manual mode, initializes the selected topic map.
- Supports:
  - per-topic toggles,
  - select-all per module,
  - automatic mode by clearing `selectedTopics`.

Functions:

- `handleTopicToggle(modName, topicList, topic, isChecked)`
- `handleSelectAll(modName, topicList, selectAll)`

Why it matters:
- This directly controls what `selected_topics.json` contains and therefore what the mapping/generation pipeline will consider.

---

## 7.9 `frontend/src/components/SemanticMapping.js`

Purpose:
- UI to trigger and inspect semantic topic-to-chunk mapping.

Component:
- `SemanticMapping({ selectedTopics, onNext })`

Internal state:
- `loading`
- `mapping`
- `error`
- `expandedModules`

Functions:

- `toggleModule(modName)`
  - expands/collapses a module display.

- `runMapping()`
  - posts either:
    - selected topics, or
    - an empty payload for full automatic mapping
  - to `/semantic-mapping`.

Behavior:
- Displays:
  - modules mapped,
  - topics covered,
  - linked chunks,
  - per-module topic tags,
  - per-chunk similarity badges.

---

## 7.10 `frontend/src/components/PatternConfig.js`

Purpose:
- Main paper-pattern editor.

Component:
- `PatternConfig({...props})`

This is the most interaction-heavy frontend component.

Main responsibilities:
- edit exam name,
- edit parts,
- edit questions,
- edit OR choices,
- edit sub-questions,
- save/generate actions.

Important helpers:

- `updatePart(idx, field, value)`
  - mutates a part field.

- `updateQuestion(pIdx, qIdx, field, value)`
  - mutates a question field.

- `addPart()`
  - appends a new part.

- `removePart(idx)`
  - removes a part.

- `addQ(pIdx)`
  - adds a question to a part.

- `removeQ(pIdx, qIdx)`
  - removes and renumbers questions in a part.

- `toggleExpand(idx)`
  - expands/collapses part sections.

- `toggleSubQuestions(pIdx, qIdx, isOr=false)`
  - creates/removes a default sub-question split.

- `addSubQuestion(pIdx, qIdx, isOr=false)`
  - adds another sub-question entry.

- `removeSubQuestion(pIdx, qIdx, sqIdx, isOr=false)`
  - removes and relabels sub-questions.

- `updateSubQuestion(pIdx, qIdx, sqIdx, field, value, isOr=false)`
  - updates sub-question values.

Local inline subcomponent:
- `SubQuestionsConfig`
  - reusable rendering block for sub-question editing.

Key design behavior:
- Uses actual syllabus-derived modules if available.
- Supports main-question sub-questions.
- Supports OR-question sub-questions.
- Shows total-question/mark summary bar.

---

## 7.11 `frontend/src/components/GeneratedQuestions.js`

Purpose:
- Final paper display and per-question regeneration UI.

Component:
- `GeneratedQuestions({ questions, examName })`

Local state:
- `localQuestions`
  - editable copy of generated output for in-place replacement.
- `regenerating`
  - tracks which question is currently being regenerated.

Functions:

- `handleRegenerate(partName, idx, isOr = false)`
  - calls `/regenerate-question`.
  - updates either:
    - main question,
    - OR question,
    - or sub-question block content.

- `handleDownloadPDF()`
  - triggers browser print.

Behavior:
- Renders:
  - exam title,
  - parts,
  - main questions,
  - sub-questions,
  - OR blocks,
  - Bloom labels,
  - marks.
- Includes print-specific layout structure.

Why it matters:
- This is the final user-visible output surface of the entire system.

---

## 7.12 `frontend/public/index.html`

Purpose:
- HTML shell for the React app.

---

## 7.13 `frontend/public/favicon.ico`

Purpose:
- Browser tab icon.

---

## 8. Backend API Surface Summary

The frontend talks to these backend endpoints:

- `POST /extract-syllabus`
  - upload syllabus PDF and extract modules/topics.

- `POST /chunk-textbook`
  - upload textbook PDF and process chunked content.

- `POST /semantic-mapping`
  - create topic/chunk semantic mapping.

- `POST /set-question-pattern`
  - persist pattern structure.

- `POST /generate-questions`
  - generate the full question paper.

- `POST /regenerate-question`
  - regenerate one question or one sub-question group.

- `GET /`
  - root health check.

---

## 9. How a Question Is Actually Generated

This is the most important runtime path to understand.

### Step 1: The frontend submits an `ExamPattern`

Source:
- `App.js` -> `/generate-questions`

### Step 2: `questions.py` receives the pattern

It calls:
- `question_service.generate_questions_from_pattern(...)`

### Step 3: `question_service` loads the runtime pipeline state

It reads:
- `selected_topics.json` if present, otherwise `syllabus_topics.json`
- `topic_chunk_mapping.json`
- `textbook_chunks.json`

### Step 4: For each question slot, it picks a topic

Method:
- `_get_random_topic(...)`

Goal:
- keep coverage inside the chosen module,
- avoid repeating the same topic too often.

### Step 5: It fetches the most relevant chunk context

Method:
- `_get_relevant_chunks(...)`

Goal:
- constrain generation to the mapped textbook content.

### Step 6: It routes by marks

Method:
- `_generate_with_bloom_retry(...)`

Behavior:
- `<= 5` marks:
  - Flan-T5 draft path, with Bloom retry if needed.
- `> 5` marks:
  - high-mark Mistral/Ollama path.

### Step 7: It may refine the draft

Method:
- `_refine_with_ollama(...)`

Goal:
- improve phrasing while preserving technical focus.

### Step 8: It classifies the finished question

In `questions.py`:
- `bloom_service.classify_batch(...)`

The result is attached as:
- `classified_bloom_level`

---

## 10. Why the System Uses Multiple Models Instead of One

Because the tasks are different.

- PDF extraction is not the same as semantic retrieval.
- Semantic retrieval is not the same as question generation.
- Question generation is not the same as Bloom classification.
- Syllabus parsing benefits from an instruction-tuned model, while chunk mapping benefits from embedding models.

In other words, the system is deliberately modular:

- PyMuPDF / OCR for document ingestion.
- LangChain splitter for chunking mechanics.
- SBERT for retrieval and semantic matching.
- Mistral for structured extraction and high-mark LLM generation.
- Flan-T5 for low-mark drafting.
- DistilBERT/heuristics for Bloom classification.

That division of labor is one of the most important architectural ideas in this repo.

---

## 11. Important Design Choices in This Codebase

### Local-first operation

The code is built assuming local inference and local document processing.

### File-based state instead of a database

The pipeline persists intermediate artifacts as JSON in `processed_data/`.

Advantages:
- simple,
- transparent,
- easy to inspect during debugging.

Tradeoff:
- not multi-user or concurrency-optimized.

### Lazy model loading

Large models are only loaded when needed.

Advantages:
- backend boots quickly,
- avoids unnecessary memory cost.

Tradeoff:
- first request is slower.

### Service-oriented backend structure

Routers are thin.
Business logic lives in `services/`.

This makes the codebase easier to reason about.

---

## 12. Common Extension Points

If someone wants to modify the system, these are the usual places:

- Change chunking behavior:
  - `backend/app/services/chunking_service.py`

- Change syllabus parsing prompt:
  - `backend/app/services/syllabus_service.py`

- Change semantic mapping thresholds:
  - `backend/app/core/config.py`
  - `backend/app/services/mapping_service.py`

- Change question-generation behavior:
  - `backend/app/services/question_service.py`

- Change Bloom classification behavior:
  - `backend/app/services/bloom_service.py`

- Change paper-configuration UX:
  - `frontend/src/components/PatternConfig.js`

- Change final paper display/printing:
  - `frontend/src/components/GeneratedQuestions.js`
  - `frontend/src/App.css`

---

## 13. Known Conceptual Constraints

These are important for anyone reading the code.

- The system is stateful across API calls via files in `processed_data/`.
- There is no database and no user/session model.
- Random topic selection means generation is not fully deterministic.
- The quality of the final question paper depends heavily on:
  - syllabus extraction quality,
  - textbook extraction quality,
  - topic/chunk mapping quality.
- The frontend assumes a linear workflow.
- The generated paper display includes regeneration at the UI level, but regeneration still relies on the same backend pipeline state.

---

## 14. Recommended Reading Order for New Developers

If someone wants to understand the codebase quickly, read in this order:

1. `backend/main.py`
2. `backend/app/factory.py`
3. `backend/app/core/config.py`
4. `frontend/src/App.js`
5. `backend/app/api/*.py`
6. `backend/app/services/ingestion_service.py`
7. `backend/app/services/syllabus_service.py`
8. `backend/app/services/chunking_service.py`
9. `backend/app/services/mapping_service.py`
10. `backend/app/services/question_service.py`
11. `backend/app/services/bloom_service.py`
12. `frontend/src/components/*.js`
13. `frontend/src/App.css`

That order moves from system entrypoints to the deepest logic.

---

## 15. Short Mental Model

If you want the shortest possible correct mental model of AQPG:

AQPG is a local, multi-stage pipeline where:

- PDFs are ingested and cleaned,
- syllabi are turned into structured topic maps,
- textbooks are chunked,
- SBERT links topics to chunks,
- the frontend lets the user choose scope and paper structure,
- Flan-T5 and Mistral generate questions,
- DistilBERT/heuristics classify Bloom levels,
- and the final paper is rendered in React.

That is the whole system in one sentence.
