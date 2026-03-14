# Backend — API Layer (`backend/app/api/`)

> **For developers & agents:** This document describes every file in the `api/` directory — the FastAPI router layer that exposes HTTP endpoints to the frontend.

---

## Directory Overview

```
backend/app/api/
├── __init__.py        # Package init (empty)
├── syllabus.py        # POST /extract-syllabus
├── textbook.py        # POST /chunk-textbook
├── mapping.py         # POST /semantic-mapping
└── questions.py       # POST /set-question-pattern, POST /generate-questions
```

All routers are registered in `app/factory.py` via `app.include_router(...)`.

---

## `__init__.py`

Empty package initializer. Makes `api/` importable as `app.api`.

---

## `syllabus.py`

**Router tag:** `syllabus`

### `POST /extract-syllabus`

Upload a syllabus PDF and extract module-wise topics.

| Aspect | Detail |
|--------|--------|
| **Input** | `UploadFile` (PDF) via multipart form |
| **Processing** | Calls `extract_syllabus_text()` → `extract_module_topics()` from `syllabus_service` |
| **Persists** | `processed_data/syllabus_topics.json` |
| **Returns** | `{ message, modules }` where `modules` is a `Dict[str, List[str]]` mapping module names to topic lists |

**Dependencies:**
- `app.services.syllabus_service` — `extract_syllabus_text`, `extract_module_topics`
- `app.core.config` — `PROCESSED_DATA_DIR`

---

## `textbook.py`

**Router tag:** `textbook`

### `POST /chunk-textbook`

Upload a textbook PDF, extract text, chunk it, extract images, and map images to chunks.

| Aspect | Detail |
|--------|--------|
| **Input** | `UploadFile` (PDF) via multipart form |
| **Processing** | 1. Clears old images directory<br>2. `extract_pages()` — page-wise text extraction<br>3. `chunk_text_by_page()` — splits into fixed-size word chunks<br>4. `extract_images_from_pdf()` — saves images from each page<br>5. `map_chunks_to_images()` — associates images with chunks by page number |
| **Persists** | `processed_data/textbook_chunks.json` and images in `processed_data/images/` |
| **Returns** | `{ message, total_chunks, total_images }` |

**Dependencies:**
- `app.services.ingestion_service` — `extract_pages`
- `app.services.chunking_service` — `chunk_text_by_page`
- `app.utils.image_utils` — `extract_images_from_pdf`, `map_chunks_to_images`
- `app.core.config` — `PROCESSED_DATA_DIR`

---

## `mapping.py`

**Router tag:** `mapping`

### `POST /semantic-mapping`

Perform semantic mapping between syllabus topics and textbook chunks using the SBERT model.

| Aspect | Detail |
|--------|--------|
| **Input** | None (uses previously persisted data on disk) |
| **Prerequisite** | Both `syllabus_topics.json` and `textbook_chunks.json` must exist in `processed_data/` |
| **Processing** | 1. Loads syllabus topics and flattens modules to a single topic list<br>2. Loads textbook chunks<br>3. Calls `mapping_service.map_topics_to_chunks()` — SBERT encodes both, computes cosine similarity, selects diverse top-K chunks per topic |
| **Persists** | `processed_data/topic_chunk_mapping.json` |
| **Returns** | `{ message, mapping }` where `mapping` is `Dict[topic_str, List[{chunk_id, page, score}]]` |

**Error handling:** Returns `{ error }` if syllabus/textbook haven't been processed yet, if no topics found, or if mapping fails.

**Dependencies:**
- `app.services.mapping_service` — `mapping_service` singleton
- `app.core.config` — `PROCESSED_DATA_DIR`

---

## `questions.py`

**Router tag:** `questions`

### `POST /set-question-pattern`

Save the exam question pattern configuration.

| Aspect | Detail |
|--------|--------|
| **Input** | JSON body conforming to `ExamPattern` schema |
| **Processing** | Flattens the nested `ExamPattern` into a list of per-question generation plan dicts. Includes `or_choice` configurations if `has_internal_choice` is true. |
| **Persists** | `processed_data/question_pattern.json` |
| **Returns** | `{ message, generation_plan }` |

### `POST /generate-questions`

Generate exam questions based on the given pattern.

| Aspect | Detail |
|--------|--------|
| **Input** | JSON body conforming to `ExamPattern` schema |
| **Processing** | 1. `question_service.generate_questions_from_pattern()` — loads topic mapping, chunks, syllabus; generates questions and internal `or_question` alternatives via Flan-T5 (with template fallback)<br>2. Each generated question (and its `or_question`) is enriched with `bloom_service.classify()` for Bloom's taxonomy verification |
| **Persists** | `processed_data/generated_questions.json` |
| **Returns** | `{ message, questions }` where `questions` is `Dict[part_name, List[question_dict]]` |

**Error handling:** Catches all exceptions; returns `{ error, message }` if generation fails.

**Dependencies:**
- `app.models.schemas` — `ExamPattern`
- `app.services.question_service` — `question_service` singleton
- `app.services.bloom_service` — `bloom_service` singleton
- `app.core.config` — `PROCESSED_DATA_DIR`

---

## Data Flow Through the API Layer

```
Frontend                   API                          Services
───────                   ────                          ────────
[Upload Syllabus PDF] ──→ /extract-syllabus  ─────────→ syllabus_service
                              │                           │
                              ▼                           ▼
                          syllabus_topics.json       (text extraction + parsing)

[Upload Textbook PDF] ──→ /chunk-textbook    ─────────→ ingestion_service
                              │                        + chunking_service
                              ▼                        + image_utils
                          textbook_chunks.json

[Run Mapping]         ──→ /semantic-mapping  ─────────→ mapping_service (SBERT)
                              │
                              ▼
                          topic_chunk_mapping.json

[Configure Pattern]   ──→ /set-question-pattern ──────→ (saves flat plan)
                              │
                              ▼
                          question_pattern.json

[Generate Questions]  ──→ /generate-questions ────────→ question_service (Flan-T5)
                              │                        + bloom_service
                              ▼
                          generated_questions.json
```

---

## Agent Notes

- **No authentication/authorization** — all endpoints are fully open.
- **No database** — all state is persisted as JSON files in `processed_data/`.
- **Sequential pipeline** — each endpoint assumes the previous steps have been completed; there is no automatic validation of prerequisite data except in `mapping.py`.
- **CORS** is configured in `factory.py` to allow requests from `localhost:3000`, `127.0.0.1:3000`, and `localhost:5173`.
