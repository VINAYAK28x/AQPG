"""
Pydantic schemas for the API request/response models.
Consolidated from the old pattern/ package.
"""

from pydantic import BaseModel
from typing import List, Optional


class SubQuestionPattern(BaseModel):
    """Schema for sub-questions within a question (e.g., a, b, c)."""
    label: str
    marks: int


class QuestionPattern(BaseModel):
    """Schema for a single question in the exam pattern."""
    question_no: int
    marks: int
    module: str
    bloom_level: Optional[str] = "Remember"
    has_internal_choice: bool = False
    sub_questions: Optional[List[SubQuestionPattern]] = None


class PartPattern(BaseModel):
    """Schema for a part of the exam (e.g., PART A, PART B)."""
    part_name: str
    answer_type: str               # "ALL" or "ANY"
    marks_per_question: int
    total_questions: int
    questions_to_answer: Optional[int] = None
    bloom_levels: List[str]
    questions: Optional[List[QuestionPattern]] = None


class ExamPattern(BaseModel):
    """Top-level schema for the entire exam pattern."""
    exam_name: str
    parts: List[PartPattern]
