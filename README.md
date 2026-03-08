# Automated Question Paper Generation System (AQPG)

AQPG is an AI-powered system that reads university syllabus PDFs and textbook PDFs, semantically maps textbook content to syllabus topics, and mathematically generates a full examination question paper adhering to Bloom's Taxonomy and custom marking patterns.

## 🚀 System Architecture

This project is fully local to ensure maximum data privacy.
*   **Frontend:** React.js (Component-based architecture, modern glassmorphic UI)
*   **Backend:** FastAPI (Python), completely modular following SOLID principles
*   **AI Models:** 
    *   **Text/PDF Extraction:** `PyMuPDF`
    *   **Semantic Mapping:** `sentence-transformers/all-MiniLM-L6-v2` (Local SBERT)
    *   **Question Generation:** `google/flan-t5-base` (Local LLM)

---

## 💻 Prerequisites

Before starting, ensure your machine has the following installed:
*   **Python 3.9+**
*   **Node.js 18+** & **npm**
*   **Git**

---

## 🛠️ Step-by-Step Setup Guide

Follow these instructions to get the application running from A to Z on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/VINAYAK28x/AQPG.git
cd AQPG
```

### 2. Backend Setup (Python Virtual Environment)
You **must** use a virtual environment to isolate the heavy Machine Learning dependencies.

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment named `venv`:
   ```bash
   # On Mac/Linux
   python3 -m venv venv
   
   # On Windows
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   # On Mac/Linux
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```
4. Install all required dependencies (this may take a few minutes as it downloads PyTorch and Transformers):
   ```bash
   pip install -r ../requirements.txt
   ```

### 3. Machine Learning Models Setup 🧠
Because AQPG runs 100% locally for data privacy, it relies on open-source HuggingFace models. 

**Automatic Download (Recommended):**
The first time you run the FastAPI backend and trigger Semantic Mapping or Question Generation, the `transformers` library will **automatically download the model weights** (~1.2GB total) from the HuggingFace hub and cache them in your system's default hidden cache folder (e.g., `~/.cache/huggingface/hub/` on Mac/Linux). **You must be connected to the internet the very first time you use the app.**

**Manual/Offline Setup:**
If you need the system to be completely air-gapped without internet access:
1. Download `all-MiniLM-L6-v2` and `flan-t5-base` manually on a separate machine.
2. Place the model folders inside the root `models/` directory.
3. Update `backend/app/core/config.py` to point to `../models/flan-t5-base`.

### 4. Running the Backend Server
While inside the `backend` folder with your `venv` activated, start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```
*The backend is now actively listening on `http://127.0.0.1:8000`.*

### 5. Frontend Setup (React)
Open a **new terminal window** (leave the backend running in the first one) and navigate to the frontend folder:
```bash
cd frontend
```
Install the Node dependencies:
```bash
npm install
```
Start the React development server:
```bash
npm start
```
*The React app will automatically open in your browser at `http://localhost:3000`.*

---

## 🎓 How to Use the Application (A to Z)

Once both the Frontend and Backend are running, use the UI to generate your exam:

1. **Step 1: Syllabus Upload**
   Upload your university's Syllabus PDF. The AI will parse the document and extract the distinct examination headings and modules.
2. **Step 2: Textbook Upload**
   Upload the source Textbook PDF (this can be hundreds of pages). `PyMuPDF` will intelligently chunk the paragraphs contextually into manageable blocks.
3. **Step 3: Semantic Mapping**
   Click the mapping button. The local SBERT model will mathematically calculate vector embeddings for every syllabus topic and every textbook chunk. It will map the most relevant textbook paragraphs to specific syllabus topics. *(Note: This process takes 10-30 seconds depending on textbook size).*
4. **Step 4: Pattern Configuration**
   Define your Exam Name, add Examination Parts (e.g., "PART A", "PART B"), assign standard marks for each section, and select the target Bloom's Taxonomy cognitive level (e.g., "Remember", "Analyze").
5. **Step 5: Generate Questions**
   The application will pass the required specifications and the isolated textbook context directly to the local `Flan-T5` model to synthetically generate new exam questions. Once complete, you can review the generated exam paper.

---

## 🔒 Security & Data Privacy
Because all data processing (Chunking, Vectorizing, Generation) happens **on your device**, this application is safe for processing proprietary or copyrighted textbooks. No document text is ever sent to OpenAI, Anthropic, or external cloud providers.
