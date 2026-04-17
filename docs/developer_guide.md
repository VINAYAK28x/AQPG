# AQPG Developer Guide (Deep Technical Reference)

This document is the detailed technical guide for developers working on AQPG (Automated Question Paper Generator).

It is written to help a new engineer understand:

1. How the system works end-to-end.
2. What each backend/frontend file does.
3. What each major function/class is responsible for.
4. Which models/libraries are used, and why.
5. Which runtime artifacts are produced between pipeline stages.

---

## 1) What AQPG Does

AQPG is a local-first pipeline that converts syllabus and textbook PDFs into a formatted exam paper.

Core workflow:

1. Parse syllabus PDF into structured modules/topics.
2. Parse textbook PDF into clean chunks with page metadata.
3. Map syllabus topics to textbook chunks using embeddings.
4. Let the user configure an exam pattern.
5. Generate questions per pattern using T5 + Mistral (via Ollama).
6. Classify generated questions into Bloom levels.
7. Render printable university-style paper in React UI.

The system is intentionally stateful via JSON files in `processed_data/` rather than a database.

---

## 2) Architecture Overview

### Backend (`backend/`)
- FastAPI app.
- Handles ingestion, parsing, mapping, generation, and Bloom classification.
- Writes all intermediate/final artifacts to `processed_data/`.

### Frontend (`frontend/`)
- React single-page workflow UI.
- Drives the linear 6-step process.
- Calls backend endpoints and renders semantic mapping + generated paper output.

### Dataflow Summary
- `POST /extract-syllabus` -> writes `syllabus_topics.json`
- `POST /chunk-textbook` -> writes `textbook_chunks.json`
- `POST /semantic-mapping` -> writes `selected_topics.json` + `topic_chunk_mapping.json`
- `POST /set-question-pattern` -> writes `question_pattern.json`
- `POST /generate-questions` -> writes `generated_questions.json`
- `POST /regenerate-question` -> in-memory regeneration path + response payload

---

## 3) ML/LLM Stack and Why Each Exists

### Mistral via Ollama (`mistral`, `mistral-pyq`)
- Used for high-mark question generation and question refinement.
- Also used in syllabus topic extraction prompt chain.
- Accessed over local HTTP (`http://localhost:11434/api/generate`) so backend remains an orchestrator rather than hosting a large instruction model directly.

### Flan-T5 (`models/flan t5 large final` or `google/flan-t5-small`)
- Used mainly for low-mark draft generation.
- Lightweight and fast for short factual prompts.
- If local model path is unavailable, fallback HF model is loaded.

### SBERT (`models/sbert_custom_model` or `all-MiniLM-L6-v2`)
- Used for semantic topic-to-chunk mapping.
- Also used in high-mark validation/coherence and context compression.
- Embeddings are cached on disk to reduce repeated compute.

### DistilBERT Bloom Classifier (`models/bloom_classifier/.../blooms_classifier`)
- Classifies generated question text into Bloom levels.
- Used as a post-generation annotation/validation layer.
- Falls back to keyword heuristics when model is unavailable.

### spaCy (`en_core_web_sm`)
- Optional validation layer in question checks.
- Detects suspicious named entities not grounded in source context.

### BM25 (`rank_bm25`) + NLTK sentence tokenization
- Used in `compress_context` path for lexical + semantic hybrid relevance.
- Helps keep high-mark prompts context-dense under token limits.

---

## 4) Dependency Breakdown

From `requirements.txt`:

- **API/runtime:** `fastapi`, `uvicorn`, `pydantic`, `python-multipart`
- **PDF parsing:** `PyMuPDF`
- **Core NLP/ML:** `sentence-transformers`, `transformers`, `torch`, `scikit-learn`
- **Validation/retrieval:** `spacy`, `nltk`, `rank_bm25`
- **Chunking helper:** `langchain-text-splitters`
- **OCR fallback stack:** `pytesseract`, `pdf2image`, `Pillow`
- **Support libs:** `numpy`, `datasets`, `accelerate`

Frontend highlights:
- `react`, `react-dom`, `react-scripts`

---

## 5) Runtime Artifacts (`processed_data/`)

