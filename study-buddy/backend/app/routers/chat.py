"""
Chat Router — AI-Powered Study Buddy
=======================================
POST /chat/  → RAG-powered Q&A
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    RAG Q&A endpoint.
    Retrieves relevant document chunks and generates a grounded answer via Gemini.
    """
    # Read user preferences for style personalisation
    return await RAGService(db).answer(
        user_id=current_user.id,
        request=request,
    )
