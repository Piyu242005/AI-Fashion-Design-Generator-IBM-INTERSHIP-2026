"""API Client — AI-Powered Study Buddy
All HTTP calls from Streamlit frontend to FastAPI backend.
"""
from __future__ import annotations
import os
from typing import Any, Optional
import httpx

API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
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
        return _handle_response(c.post(f"{API_BASE_URL}/auth/register",
            json={"name": name, "email": email, "password": password}))

def login_user(email: str, password: str) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.post(f"{API_BASE_URL}/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}))

def get_profile(token: str) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.get(f"{API_BASE_URL}/auth/me", headers=_headers(token)))

def upload_document(token: str, file_bytes: bytes, filename: str) -> dict:
    with httpx.Client(timeout=60) as c:
        return _handle_response(c.post(f"{API_BASE_URL}/documents/upload",
            files={"file": (filename, file_bytes)},
            headers={"Authorization": f"Bearer {token}"}))

def list_documents(token: str) -> list:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.get(f"{API_BASE_URL}/documents/", headers=_headers(token)))

def delete_document(token: str, doc_id: int) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.delete(f"{API_BASE_URL}/documents/{doc_id}", headers=_headers(token)))

def send_chat_message(token: str, question: str, doc_ids: list[int]) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.post(f"{API_BASE_URL}/chat/",
            json={"question": question, "document_ids": doc_ids}, headers=_headers(token)))

def generate_summary(token: str, doc_id: int, style: str = "bullet") -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.post(f"{API_BASE_URL}/summary/",
            json={"document_id": doc_id, "style": style}, headers=_headers(token)))

def generate_quiz(token: str, doc_id: int, num_questions: int = 5, qtype: str = "mcq") -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.post(f"{API_BASE_URL}/quiz/generate",
            json={"document_id": doc_id, "num_questions": num_questions,
                  "question_type": qtype}, headers=_headers(token)))

def generate_flashcards(token: str, doc_id: int, count: int = 10) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.post(f"{API_BASE_URL}/flashcards/generate",
            json={"document_id": doc_id, "count": count}, headers=_headers(token)))

def get_dashboard_stats(token: str) -> dict:
    with httpx.Client(timeout=TIMEOUT) as c:
        return _handle_response(c.get(f"{API_BASE_URL}/dashboard/stats", headers=_headers(token)))