These files represent pipeline state:

- `syllabus_topics.json`: extracted course metadata + module/topic structure.
- `selected_topics.json`: optional filtered syllabus subset chosen by user.
- `textbook_chunks.json`: chunk list with `chunk_id`, `page`, `text`, `images`.
- `topic_chunk_mapping.json`: mapping of module/topic -> scored chunk references.
- `question_pattern.json`: flattened generation plan from configured pattern.
- `generated_questions.json`: final generated paper with Bloom classification tags.
- `images/`: extracted textbook images.
- `cache/`: SBERT embedding pickle cache files.

No database exists; these files are the source of truth between calls.

---

## 6) Backend File-by-File Reference

## 6.1 `backend/main.py`
- Thin entrypoint that builds app from factory.
- Keeps startup logic minimal.

## 6.2 `backend/app/factory.py`
### Purpose
- Composition root for FastAPI app.

### Key function
- `create_app()`
  - Creates FastAPI instance.
  - Configures CORS using `CORS_ORIGINS`.
  - Includes routers from `syllabus`, `textbook`, `mapping`, `questions`.
  - Registers health route `GET /`.

## 6.3 `backend/app/core/config.py`
### Purpose
- Central constants for paths, models, thresholds, and CORS.

### Important values
- `PROJECT_ROOT`, `BACKEND_ROOT`, `PROCESSED_DATA_DIR`
- `SBERT_MODEL_PATH`, `FLAN_T5_MODEL_PATH`
- `SBERT_FALLBACK_MODEL`, `FLAN_T5_FALLBACK_MODEL`
- `OLLAMA_BASE_URL`, `LLM_MODEL`
- `SIMILARITY_THRESHOLD`, `DIVERSITY_THRESHOLD`, `MAX_CHUNKS_PER_TOPIC`
- `CHUNK_SIZE_CHARS`, `CHUNK_OVERLAP_CHARS`, `MIN_CHUNK_LENGTH`
- `TESSERACT_CMD`, `POPPLER_PATH` (platform-aware)

## 6.4 `backend/app/models/schemas.py`
### Purpose
- Pydantic contracts for question API payloads.

### Models
- `SubQuestionPattern`: `(label, marks)` unit.
- `OrChoicePattern`: OR branch config.
- `QuestionPattern`: question slot including module/marks/internal-choice/sub-questions.
- `PartPattern`: section-level pattern.
- `ExamPattern`: full paper payload root.
- `RegenerateRequest`: per-question regenerate payload.

## 6.5 `backend/app/api/syllabus.py`
### Endpoint
- `POST /extract-syllabus`

### Flow
- Reads uploaded PDF bytes.
- Calls `extract_syllabus_text` -> `extract_module_topics` -> `build_structured_syllabus`.
- Persists `syllabus_topics.json`.
- Calls `question_service.clear_caches()`.

## 6.6 `backend/app/api/textbook.py`
### Endpoint
- `POST /chunk-textbook`

### Functions
- `parse_page_range(page_range)`
  - Parses `1-5, 8, 10-20` style input to set of pages.
- `chunk_textbook(file, page_range)`
  - Extracts pages.
  - Filters pages if range given.
  - Chunks text.
  - Extracts images and maps image metadata to chunks.
  - Persists `textbook_chunks.json`.
  - Clears generation caches.

## 6.7 `backend/app/api/mapping.py`
### Endpoint
- `POST /semantic-mapping`

### Request model
- `MappingRequest.selected_modules: Optional[Dict[module, List[topics]]]`

### Flow
- Loads `syllabus_topics.json` + `textbook_chunks.json`.
- Optionally filters syllabus to selected topics.
- Saves filtered selection to `selected_topics.json`.
- Calls `mapping_service.map_modules_to_chunks`.
- Saves `topic_chunk_mapping.json`.

## 6.8 `backend/app/api/questions.py`
### Endpoints
- `POST /set-question-pattern`
- `POST /generate-questions`
- `POST /regenerate-question`

### Functions
- `set_question_pattern(pattern)`
  - Flattens pattern into generation plan and persists `question_pattern.json`.
