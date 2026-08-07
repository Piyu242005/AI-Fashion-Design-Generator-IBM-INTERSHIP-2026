"""
Pydantic Schemas — AI-Powered Study Buddy
==========================================
Request / Response schemas for all API endpoints.
Pydantic v2 — uses model_config instead of class Config.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ============================================================================
# AUTH
# ============================================================================

class UserRegister(BaseModel):
    name:     str       = Field(..., min_length=2, max_length=120)
    email:    EmailStr
    password: str       = Field(..., min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def name_no_special(cls, v: str) -> str:
        if not v.replace(" ", "").isalpha():
            raise ValueError("Name must contain only letters and spaces.")
        return v.strip()


class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"


class UserOut(BaseModel):
    id:           int
    name:         str
    email:        str
    study_streak: int
    created_at:   datetime
    # Computed fields from joins (optional, filled by service)
    document_count: int  = 0
    quiz_count:     int  = 0
    avg_score:      float = 0.0

    model_config = {"from_attributes": True}


# ============================================================================
# DOCUMENTS
# ============================================================================

class DocumentOut(BaseModel):
    id:           int
    filename:     str
    file_type:    str
    file_size_kb: int
    chunk_count:  int
    status:       str
    uploaded_at:  datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    id:          int
    filename:    str
    chunk_count: int
    status:      str
    message:     str


# ============================================================================
# CHAT / RAG
# ============================================================================

class ChatRequest(BaseModel):
    question:     str       = Field(..., min_length=3, max_length=2000)
    document_ids: list[int] = Field(..., min_length=1)

    @field_validator("question")
    @classmethod
    def strip_question(cls, v: str) -> str:
        return v.strip()


class ChatResponse(BaseModel):
    answer:   str
    sources:  list[str]  = []
    intent:   str        = "ask"
    latency_ms: int      = 0


# ============================================================================
# SUMMARY
# ============================================================================

class SummaryRequest(BaseModel):
    document_id: int
    style:       str = Field(default="bullet", pattern="^(bullet|paragraph)$")
    detail:      str = Field(default="standard", pattern="^(brief|standard|detailed)$")


class SummaryResponse(BaseModel):
    document_id: int
    filename:    str
    summary:     str
    style:       str


# ============================================================================
# QUIZ
# ============================================================================

class QuizRequest(BaseModel):
    document_id:   int
    num_questions: int  = Field(default=5, ge=3, le=15)
    question_type: str  = Field(default="mcq",
                                 pattern="^(mcq|true_false|short_answer|mixed)$")
    difficulty:    str  = Field(default="medium",
                                 pattern="^(easy|medium|hard)$")
    topic:         Optional[str] = None


class QuizQuestion(BaseModel):
    question:    str
    options:     list[str]  = []   # empty for short_answer
    answer:      str
    explanation: str         = ""
    type:        str         = "mcq"


class QuizResponse(BaseModel):
    document_id:   int
    questions:     list[QuizQuestion]
    num_questions: int
    question_type: str
    difficulty:    str


class QuizSubmitRequest(BaseModel):
    document_id: int
    topic:       str        = "General"
    score_pct:   float      = Field(..., ge=0, le=100)
    num_questions: int


# ============================================================================
# FLASHCARDS
# ============================================================================

class FlashcardRequest(BaseModel):
    document_id: int
    count:       int = Field(default=10, ge=3, le=30)


class Flashcard(BaseModel):
    term:       str
    definition: str


class FlashcardsResponse(BaseModel):
    document_id: int
    flashcards:  list[Flashcard]
    count:       int


# ============================================================================
# DASHBOARD
# ============================================================================

class DashboardStats(BaseModel):
    document_count:    int
    total_study_mins:  int
    avg_quiz_score:    float
    study_streak:      int
    weak_topics:       list[str]
    strong_topics:     list[str]
    ai_suggestions:    list[str]
    recent_chats:      list[dict[str, Any]]
    recent_activity:   list[dict[str, Any]]
    topic_scores:      dict[str, int]
    flashcards_reviewed: int
    daily_goal_pct:    int
