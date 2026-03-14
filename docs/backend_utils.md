# Backend — Utilities (`backend/app/utils/`)

> **For developers & agents:** This document describes the `utils/` directory — low-level helper functions for PDF text extraction and image handling.

---

## Directory Overview

```
backend/app/utils/
├── __init__.py       # Package init (empty)
├── pdf_utils.py      # PyMuPDF text extraction + quality validation
└── image_utils.py    # Image extraction from PDFs + chunk-to-image mapping
```

---

## `__init__.py`

Empty package initializer.

---

## `pdf_utils.py`

Low-level PDF text extraction using **PyMuPDF (`fitz`)**. Shared by both the ingestion and syllabus services.

### Functions

#### `extract_full_text(pdf_bytes: bytes) → str`
Extracts all text from every page of a PDF and concatenates it with newlines. Uses `page.get_text("text")`.

#### `extract_text_by_page(pdf_bytes: bytes) → List[Tuple[int, str]]`
Extracts text page-by-page, returning a list of `(page_number, page_text)` tuples. Page numbers are **1-indexed**.

#### `is_valid_extracted_text(text: str) → bool`
Quality gate for extracted text. Returns `False` (triggering OCR fallback) if:
- Text is empty or under 300 characters.
- Contains more than 3 occurrences of garbage patterns: `"hidden page"`, `"this page intentionally left blank"`, `"digitized by"`, `"scanned by"`, `"copyright"`.
- **Word diversity ratio** is below 0.25 (i.e., fewer than 25% unique words — indicates OCR noise or gibberish).

> **Agent note:** If OCR is being triggered unexpectedly, check and adjust the thresholds in this function. The 300-character minimum and 0.25 diversity ratio may need tuning for very short documents.

**Used by:** `ingestion_service.extract_text()`

---

## `image_utils.py`

Extracts images from PDFs and maps them to text chunks using page numbers.

### Functions

#### `extract_images_from_pdf(pdf_bytes: bytes, output_dir: str) → List[Dict]`
Extracts all embedded images from a PDF and saves them as files.

**Process:**
1. Opens the PDF via PyMuPDF.
2. For each page, calls `page.get_images(full=True)` to get image references.
3. For each image, extracts the raw bytes via `doc.extract_image(xref)`.
4. Saves to disk as `page_{N}_img_{M}.{ext}`.

**Output:** List of metadata dicts:
```python
{
    "image_id": "page_3_img_1.png",
    "page": 3,
    "path": "/absolute/path/to/image.png"
}
```

**Error handling:** If an individual image fails to extract, logs a warning and continues to the next.

#### `map_chunks_to_images(chunks: List[Dict], images: List[Dict]) → List[Dict]`
Associates images with text chunks based on matching page numbers.

**Algorithm:**
1. Builds an `image_map: Dict[page_number, List[image_meta]]` from the images list.
2. For each chunk, adds an `"images"` key with all images from that chunk's page (or an empty list if none).

**Mutates the input:** This function modifies the `chunks` list in-place by adding the `"images"` key.

**Output:** The same chunks list with added `images` field:
```python
{
    "chunk_id": 5,
    "page": 3,
    "text": "...",
    "images": [
        {"image_id": "page_3_img_1.png", "page": 3, "path": "..."}
    ]
}
```

---

## Utility Dependency Map

```
API Layer
└── textbook.py
    ├── ingestion_service.py
    │   └── pdf_utils.py         ← extract_full_text, extract_text_by_page, is_valid_extracted_text
    ├── chunking_service.py
    └── image_utils.py           ← extract_images_from_pdf, map_chunks_to_images

└── syllabus.py
    └── syllabus_service.py
        └── ingestion_service.py
            └── pdf_utils.py     ← extract_full_text, is_valid_extracted_text
```

---

## Agent Notes

- **PyMuPDF is the only PDF library used** — all text and image extraction flows through `fitz`. If you need to add table extraction or layout analysis, this is where it would go.
- `map_chunks_to_images` mutates the input list. Be aware of this if you're working with the chunks list elsewhere.
- Image extraction relies on embedded images in the PDF. It will **not** extract images from scanned pages (those are full-page raster images, not embedded "images" in the PDF spec sense).