- `generate_questions(pattern)`
  - Calls `question_service.generate_questions_from_pattern`.
  - Collects all main/sub/or texts.
  - Batch classifies via `bloom_service.classify_batch`.
  - Writes back `classified_bloom_level` into nested structure.
  - Persists `generated_questions.json`.
- `regenerate_question(req)`
  - Loads mapping/chunk/syllabus artifacts.
  - Builds mock question/part object shape.
  - Reuses `_generate_single_question`.
  - Classifies regenerated text(s) and returns payload.

## 6.9 `backend/app/services/ingestion_service.py`
### Purpose
- Robust text extraction with OCR fallback.

### Functions
- `clean_extracted_text(text)`: removes textbook noise and formatting junk.
- `extract_text(pdf_bytes)`: full-text extraction with fallback to OCR.
- `extract_pages(pdf_bytes)`: page-wise extraction for chunking stage.
- `_ocr_extract(pdf_bytes)`: `pdf2image` + `pytesseract`.
- `extract_syllabus_raw(pdf_bytes)`: less aggressive cleanup for syllabus semantics.

## 6.10 `backend/app/services/chunking_service.py`
### Purpose
- Convert page text into quality-filtered chunks.

### Functions
- `technical_density(text)`: heuristic signal for chunk quality.
- `sentence_count(text)`: rough sentence metric.
- `_is_quality_chunk(text)`: filters low-signal chunks.
- `chunk_text_by_page(...)`: uses recursive char splitter and returns chunk dicts.

## 6.11 `backend/app/services/syllabus_service.py`
### Purpose
- Parse syllabus text into structured module/topic graph + metadata.

### Components
- `SyllabusTopicsList`: parser schema for LLM JSON extraction.
- `_extract_topics_from_module_text(module_text)`
  - ChatOllama + PromptTemplate + JsonOutputParser chain.
  - Returns clean topic list or fallback.
- `extract_module_topics(text)`
  - Detects module blocks.
  - Ignores non-topic noise lines.
  - Calls semantic topic extractor per module.
  - Fallbacks to `General Topics` when module headings are absent.
- `build_embedding_ready_text(topics)`: normalization for retrieval text.
- `build_structured_syllabus(text, modules)`: final structured payload.

## 6.12 `backend/app/services/mapping_service.py`
### Purpose
- Build topic-level semantic links to textbook chunks.

### Class: `MappingService`
- `model` property: lazy SBERT load (custom/fallback).
- `_compute_hash(texts)`: MD5 cache key.
- `_encode_with_cache(texts, prefix)`: embedding cache read/write.
- `_cleanup_cache(prefix)`: keep recent cache files only.
- `map_modules_to_chunks(...)`
  - Topic embedding vs all chunk embeddings.
  - Threshold filtering + fallback top-k.
  - Diversity filtering.
  - Deduplication by similarity.
  - Produces nested `topic_mappings`.
- `_deduplicate_chunks(...)`: removes semantically near-duplicate chunk candidates.
- `_build_embedding_text(raw_text)`: normalization helper.
- `map_topics_to_chunks(...)`: legacy method retained.

Singleton: `mapping_service`.

## 6.13 `backend/app/services/bloom_service.py`
### Purpose
- Bloom level classification for generated text.

### Constants
- `BLOOM_LEVELS`, `LABEL_INDEX_MAP`, `BLOOM_KEYWORDS`

### Class: `BloomClassifierService`
- `_load_model()`: lazy load classification pipeline.
- `classify(text)`: single text path.
- `classify_batch(texts)`: batched path for speed.
- `_map_label_to_bloom(label, original_text)`: label normalization.
- `_classify_with_model(text)`: model path.
- `_classify_with_keywords(text)`: heuristic fallback.

Singleton: `bloom_service`.

## 6.14 `backend/app/services/question_service.py` (Core Orchestrator)
### Purpose
- Main generation engine tying together mapping artifacts, model calls, validation, and fallback logic.

### Core responsibilities
- Load and cache runtime JSON artifacts.
- Route by marks (low-mark vs high-mark generation).
- Build and regenerate main/or/sub questions.
- Apply question validation and refinement.

