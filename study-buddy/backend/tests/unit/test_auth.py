"""
Unit Tests — Auth Service
==========================
Tests for user registration, login, and JWT token logic.
Uses pytest-asyncio for async test support.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.schemas import UserRegister


# ---------------------------------------------------------------------------
# Security utility tests (sync — no DB needed)
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("mysecret123")
        assert hashed != "mysecret123"
        assert len(hashed) > 30

    def test_verify_correct_password(self):
        hashed = hash_password("correct_password")
        assert verify_password("correct_password", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_two_hashes_differ(self):
        """bcrypt uses random salt — same input gives different hashes."""
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token({"sub": "42"})
        payload = decode_access_token(token)
        assert payload["sub"] == "42"

    def test_token_contains_exp(self):
        token = create_access_token({"sub": "1"})
        payload = decode_access_token(token)
        assert "exp" in payload

    def test_invalid_token_raises(self):
        from jose import JWTError
        with pytest.raises(JWTError):
            decode_access_token("not.a.valid.token")


# ---------------------------------------------------------------------------
# UserRegister schema validation tests
# ---------------------------------------------------------------------------

class TestUserRegisterSchema:
    def test_valid_registration(self):
        data = UserRegister(name="Alice Smith", email="alice@example.com", password="securepass1")
        assert data.name == "Alice Smith"
        assert data.email == "alice@example.com"

    def test_password_too_short(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UserRegister(name="Alice", email="a@b.com", password="short")

    def test_invalid_email(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UserRegister(name="Alice", email="not-an-email", password="validpass1")

    def test_name_too_short(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UserRegister(name="A", email="a@b.com", password="validpass1")
