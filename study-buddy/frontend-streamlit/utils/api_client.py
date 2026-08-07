"""
API Client — AI-Powered Study Buddy
====================================
All HTTP calls from Streamlit frontend to FastAPI backend.
Uses httpx for async-compatible sync requests with timeout handling,
auth header injection, and structured error responses.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx

# ---------------------------------------------------------------------------
# Base URL — reads from environment or defaults to localhost for dev
# ---------------------------------------------------------------------------
API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT: int = 30  # seconds


def _headers(token: Optional[str] = None) -> dict[str, str]:
    """Build standard request headers, injecting JWT if available."""
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _handle_response(resp: httpx.Response) -> dict[str, Any]:
    """Raise a descriptive error on non-2xx responses."""
    try:
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        raise RuntimeError(detail) from e


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def register_user(name: str, email: str, password: str) -> dict[str, Any]:
    """POST /auth/register"""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(
            f"{API_BASE_URL}/auth/register",
            json={"name": name, "email": email, "password": password},
        )
        return _handle_response(resp)


def login_user(email: str, password: str) -> dict[str, Any]:
    """POST /auth/login → returns {access_token, token_type}"""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(
            f"{API_BASE_URL}/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return _handle_response(resp)


def get_profile(token: str) -> dict[str, Any]:
    """GET /auth/me"""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.get(
            f"{API_BASE_URL}/auth/me", headers=_headers(token)
        )
        return _handle_response(resp)


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

def upload_document(token: str, file_bytes: bytes, filename: str) -> dict[str, Any]:
    """POST /documents/upload — multipart file upload."""
    with httpx.Client(timeout=60) as client:
        resp = client.post(
            f"{API_BASE_URL}/documents/upload",
            files={"file": (filename, file_bytes)},
            headers={"Authorization": f"Bearer {token}"},
        )
        return _handle_response(resp)


def list_documents(token: str) -> list[dict[str, Any]]:
    """GET /documents/"""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.get(
            f"{API_BASE_URL}/documents/", headers=_headers(token)
        )
        return _handle_response(resp)


def delete_document(token: str, doc_id: int) -> dict[str, Any]:
    """DELETE /documents/{doc_id}"""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.delete(
            f"{API_BASE_URL}/documents/{doc_id}", headers=_headers(token)
        )
        return _handle_response(resp)


# ---------------------------------------------------------------------------
# AI Features
# ---------------------------------------------------------------------------

def send_chat_message(token: str, question: str, doc_ids: list[int]) -> dict[str, Any]:
    """POST /chat/ — RAG Q&A"""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(
            f"{API_BASE_URL}/chat/",
            json={"question": question, "document_ids": doc_ids},
            headers=_headers(token),
        )
        return _handle_response(resp)


def generate_summary(token: str, doc_id: int, style: str = "bullet") -> dict[str, Any]:
    """POST /summary/ — document summarisation"""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(
            f"{API_BASE_URL}/summary/",
            json={"document_id": doc_id, "style": style},
            headers=_headers(token),
        )
        return _handle_response(resp)


def generate_quiz(token: str, doc_id: int, num_questions: int = 5, qtype: str = "mcq") -> dict[str, Any]:
    """POST /quiz/generate"""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(
            f"{API_BASE_URL}/quiz/generate",
            json={"document_id": doc_id, "num_questions": num_questions, "question_type": qtype},
            headers=_headers(token),
        )
        return _handle_response(resp)


def generate_flashcards(token: str, doc_id: int, count: int = 10) -> dict[str, Any]:
    """POST /flashcards/generate"""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(
            f"{API_BASE_URL}/flashcards/generate",
            json={"document_id": doc_id, "count": count},
            headers=_headers(token),
        )
        return _handle_response(resp)


def get_dashboard_stats(token: str) -> dict[str, Any]:
    """GET /dashboard/stats"""
    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.get(
            f"{API_BASE_URL}/dashboard/stats", headers=_headers(token)
        )
        return _handle_response(resp)