### Important methods
- `clear_caches()`: reset in-memory artifact caches.
- `_load_json(filepath)`: safe JSON loader.
- `_get_sbert_model()`, `_get_spacy_nlp()`: lazy dependency loaders.
- `_load_pyq_dataset()`: loads `pyq_mistral_train.jsonl`.
- `_parse_pyq_metadata(row)`: parse structured fields from PYQ row.
- `fetch_similar_pyqs(...)`: token-overlap + SBERT exemplar retrieval.
- `generate_high_mark_question(...)`
  - compress context,
  - retrieve few-shot PYQs,
  - call Ollama (`mistral-pyq`),
  - validate and retry,
  - fallback to hybrid rewrite.
- `fallback_t5_anchor_rewrite(...)`: T5 draft + Mistral rewrite fallback.
- `_load_model()`: T5 load with fallback and thread tuning.
- `generate_questions_from_pattern(...)`: full paper orchestration.
- `_resolve_course_subject(syllabus_topics)`: course title fallback logic.
- `_generate_single_question(...)`
  - picks topic,
  - retrieves mapped context,
  - generates main question,
  - handles internal OR branch,
  - handles sub-question blocks.
- `_expected_bloom_for_marks(marks)`: expected Bloom by mark band.
- `_generate_with_bloom_retry(...)`: retries low-mark generation with Bloom check.
- `_generate_with_t5(...)`: low-mark generation + cleanup + Ollama refinement.
- `_generate_with_template(...)`: final fallback template path.
- `_get_random_topic(...)`: module-aware topic sampling with repeat avoidance.

Singleton: `question_service`.

## 6.15 Utility Modules

### `backend/app/utils/pdf_utils.py`
- `extract_full_text`, `extract_text_by_page`, `is_valid_extracted_text`.
- Decides whether text looks meaningful before OCR fallback path.

### `backend/app/utils/image_utils.py`
- `extract_images_from_pdf`: extract + save image metadata.
- `map_chunks_to_images`: attach image list to chunk objects by page.

### `backend/app/utils/context_utils.py`
- `normalize_module_name`: normalize Roman/Arabic module forms.
- `find_matching_key`: normalized dictionary key resolution.
- `normalize_subject_name`, `mark_bucket`, `extract_topic_tokens`: retrieval helpers.
- `compress_context`: hybrid SBERT/BM25 sentence-level context compression.
- `get_relevant_chunks`: resolves topic mapping and stitches top-ranked chunk texts.

### `backend/app/utils/ollama_client.py`
- `ollama_generate`: low-level HTTP caller.
- `extract_generated_question`: strips prompt wrappers.
- `refine_with_ollama`: post-processes draft into cleaner mark-aware question.

### `backend/app/utils/question_constants.py`
- Defines `BLOOM_VERBS`, `VALID_OPENERS`, `CONTEXT_STOPWORDS`, scaffold template.
- These constants shape both prompting and validation behavior.

### `backend/app/utils/question_validation.py`
- `validate_question`: gatekeeper for length/format/meta-phrases/entity-coherence/semantic fit.
- `filter_hallucinations`: regex cleanup for code-like garbage output.

### `backend/app/utils/syllabus_extractors.py`
- `extract_course_title`, `_clean_title`, `extract_course_code`, `extract_course_outcomes`.
- Handles flexible syllabus formats and noisy text layouts.

---

## 7) Frontend File-by-File Reference

## 7.1 `frontend/src/index.js`
- React bootstrap mounting `App`.

## 7.2 `frontend/src/App.js`
### Purpose
- Master workflow controller and state owner.

### State domains
- **Step/navigation:** `step`
- **Syllabus/topics:** `topics`, `syllabusLoading`, `selectedTopics`
- **Textbook/chunking:** `chunkCount`, `textbookLoading`, `totalPdfPages`, `pagesProcessed`
- **Pattern config:** `examName`, `parts`, `expandedParts`, `patternLoading`
- **Generation:** `generationLoading`, `generatedQuestions`, `generationError`

### Main handlers
- `uploadSyllabus`: posts to `/extract-syllabus`
- `uploadTextbook`: posts to `/chunk-textbook`
- `savePattern`: posts to `/set-question-pattern`
- `generateQuestions`: posts to `/generate-questions`
- `defaultPattern`: initial Part A + Part B template

