"""API Client — AI-Powered Study Buddy
All HTTP calls from Streamlit frontend to FastAPI backend.
Updated to use /api/v1 versioned prefix.
"""
from __future__ import annotations
import os
import time
from typing import Any, Optional
import httpx

API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
_V1: str = f"{API_BASE_URL}/api/v1"   # All endpoints live under /api/v1
TIMEOUT: int = 30

def _headers(token: Optional[str] = None) -> dict[str, str]:
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def _handle_response(resp: httpx.Response) -> Any:
    try:
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        raise RuntimeError(detail) from e

def register_user(name: str, email: str, password: str) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.post(f"{_V1}/auth/register",
            json={"name": name, "email": email, "password": password}))

def login_user(email: str, password: str) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.post(f"{_V1}/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}))

def get_profile(token: str) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.get(f"{_V1}/auth/me", headers=_headers(token)))

def upload_document(token: str, file_bytes: bytes, filename: str) -> dict:
    """Upload file — backend returns 202 immediately; poll status for completion."""
    with httpx.Client(timeout=60) as c:
        return _handle_response(c.post(f"{_V1}/documents/upload",
            files={"file": (filename, file_bytes)},
            headers={"Authorization": f"Bearer {token}"}))

def poll_document_status(token: str, doc_id: int, max_wait: int = 60) -> dict:
    """
    Poll /documents/{id}/status until status != 'processing' or timeout.
    Returns the final status dict.
    """
    deadline = time.monotonic() + max_wait
    while time.monotonic() < deadline:
        with httpx.Client(timeout=TIMEOUT) as c:
            status = _handle_response(c.get(
                f"{_V1}/documents/{doc_id}/status",
                headers=_headers(token),
            ))
        if status.get("status") != "processing":
            return status
        time.sleep(2)
    return {"id": doc_id, "status": "processing", "chunk_count": 0}

def list_documents(token: str) -> list:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.get(f"{_V1}/documents/", headers=_headers(token)))

def delete_document(token: str, doc_id: int) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.delete(f"{_V1}/documents/{doc_id}", headers=_headers(token)))

def send_chat_message(token: str, question: str, doc_ids: list[int]) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.post(f"{_V1}/chat/",
            json={"question": question, "document_ids": doc_ids}, headers=_headers(token)))

def generate_summary(token: str, doc_id: int, style: str = "bullet") -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.post(f"{_V1}/summary/",
            json={"document_id": doc_id, "style": style}, headers=_headers(token)))

def generate_quiz(token: str, doc_id: int, num_questions: int = 5, qtype: str = "mcq") -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.post(f"{_V1}/quiz/generate",
            json={"document_id": doc_id, "num_questions": num_questions,
                  "question_type": qtype}, headers=_headers(token)))

def generate_flashcards(token: str, doc_id: int, count: int = 10) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.post(f"{_V1}/flashcards/generate",
            json={"document_id": doc_id, "count": count}, headers=_headers(token)))

def get_dashboard_stats(token: str) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.get(f"{_V1}/dashboard/stats", headers=_headers(token)))
