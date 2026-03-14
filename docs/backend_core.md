# Backend — Core Layer (`backend/app/core/`)

> **For developers & agents:** This document describes the `core/` directory — centralized configuration for the entire backend application.

---

## Directory Overview

```
backend/app/core/
├── __init__.py    # Package init (empty)
└── config.py      # All paths, model names, thresholds, and constants
```

---

## `__init__.py`

Empty package initializer. Makes `core/` importable as `app.core`.

---

## `config.py`

Single source of truth for every configurable value in the backend. Every service and utility file imports its settings from here. This is the **first file to check** when debugging path issues, threshold tuning, or CORS problems.

### Constants Defined

#### Directory Paths

| Constant | Value | Purpose |
|----------|-------|---------|
| `PROJECT_ROOT` | 3 levels up from `config.py` (repo root) | Reference point for model paths |
| `BACKEND_ROOT` | 2 levels up from `config.py` (`backend/`) | Reference point for processed data |
| `PROCESSED_DATA_DIR` | `backend/processed_data/` | Runtime output directory for all JSON artifacts; auto-created on import |

#### Model Paths

| Constant | Value | Purpose |
|----------|-------|---------|
| `SBERT_MODEL_PATH` | `<PROJECT_ROOT>/models/sbert_custom_model` | Local SBERT model directory |
| `FLAN_T5_MODEL_PATH` | `<PROJECT_ROOT>/models/flan_t5_cns_model` | Local Flan-T5 model directory |
| `SBERT_FALLBACK_MODEL` | `"all-MiniLM-L6-v2"` | HuggingFace model ID if local SBERT not found |
| `FLAN_T5_FALLBACK_MODEL` | `"google/flan-t5-small"` | HuggingFace model ID if local Flan-T5 not found |

> **Agent note:** If you see models loading slowly or unexpectedly downloading, check whether the local model directories exist at the paths above. The fallback paths trigger automatic downloads from HuggingFace Hub.

#### SBERT Mapping Settings

| Constant | Default | Purpose |
|----------|---------|---------|
| `SIMILARITY_THRESHOLD` | `0.45` | Minimum cosine similarity score for a chunk to be considered a match |
| `DIVERSITY_THRESHOLD` | `0.85` | Maximum inter-chunk similarity to enforce diversity in selected chunks |
| `MAX_CHUNKS_PER_TOPIC` | `6` | Maximum number of chunks to map per syllabus topic |

#### Chunking Settings

| Constant | Default | Purpose |
|----------|---------|---------|
| `CHUNK_SIZE_WORDS` | `200` | Number of words per text chunk |
| `MIN_CHUNK_LENGTH` | `50` | Minimum character length for a chunk to be retained |

#### CORS Settings

| Constant | Value |
|----------|-------|
| `CORS_ORIGINS` | `["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"]` |

> **Agent note:** If adding a new frontend origin (e.g., deploying to production), add the URL to this list.

#### OCR Settings (Platform-Aware)

| Constant | Windows | macOS/Linux |
|----------|---------|-------------|
| `TESSERACT_CMD` | `C:\Program Files\Tesseract-OCR\tesseract.exe` | `"tesseract"` (expects it on PATH) |
| `POPPLER_PATH` | `C:\poppler\Library\bin` | `None` (expects it on PATH) |

---

## How Config Is Used

Every service, API route, and utility imports values directly from `config.py`:

```python
from app.core.config import PROCESSED_DATA_DIR, SBERT_MODEL_PATH, SIMILARITY_THRESHOLD
```

There is **no `.env` file** or environment variable loading — all values are hardcoded. To make values configurable at runtime, you'd need to refactor this file to use `os.environ.get()` or a Pydantic `BaseSettings` class.

---

## Agent Notes

- Changing `SIMILARITY_THRESHOLD` or `DIVERSITY_THRESHOLD` directly impacts the quality and quantity of topic-to-chunk mappings in `mapping_service.py`.
- `PROCESSED_DATA_DIR` is auto-created on module import (`mkdir(parents=True, exist_ok=True)`), so it's always guaranteed to exist.
- Model paths use `Path.resolve()` so they always produce absolute paths regardless of where the server is started from.
