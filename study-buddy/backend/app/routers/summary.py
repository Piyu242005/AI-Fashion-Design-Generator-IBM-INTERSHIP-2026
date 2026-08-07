"""
Summary Router — AI-Powered Study Buddy
POST /summary/  → generate a document summary
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.schemas import SummaryRequest, SummaryResponse
from app.services.summary_service import SummaryService

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.post("/", response_model=SummaryResponse)
async def summarise(
    request: SummaryRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SummaryResponse:
    """Generate a bullet-point or paragraph summary of a document."""
    return await SummaryService(db).summarise(current_user.id, request)
