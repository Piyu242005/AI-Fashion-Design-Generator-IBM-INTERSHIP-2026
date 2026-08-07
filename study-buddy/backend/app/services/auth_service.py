"""
Auth Service — AI-Powered Study Buddy
=======================================
Business logic for user registration and login.
Keeps all auth rules here — routers stay thin.
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions import UnauthorizedError, ValidationError
from app.repositories.user_repo import UserRepository
from app.schemas import TokenResponse, UserOut, UserRegister

logger = logging.getLogger("study_buddy.auth_service")


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = UserRepository(db)

    async def register(self, data: UserRegister) -> UserOut:
        """
        Create a new user account.

        Raises:
            ValidationError: If email is already registered.
        """
        existing = await self._repo.get_by_email(data.email)
        if existing:
            raise ValidationError("An account with this email already exists.")

        hashed = hash_password(data.password)
        user   = await self._repo.create(
            name=data.name,
            email=data.email,
            hashed_password=hashed,
        )
        logger.info("New user registered: id=%d email=%s", user.id, user.email)

        doc_count = await self._repo.count_documents(user.id)
        out = UserOut.model_validate(user)
        out.document_count = doc_count
        return out

    async def login(self, email: str, password: str) -> TokenResponse:
        """
        Authenticate user and return a JWT access token.

        Raises:
            UnauthorizedError: If credentials are invalid.
        """
        user = await self._repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedError("Account is disabled.")

        token = create_access_token({"sub": str(user.id)})
        logger.info("User logged in: id=%d", user.id)
        return TokenResponse(access_token=token)

    async def get_profile(self, user_id: int) -> UserOut:
        """Return full user profile with computed stats."""
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedError()

        doc_count = await self._repo.count_documents(user_id)
        out = UserOut.model_validate(user)
        out.document_count = doc_count
        return out
