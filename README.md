# AQPG - Automated Question Paper Generation System

AQPG is a local-first AI pipeline that:

1. Extracts module/topics from a syllabus PDF.
2. Extracts and chunks content from a textbook PDF.
3. Semantically maps syllabus topics to textbook chunks.
4. Generates exam questions from a configurable paper pattern.
5. Classifies generated questions using Bloom's taxonomy.

The project is designed to run fully on your machine (with Ollama + local/inferred model loading), so textbook/syllabus content does not need to leave your local environment.

---

## Documentation Index

- Deep technical architecture and file-by-file explanation: `docs/developer_guide.md`
- Additional codebase references: `docs/COMPREHENSIVE_CODEBASE_GUIDE.md`
- LoRA training notebook/script notes: `train.md`

---

## Tech Stack

### Frontend
- React (`frontend/`)

### Backend
- FastAPI (`backend/`)
- PDF extraction: PyMuPDF (+ OCR fallback with Tesseract)
- Semantic mapping: Sentence Transformers (SBERT)
- Question generation:
  - Low mark: Flan-T5 path
  - High mark: Mistral via Ollama (`mistral-pyq` adapter)
- Bloom classification: DistilBERT pipeline + keyword fallback

---

## 1) Prerequisites

Install these before setup:

- Python 3.10+ recommended
- Node.js 18+ and npm
- Git
- Ollama installed and running
- Tesseract OCR installed (needed for scanned PDFs)
- (Windows only) Poppler binaries for `pdf2image`

Optional but recommended:
- GPU-capable environment for faster local model inference/training
- `models/` directory with pre-downloaded custom models

---

## 2) Project Structure (Important Paths)

- `backend/` - FastAPI backend
- `frontend/` - React frontend
- `processed_data/` - runtime pipeline artifacts (auto-created/updated)
- `models/` - optional local model directories
- `Modelfile` - Ollama model adapter recipe used for `mistral-pyq`
- `pyq_mistral_train.jsonl` - prior question dataset used in high-mark generation support

---

## 3) Local Setup - Backend

From project root:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
```

On Windows (PowerShell):

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
```

### Backend Run

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Backend health check:

```bash
curl http://127.0.0.1:8000/
```

Expected response:

```json
{"status":"Backend running successfully"}
```

---

## 4) Local Setup - Frontend

From project root in a new terminal:

```bash
cd frontend
npm install
npm start
```

The UI opens at:
- `http://localhost:3000`

Frontend talks to:
- `REACT_APP_API_URL` if set
- else default backend `http://127.0.0.1:8000`

---

## 5) Mistral Adapter Setup (Ollama) - Required for Best High-Mark Results

This repo contains a `Modelfile`:

```text
FROM mistral
ADAPTER "models/mistral 1/Mistral-1-F32-LoRA.gguf"
```

This means AQPG expects an Ollama model named `mistral-pyq` (or equivalent) built by combining:
- base `mistral` model
- local LoRA adapter file at `models/mistral 1/Mistral-1-F32-LoRA.gguf`

### 5.1 Ensure Ollama is installed and running

Check:

```bash
ollama --version
ollama list
```

### 5.2 Pull base Mistral model

```bash
ollama pull mistral
```

### 5.3 Place adapter file

Put your LoRA GGUF adapter at:

- `models/mistral 1/Mistral-1-F32-LoRA.gguf`

If you use another path/name, update `Modelfile` accordingly.

### 5.4 Build adapter model in Ollama

From project root:

```bash
ollama create mistral-pyq -f Modelfile
```

### 5.5 Verify adapter model

```bash
ollama list
ollama run mistral-pyq "Write one 12-mark university exam question on operating systems memory management."
```

If this works, AQPG high-mark generation path can use `mistral-pyq`.

---

## 6) Model Resolution Behavior in AQPG

Configured in `backend/app/core/config.py`:

- SBERT local path: `models/sbert_custom_model`
- T5 local path: `models/flan t5 large final`
- SBERT fallback: `all-MiniLM-L6-v2`
- T5 fallback: `google/flan-t5-small`
- Ollama base URL: `http://localhost:11434`

### Important runtime behavior

- If local SBERT/T5 folders do not exist, backend falls back to Hugging Face model names.
- First fallback run may download weights (internet required once).
- High-mark path in question service calls Ollama and expects local Ollama service reachable.

---

## 7) Optional: About Training the Mistral LoRA Adapter

`train.md` contains a notebook-style workflow using Unsloth + SFTTrainer to create LoRA adapters.

Typical flow:
1. Load quantized Mistral instruct model.
2. Apply LoRA config.
3. Train on JSONL prompt-completion style data.
4. Save LoRA adapter.
5. Export/convert to GGUF adapter format compatible with your Ollama setup.
6. Reference adapter in `Modelfile`.

Note:
- Training script in `train.md` is experimental/not productionized as a CLI.
- Keep training artifacts versioned externally; only publish final adapter intended for inference.

---

## 8) End-to-End Run Sequence (UI)

With backend + frontend + Ollama running:

1. Step 1: Upload syllabus PDF.
2. Step 2: Upload textbook PDF (optionally with page range).
3. Step 3: Select topics (auto or manual).
4. Step 4: Run semantic mapping.
5. Step 5: Configure question paper pattern.
6. Step 6: Generate questions and optionally regenerate individual questions.

---

## 9) Runtime Files You Should Expect

Generated under `processed_data/`:

- `syllabus_topics.json`
- `selected_topics.json` (if topic filtering used)
- `textbook_chunks.json`
- `topic_chunk_mapping.json`
- `question_pattern.json`
- `generated_questions.json`
- `images/`
- `cache/` (embedding cache)

These are crucial for debugging each pipeline stage.

---

## 10) Common Troubleshooting

### Backend starts but generation fails
- Ensure Ollama is running.
- Ensure `mistral-pyq` exists in `ollama list`.
- Check `processed_data/topic_chunk_mapping.json` exists before generation.

### No/poor syllabus topics extracted
- Validate syllabus PDF text quality.
- Try a cleaner digital PDF (not scanned image-only).
- Verify Ollama base model responds.

### No chunks or too few chunks
- Check textbook extraction quality (scanned docs may need OCR).
- Verify Tesseract installation.
- If page range used, confirm range is valid.

### High-mark questions become generic
- Verify adapter model is actually used (`mistral-pyq` available).
- Inspect mapping scores and context quality.
- Improve adapter quality or training data.

### Slow first run
- Normal when fallback models are downloaded first time.
- Later runs should be faster due to cache and model warm state.

---

## 11) Development Tips

- Keep backend and frontend in separate terminals.
- Do not delete `processed_data/` while active requests are running.
- If behavior looks stale after uploading new files, re-run mapping and generation.
- Use `docs/developer_guide.md` for deeper internals before making service-level changes.

---

## 12) Security and Privacy Notes

- AQPG is designed for local processing.
- No mandatory external SaaS API calls are built into the main generation path.
- Fallback model downloads from Hugging Face may occur when local model folders are missing.

For stricter offline use:
- Pre-download all required models.
- Keep Ollama models/adapters local.
- Block internet after initial setup if needed.
