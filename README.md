# Question Paper Generation System

An intelligent NLP-based platform for automated question paper generation. Uses **SBERT** for semantic topic-chunk mapping, **Flan-T5** for question generation, and **DistilBERT** for Bloom's taxonomy classification.

## Project Structure

```
├── backend/                    # FastAPI backend
│   ├── main.py                 # ← Single entrypoint
│   └── app/
│       ├── api/                # Route handlers
│       ├── services/           # Business logic (ML models)
│       ├── models/             # Pydantic schemas
│       ├── core/               # Config & constants
│       └── utils/              # Shared utilities
├── frontend/                   # React frontend (CRA)
│   └── src/App.js
├── models/                     # Trained ML model weights
│   ├── sbert_custom_model/     # Fine-tuned SBERT
│   └── flan_t5_cns_model/      # Fine-tuned Flan-T5
├── docs/                       # Project documentation
├── scripts/standalone/         # Archived standalone scripts
└── requirements.txt
```

## Quick Start

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Start the backend server
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

### Frontend

```bash
cd frontend
npm install
npm start
```

The React app will open at `http://localhost:3000`.

## Pipeline

1. **Upload Syllabus** → Extracts module-wise topics from syllabus PDF
2. **Upload Textbook** → Chunks textbook content with page metadata
3. **Semantic Mapping** → Maps topics to chunks using SBERT embeddings
4. **Configure Pattern** → Set exam structure (parts, marks, Bloom levels)
5. **Generate Questions** → Generates questions using Flan-T5 + Bloom classification

## Models

| Model | Purpose | Location |
|-------|---------|----------|
| SBERT (fine-tuned) | Topic ↔ chunk semantic mapping | `models/sbert_custom_model/` |
| Flan-T5 (fine-tuned) | Question text generation | `models/flan_t5_cns_model/` |
| DistilBERT | Bloom's taxonomy classification | Loaded at runtime |
