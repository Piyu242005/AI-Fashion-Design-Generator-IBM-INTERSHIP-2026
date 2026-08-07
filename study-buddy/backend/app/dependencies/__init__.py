"""
FastAPI Dependencies — AI-Powered Study Buddy
===============================================
Reusable Depends() callables for:
  - DB session injection
  - Current authenticated user extraction
"""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database import AsyncSessionLocal
from app.exceptions import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------------------------------------------------------------------------
# DB Session
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an async database session per request.
    Automatically closed after response.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Current User
# ---------------------------------------------------------------------------

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Decode JWT and return the authenticated User ORM object.
    Raises UnauthorizedError if token is invalid or user not found.
    """
    from app.repositories.user_repo import UserRepository  # avoid circular

    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError()
    except JWTError:
        raise UnauthorizedError("Invalid or expired token.")

    repo = UserRepository(db)
    user = await repo.get_by_id(int(user_id))
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive.")
    return user
