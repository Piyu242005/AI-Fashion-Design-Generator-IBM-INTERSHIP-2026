"""
Auth Router — AI-Powered Study Buddy
=======================================
Endpoints:
  POST /auth/register  → create new user
  POST /auth/login     → OAuth2 password flow → JWT
  GET  /auth/me        → return current user profile
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.schemas import TokenResponse, UserOut, UserRegister
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """Register a new student account."""
    return await AuthService(db).register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db:   AsyncSession              = Depends(get_db),
) -> TokenResponse:
    """
    OAuth2 password flow login.
    Returns a JWT access token valid for ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    return await AuthService(db).login(form.username, form.password)


@router.get("/me", response_model=UserOut)
async def get_me(current_user=Depends(get_current_user)) -> UserOut:
    """Return the authenticated user's profile."""
    from app.schemas import UserOut as UO
    out = UO.model_validate(current_user)
    return out
