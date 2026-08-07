"""
Quiz Router — AI-Powered Study Buddy
=======================================
POST /quiz/generate  → generate quiz questions
POST /quiz/submit    → save a completed quiz result
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.schemas import QuizRequest, QuizResponse, QuizSubmitRequest
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizResponse:
    """Generate quiz questions from a document using Gemini."""
    return await QuizService(db).generate(current_user.id, request)


@router.post("/submit")
async def submit_quiz(
    request: QuizSubmitRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Save quiz result and update topic scores for recommendations."""
    return await QuizService(db).submit_result(current_user.id, request)
