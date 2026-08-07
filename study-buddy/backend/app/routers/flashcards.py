"""
Flashcards Router — AI-Powered Study Buddy
POST /flashcards/generate  → generate flashcards from a document
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.schemas import FlashcardRequest, FlashcardsResponse
from app.services.flashcard_service import FlashcardService

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])


@router.post("/generate", response_model=FlashcardsResponse)
async def generate_flashcards(
    request: FlashcardRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlashcardsResponse:
    """Generate interactive flashcards from a document using Gemini."""
    return await FlashcardService(db).generate(current_user.id, request)