### Step rendering
1. `SyllabusUpload`
2. `TextbookUpload`
3. `TopicSelection`
4. `SemanticMapping`
5. `PatternConfig`
6. `GeneratedQuestions`

## 7.3 `frontend/src/components/Stepper.js`
- Displays clickable 6-step progress with completed-state indicators.

## 7.4 `frontend/src/components/SyllabusUpload.js`
- Upload UI for syllabus.
- Displays extracted course metadata/modules/topics.

## 7.5 `frontend/src/components/TextbookUpload.js`
- Upload UI with all-pages vs custom page-range option.
- Shows chunking progress stats.

## 7.6 `frontend/src/components/TopicSelection.js`
- Switches between auto mode (all topics) and manual topic selection.
- Supports per-module and per-topic toggles.

## 7.7 `frontend/src/components/SemanticMapping.js`
- Triggers `/semantic-mapping`.
- Renders returned module/topic/chunk similarity structure.

## 7.8 `frontend/src/components/PatternConfig.js`
### Purpose
- High-interaction exam structure editor.

### Key helpers
- `updatePart`, `updateQuestion`
- `addPart`, `removePart`
- `addQ`, `removeQ`
- `toggleExpand`
- `toggleSubQuestions`
- `addSubQuestion`, `removeSubQuestion`, `updateSubQuestion`

### Notable behavior
- Uses dynamic module list from extracted syllabus when available.
- Supports OR choices and sub-question splits for both main and OR branches.
- Shows summary totals for questions and marks.

## 7.9 `frontend/src/components/GeneratedQuestions.js`
### Purpose
- Render final paper and support per-question regeneration.

### Key logic
- `bloomToCode(level)`: maps verbose Bloom labels to L1-L6.
- `handleRegenerate(partName, idx, isOr)`: calls `/regenerate-question`, updates local nested state.
- `handleDownloadPDF`: print-based PDF export.

### Rendering details
- Screen + print-specific layouts.
- Includes course title/code/outcomes in print header.
- Shows question metadata columns (Marks/BL/CO/PO) in print mode.

## 7.10 `frontend/src/App.css` and `frontend/src/index.css`
- Main styling system and print styling rules.
- `App.css` contains most workflow/paper formatting styles.

---

## 8) API Contract Summary

- `POST /extract-syllabus`
  - multipart: `file`
  - returns structured syllabus (`course_title`, `course_code`, `course_outcomes`, `modules`)
- `POST /chunk-textbook`
  - multipart: `file`, optional `page_range`
  - returns chunk/image counts and page stats
- `POST /semantic-mapping`
  - JSON: optional `{ selected_modules: { module: [topics...] } }`
  - returns semantic mapping structure
- `POST /set-question-pattern`
  - JSON `ExamPattern`
  - persists generation plan
- `POST /generate-questions`
  - JSON `ExamPattern`
  - returns generated nested question structure with classified Bloom levels
- `POST /regenerate-question`
  - JSON `RegenerateRequest`
  - returns one regenerated question block

---

## 9) Generation Pipeline: Mental Model

When the user clicks Generate:

1. Pattern is sent to `/generate-questions`.
2. `question_service` loads mapping + chunks + selected/full syllabus.
3. For each configured slot:
   - choose topic from module,
   - fetch mapped context,
   - route by marks:
     - `<=5`: T5 path (+ Bloom retry),
     - `>5`: high-mark Mistral path with context compression + PYQ grounding.
4. Build OR/sub-question branches where configured.
5. Classify all generated texts via Bloom classifier.
6. Return to UI for final rendering and optional per-question regeneration.

---

## 10) Important Design Decisions and Tradeoffs

- **Local-first inference:** privacy-friendly, but depends on local model/runtime availability.
- **File-based pipeline state:** easy to inspect/debug, but not multi-user database architecture.
- **Lazy model loading:** faster backend startup, slower first inference call.
- **Service-oriented backend:** thin routers + concentrated logic in services/utils.
- **Hybrid generation:** no single-model dependence; each model handles a specific subproblem.

---

## 11) Extension Points for Developers

