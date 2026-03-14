# Backend — Models / Schemas (`backend/app/models/`)

> **For developers & agents:** This document describes the `models/` directory — Pydantic schemas that define the shape of all API request/response payloads.

---

## Directory Overview

```
backend/app/models/
├── __init__.py    # Package init (empty)
└── schemas.py     # All Pydantic models for the exam pattern
```

---

## `__init__.py`

Empty package initializer. Makes `models/` importable as `app.models`.

---

## `schemas.py`

Contains the Pydantic request body schemas used by the Questions API endpoints (`/set-question-pattern` and `/generate-questions`). These schemas validate incoming JSON payloads and provide type safety throughout the backend.

### Schema Hierarchy

```
ExamPattern
├── exam_name: str
└── parts: List[PartPattern]
         ├── part_name: str
         ├── answer_type: str          ("ALL" | "ANY")
         ├── marks_per_question: int
         ├── total_questions: int
         ├── questions_to_answer: Optional[int]
         ├── bloom_levels: List[str]
         └── questions: Optional[List[QuestionPattern]]
                  ├── question_no: int
                  ├── marks: int
                  ├── module: str
                  ├── bloom_level: Optional[str]   (default: "Remember")
                  ├── has_internal_choice: bool     (default: False)
                  ├── or_choice: Optional[dict]     (configuration for OR question)
                  └── sub_questions: Optional[List[SubQuestionPattern]]
                           ├── label: str
                           └── marks: int
```

### `SubQuestionPattern`

Represents a sub-question within a question (e.g., parts a, b, c).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `str` | required | Sub-question label (e.g., `"a"`, `"b"`) |
| `marks` | `int` | required | Marks allocated to this sub-question |

### `QuestionPattern`

Represents a single question in the exam pattern.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `question_no` | `int` | required | Sequential question number |
| `marks` | `int` | required | Total marks for this question |
| `module` | `str` | required | Module the question targets (e.g., `"Module 1"`) |
| `bloom_level` | `Optional[str]` | `"Remember"` | Target Bloom's taxonomy level |
| `has_internal_choice` | `bool` | `False` | Whether the question has OR-type internal choices |
| `or_choice` | `Optional[dict]` | `None` | Configuration object `{"marks": int, "module": str}` for the alternative OR question |
| `sub_questions` | `Optional[List[SubQuestionPattern]]` | `None` | Sub-questions, if any |

### `PartPattern`

Represents a part of the exam (e.g., PART A, PART B).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `part_name` | `str` | required | Name of the part (e.g., `"PART A"`) |
| `answer_type` | `str` | required | `"ALL"` (answer all) or `"ANY"` (answer N of M) |
| `marks_per_question` | `int` | required | Default marks per question in this part |
| `total_questions` | `int` | required | Total number of questions in this part |
| `questions_to_answer` | `Optional[int]` | `None` | If `answer_type=ANY`, how many must be answered |
| `bloom_levels` | `List[str]` | required | Bloom's taxonomy levels applicable to this part |
| `questions` | `Optional[List[QuestionPattern]]` | `None` | Individual question specifications |

### `ExamPattern`

Top-level schema for the entire exam pattern — this is the request body for both `/set-question-pattern` and `/generate-questions`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `exam_name` | `str` | required | Name of the exam (e.g., `"Mid Semester Exam"`) |
| `parts` | `List[PartPattern]` | required | The exam parts |

### Example JSON Payload

```json
{
  "exam_name": "Mid Semester Exam",
  "parts": [
    {
      "part_name": "PART A",
      "answer_type": "ALL",
      "marks_per_question": 2,
      "total_questions": 5,
      "bloom_levels": ["Remember", "Understand"],
      "questions": [
        {
          "question_no": 1,
          "marks": 2,
          "module": "Module I",
          "bloom_level": "Remember",
          "has_internal_choice": true,
          "or_choice": {
            "marks": 2,
            "module": "Module I"
          }
        }
      ]
    }
  ]
}
```

---

## Bloom's Taxonomy Levels (Valid Values)

The following string values are expected for `bloom_level` and `bloom_levels`:
- `"Remember"`
- `"Understand"`
- `"Apply"`
- `"Analyze"`
- `"Evaluate"`
- `"Create"`

---

## Agent Notes

- These schemas are **only used by the Questions API** (`questions.py`). Syllabus and textbook endpoints use raw `UploadFile` inputs and return untyped dicts.
- `sub_questions` is defined in the schema but is **not currently used** in the question generation logic — it exists for future expansion.
- `questions_to_answer` is also not used in generation logic but is part of the pattern structure for frontend display purposes.
- If you need to add new fields to the exam pattern, modify these schemas first — FastAPI will auto-validate and auto-document them in the OpenAPI spec.
