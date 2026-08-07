"""
Dashboard Router — AI-Powered Study Buddy
GET /dashboard/stats  → return aggregated study stats
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.schemas import DashboardStats
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardStats:
    """Return aggregated dashboard statistics for the current user."""
    return await DashboardService(db).get_stats(current_user.id)
