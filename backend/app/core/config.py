"""
Centralized configuration for the backend application.
All paths, model names, and constants are defined here.
"""

import os
from pathlib import Path


# --------------------------------------------------
# DIRECTORY PATHS
# --------------------------------------------------

# Root of the entire project (parent of backend/)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Backend root
BACKEND_ROOT = Path(__file__).resolve().parents[2]

# Runtime output directory (moved to PROJECT_ROOT to avoid uvicorn --reload loops)
PROCESSED_DATA_DIR = PROJECT_ROOT / "processed_data"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# MODEL PATHS
# --------------------------------------------------

SBERT_MODEL_PATH = str(PROJECT_ROOT / "models" / "sbert_custom_model")
FLAN_T5_MODEL_PATH = str(PROJECT_ROOT / "models" / "flan t5 large final")

# Fallback model names (downloaded from HuggingFace if local not found)
SBERT_FALLBACK_MODEL = "all-MiniLM-L6-v2"
FLAN_T5_FALLBACK_MODEL = "google/flan-t5-small"

# Semantic Syllabus Extractor (Local Mistral via Ollama)
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "mistral"


# --------------------------------------------------
# SBERT MAPPING SETTINGS
# --------------------------------------------------

SIMILARITY_THRESHOLD = 0.45
DIVERSITY_THRESHOLD = 0.85
MAX_CHUNKS_PER_TOPIC = 6

# --------------------------------------------------
# CHUNKING SETTINGS (character-based for RecursiveCharacterTextSplitter)
# --------------------------------------------------

CHUNK_SIZE_CHARS = 2000
CHUNK_OVERLAP_CHARS = 300
MIN_CHUNK_LENGTH = 300

# --------------------------------------------------
# CORS SETTINGS
# --------------------------------------------------

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
]

# --------------------------------------------------
# TESSERACT / POPPLER (platform-aware)
# --------------------------------------------------

import platform

if platform.system() == "Windows":
    TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    POPPLER_PATH = r"C:\poppler\Library\bin"
else:
    # On macOS/Linux, assume installed via brew/apt and available on PATH
    TESSERACT_CMD = "tesseract"
    POPPLER_PATH = None
