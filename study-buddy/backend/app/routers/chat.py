"""
Chat Router — AI-Powered Study Buddy (Agent-Powered)
======================================================
POST /chat/  → Intent-classified, agent-routed Q&A
GET  /chat/history → Retrieve conversation history
DELETE /chat/history → Clear session memory
"""

from __future__ import annotations

import asyncio
from functools import partial

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agent_router import AgentRouter
from app.ai.memory_manager import clear_session_memory
from app.dependencies import get_current_user, get_db
from app.repositories.session_repo import SessionRepository
from app.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

# Singleton AgentRouter (shared across requests — agents are stateless)
_agent_router = AgentRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Intelligent chat endpoint.

    - Classifies user intent (ask/quiz/summary/flashcard/teach)
    - Routes to the appropriate AI agent
    - Returns a grounded, validated answer
    - Persists Q&A to chat history
    """
    # Run the synchronous agent pipeline in a thread-pool executor so the
    # async event loop is never blocked (Gemini calls take 1-4 seconds).
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        partial(
            _agent_router.route,
            user_id=current_user.id,
            message=request.question,
            doc_ids=request.document_ids,
            doc_id=request.document_ids[0] if request.document_ids else None,
        ),
    )

    # Persist to database
    repo = SessionRepository(db)
    await repo.save_chat(
        user_id=current_user.id,
        document_id=request.document_ids[0] if request.document_ids else None,
        question=request.question,
        answer=result.get("answer", ""),
        sources=str(result.get("sources", [])),
        intent=result.get("intent", "ask"),
    )

    return ChatResponse(
        answer=result.get("answer", ""),
        sources=result.get("sources", []),
        intent=result.get("intent", "ask"),
        latency_ms=result.get("latency_ms", 0),
    )


@router.get("/history")
async def get_history(
    limit: int = 20,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Return the user's recent chat history from the database."""
    repo    = SessionRepository(db)
    history = await repo.recent_chats(current_user.id, limit=limit)
    return [
        {
            "id":         h.id,
            "question":   h.question,
            "answer":     h.answer,
            "intent":     h.intent,
            "sources":    h.sources,
            "created_at": str(h.created_at),
        }
        for h in history
    ]


@router.delete("/history", status_code=204)
async def clear_history(current_user=Depends(get_current_user)) -> None:
    """Clear in-process session memory for the current user."""
    clear_session_memory(current_user.id)