- Change syllabus extraction behavior:
  - `backend/app/services/syllabus_service.py`
  - `backend/app/utils/syllabus_extractors.py`
- Tune chunk quality/size:
  - `backend/app/services/chunking_service.py`
  - `backend/app/core/config.py`
- Change mapping behavior/thresholds:
  - `backend/app/services/mapping_service.py`
  - `backend/app/core/config.py`
- Improve question quality/validation:
  - `backend/app/services/question_service.py`
  - `backend/app/utils/question_validation.py`
  - `backend/app/utils/question_constants.py`
- Update final paper formatting/UX:
  - `frontend/src/components/GeneratedQuestions.js`
  - `frontend/src/components/PatternConfig.js`
  - `frontend/src/App.css`

---

## 12) Suggested Reading Order for New Contributors

1. `backend/app/factory.py`
2. `backend/app/core/config.py`
3. `frontend/src/App.js`
4. `backend/app/api/syllabus.py`
5. `backend/app/api/textbook.py`
6. `backend/app/api/mapping.py`
7. `backend/app/api/questions.py`
8. `backend/app/services/ingestion_service.py`
9. `backend/app/services/syllabus_service.py`
10. `backend/app/services/chunking_service.py`
11. `backend/app/services/mapping_service.py`
12. `backend/app/services/question_service.py`
13. `backend/app/services/bloom_service.py`
14. `frontend/src/components/*.js`

This order follows the same path as runtime data through the pipeline.

---

## 13) New Developer Onboarding (Step-by-Step)

This section is intentionally practical. If you are new to this repo, follow this sequence before changing code.

### 13.1 Prerequisites

You need:
- Python 3.10+ (recommended)
- Node.js + npm (for React frontend)
- Ollama installed and running locally
- Tesseract OCR installed (needed for scanned PDFs)
- Poppler (mainly relevant on Windows for `pdf2image`)

Optional but strongly recommended:
- Local model folders under `models/` (SBERT, Flan-T5, Bloom classifier)
- `en_core_web_sm` spaCy model for stronger validation

### 13.2 First local setup

Backend:
1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Ensure Ollama is running.
4. Verify model fallbacks in `backend/app/core/config.py`.

Frontend:
1. Install packages in `frontend/`.
2. Run development server.
3. Ensure frontend can reach backend URL (`REACT_APP_API_URL` or default `http://127.0.0.1:8000`).

### 13.3 First smoke test path

Use this exact order in UI:
1. Upload syllabus in Step 1.
2. Upload textbook in Step 2.
3. Select topics in Step 3 (or keep automatic).
4. Run mapping in Step 4.
5. Save/generate pattern in Step 5.
6. Validate output + regenerate one question in Step 6.

At each step, verify corresponding `processed_data/` file is created.

### 13.4 What to inspect when something fails

- If syllabus parsing fails: inspect `syllabus_topics.json`.
- If textbook processing fails: inspect `textbook_chunks.json`, especially chunk count and text quality.
- If mapping quality is poor: inspect `topic_chunk_mapping.json` similarity scores.
- If generation quality is poor: inspect mapped chunk context and whether topic/module resolution is correct.
- If Bloom labels look wrong: verify classifier model availability and fallback heuristics.

---

## 14) Pipeline Walkthrough with Data Examples

The most useful way to understand AQPG is to track data shape changes across stages.

### 14.1 Syllabus extraction output shape (`syllabus_topics.json`)

Typical structure:
- `course_title`
- `course_code`
- `course_outcomes` (list)
- `modules` (dictionary)
  - each module has:
    - `raw_text`
    - `topics`
    - `embedding_ready_text`

Why it matters:
- `topics` drive mapping + generation.
- `course_title` influences subject context in prompts.

### 14.2 Textbook chunk output shape (`textbook_chunks.json`)

Each chunk object contains:
- `chunk_id`
- `page`
- `text`
- `images` (optional list)

Why it matters:
- `chunk_id` is the stable key used in mapping results.
- `text` becomes generation context.

### 14.3 Topic mapping output shape (`topic_chunk_mapping.json`)

For each module:
- `topics`
- `embedding_ready_text`
- `topic_mappings`
  - each topic points to a ranked list of chunk references:
    - `chunk_id`
    - `page`
    - `score`

Why it matters:
- This is the context boundary for question generation.
- Wrong mapping here usually causes generic/off-topic questions.

### 14.4 Generation output shape (`generated_questions.json`)

Nested by part name (e.g., `PART A`, `PART B`), then question objects:
- `question_no`, `marks`, `module`
- `text`
- `classified_bloom_level`
- `source_chunk` (preview)
- optional `sub_questions`
- optional `or_question` (with same nested schema)

Why it matters:
- Frontend renders this structure directly.
- Regeneration updates individual nodes in this nested tree.

---

## 15) Deep Dive: Question Generation Decision Logic

This section explains how one question slot is produced.

### 15.1 Topic selection
- `_get_random_topic(module, syllabus_topics, exclude_topics)` picks a module-aligned topic.
- Module names are normalized (Roman vs Arabic forms).
- Previously seen topics are avoided when possible.

### 15.2 Context retrieval
- `get_relevant_chunks(module, topic, topic_mapping, chunks_dict)`
- Prefers topic-specific mappings (`topic_mappings`) over legacy formats.
- Selects top scored chunks and stitches them into one context block.

### 15.3 Routing by marks
- `_generate_with_bloom_retry` is the main routing layer.
- If `marks > 5` -> `generate_high_mark_question`.
- Else -> `_generate_with_t5` + Bloom retry logic.

### 15.4 High-mark path
- `compress_context` (SBERT + BM25) shrinks context to high-signal text.
- Retrieves nearest PYQ examples (`fetch_similar_pyqs`) for stylistic guidance.
- Calls Ollama (`mistral-pyq`) with scaffolded prompt.
- Validates (`validate_question`) and retries.
- Falls back to `fallback_t5_anchor_rewrite` if retries fail.

### 15.5 Low-mark path
- Builds concise prompt styles around topic + context.
- Generates with T5 (`_generate_with_t5`).
- Applies hallucination filtering.
- Applies final language refinement via `refine_with_ollama`.
- Optionally retries once if predicted Bloom level mismatches expected level.

### 15.6 Last-resort fallback
- `_generate_with_template` creates deterministic templates if models fail.
- Ensures system can still return output even under degraded model conditions.

---

## 16) API Endpoint Behavior in More Detail

### `POST /extract-syllabus`
Input:
- multipart `file`

Output:
- message + structured syllabus payload.

Side effects:
- overwrites `processed_data/syllabus_topics.json`
- clears question service caches

Failure causes:
- unreadable PDF
- no extractable module/topic content
- Ollama parse failure (will fallback but may produce low-quality topics)

### `POST /chunk-textbook`
Input:
- multipart `file`
- optional `page_range` like `1-10, 15, 20-30`

Output:
- chunk count, image count, total pages, processed pages

Side effects:
- clears `processed_data/images/` directory
- writes `textbook_chunks.json`
- clears generation caches

### `POST /semantic-mapping`
Input:
- optional topic filter payload

Output:
- semantic mapping structure with scores

Side effects:
- writes `selected_topics.json`
- writes `topic_chunk_mapping.json`

### `POST /set-question-pattern`
Input:
- `ExamPattern`

Output:
- flattened generation plan

Side effects:
- writes `question_pattern.json`

### `POST /generate-questions`
Input:
- `ExamPattern`

Output:
- nested generated questions with Bloom annotations

Side effects:
- writes `generated_questions.json`

### `POST /regenerate-question`
Input:
- module, marks, question number, optional sub-question descriptors

Output:
- one regenerated question object

Side effects:
- no full paper rewrite; caller updates UI-local state

---

## 17) Configuration Tuning Guide

Most quality/performance tuning happens in `backend/app/core/config.py`.

### 17.1 Mapping knobs
- `SIMILARITY_THRESHOLD`:
  - Increase for stricter relevance, decrease for broader context capture.
- `DIVERSITY_THRESHOLD`:
  - Lower values enforce more diversity among selected chunks.
- `MAX_CHUNKS_PER_TOPIC`:
  - Controls context breadth per topic.

### 17.2 Chunking knobs
- `CHUNK_SIZE_CHARS`:
  - Larger chunks preserve context but may include noise.
- `CHUNK_OVERLAP_CHARS`:
  - Larger overlap helps continuity at cost of redundancy.
- `MIN_CHUNK_LENGTH`:
  - Raise to drop weak tiny chunks.

### 17.3 Model path knobs
- `SBERT_MODEL_PATH`, `FLAN_T5_MODEL_PATH`
- Ensure local paths are correct to avoid silent fallback to smaller/default models.

### 17.4 Operational note
- `PROCESSED_DATA_DIR` is intentionally outside backend package tree to avoid dev reload loops from runtime file writes.

---

## 18) Debugging and Troubleshooting Playbook

### 18.1 Symptom: “Generated questions are generic”
Check:
1. `topic_chunk_mapping.json` scores.
2. Whether selected topic exists in mapping.
3. Whether `get_relevant_chunks` returned meaningful context.
4. Whether model fell back to template path.

Likely fixes:
- improve syllabus topic extraction prompt
- adjust mapping thresholds
- improve chunking quality filters

### 18.2 Symptom: “Wrong module/topic appears in output”
Check:
1. module normalization (`Module I` vs `Module 1`)
2. `selected_topics.json` content
3. topic sampling behavior in `_get_random_topic`

Likely fixes:
- normalize module naming earlier in pipeline
- enforce stronger manual topic selection constraints

### 18.3 Symptom: “No chunks generated”
Check:
1. textbook extraction quality (empty/noisy text)
2. overly strict `_is_quality_chunk` filtering
3. page range accidentally excluding all useful pages

Likely fixes:
- reduce quality strictness
- verify OCR fallback
- adjust page-range parsing

### 18.4 Symptom: “Bloom levels look off”
Check:
1. classifier model load logs
2. fallback heuristic triggers
3. question opener/verb alignment vs expected Bloom band

Likely fixes:
- improve classifier model path/config
- fine-tune keywords for subject domain language

### 18.5 Symptom: “Regeneration works but format is inconsistent”
Check:
1. whether regenerated object includes expected nested fields
2. frontend replacement logic in `GeneratedQuestions.js`
3. Bloom annotation assignment for regenerated sub-questions

---

## 19) Safe Modification Guide (Where to Change What)

If your goal is X, edit Y:

- **Change syllabus parsing behavior**
  - `syllabus_service.py`, `syllabus_extractors.py`
- **Improve textbook extraction**
  - `ingestion_service.py`, `pdf_utils.py`
- **Improve relevance/mapping**
  - `mapping_service.py`, `context_utils.py`, config thresholds
- **Improve wording/quality of questions**
  - `question_service.py`, `ollama_client.py`, `question_validation.py`
- **Change UI flow**
  - `App.js` step transitions + relevant component
- **Change paper appearance**
  - `GeneratedQuestions.js` + `App.css`
- **Add new API endpoint**
  - create route in `app/api/`, register in `factory.py`

---

## 20) Glossary (Repo-specific Terms)

- **Structured syllabus**: normalized JSON of course metadata + module topics.
- **Chunk**: one segmented block of textbook text tied to page metadata.
- **Topic mapping**: semantic link from one syllabus topic to ranked textbook chunks.
- **Generation plan**: flattened representation of exam pattern for backend generation.
- **Internal choice**: OR branch for a question slot.
- **Sub-questions**: split question (a), (b), etc under one question number.
- **Bloom classification**: post-generation label assigning cognitive level L1-L6 equivalent.

---

## 21) Final Mental Model for New Engineers

If you remember only one thing, remember this:

AQPG is a staged pipeline where each step creates a concrete artifact used by the next step.

- Syllabus step defines **what can be asked**.
- Textbook step defines **what content is available**.
- Mapping step defines **which content belongs to which topic**.
- Pattern step defines **how many and what kind of questions are needed**.
- Generation step creates **question text constrained by marks/module/context**.
- Bloom step annotates **cognitive level quality signals**.
- Frontend step renders **human-usable exam output with regeneration controls**.

When debugging, always trace backward from the broken stage to its input artifact.
