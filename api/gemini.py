"""
api/gemini.py
=============
Vercel Python Serverless Function — POST /api/gemini

Server-side Gemini text extraction for fashion specifications.
The Gemini API key NEVER reaches the browser.

Required environment variables:
    GEMINI_API_KEY
    GEMINI_MODEL (optional; defaults to gemini-2.5-flash)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler

DEFAULT_MODEL = "gemini-2.5-flash"
MAX_PROMPT_LENGTH = 500
CF_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

SCHEMA_PROMPT = (
    "Extract fashion details from the user's request and return JSON only. "
    'Schema: {"category":"","fabric":"","colors":["hex"],'
    '"sustainability_score":0,"budget":{"maximum":0},'
    '"garment_description":""}. '
    "Keep strings concise and use an empty string/array when unknown.\n\nUser request: "
)


def _send_json(handler: BaseHTTPRequestHandler, status: int, data: dict) -> None:
    body = json.dumps(data).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    for key, value in CF_HEADERS.items():
        handler.send_header(key, value)
    handler.end_headers()
    handler.wfile.write(body)


def _error(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def _call_gemini(prompt: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    if not api_key:
        return _error("CONFIGURATION_ERROR", "Gemini is not configured on the server.")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": SCHEMA_PROMPT + prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            return _error("RATE_LIMITED", "Gemini rate limit reached. Please try again shortly.")
        if exc.code in (400, 401, 403):
            return _error("AUTH_ERROR", "Gemini configuration or authorization failed.")
        return _error("UPSTREAM_ERROR", "Gemini could not process the request.")
    except Exception:
        return _error("NETWORK_ERROR", "Could not reach Gemini.")

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        spec = _extract_json(text)
        if not isinstance(spec, dict):
            raise ValueError("Gemini response was not an object")
        return {"success": True, "specification": spec}
    except Exception:
        return _error("PARSE_ERROR", "Gemini returned an invalid fashion specification.")


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        for key, value in CF_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length else b"{}"

        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            _send_json(self, 400, _error("INVALID_JSON", "Request body must be valid JSON."))
            return

        prompt = str(body.get("prompt") or "").strip()
        if len(prompt) < 2 or len(prompt) > MAX_PROMPT_LENGTH:
            _send_json(
                self,
                400,
                _error("VALIDATION_ERROR", f"Prompt must be between 2 and {MAX_PROMPT_LENGTH} characters."),
            )
            return

        result = _call_gemini(prompt)
        if result.get("success"):
            _send_json(self, 200, result)
            return

        code = result.get("error", {}).get("code", "")
        status = {
            "CONFIGURATION_ERROR": 500,
            "AUTH_ERROR": 500,
            "RATE_LIMITED": 429,
            "NETWORK_ERROR": 502,
            "UPSTREAM_ERROR": 502,
            "PARSE_ERROR": 502,
        }.get(code, 500)
        _send_json(self, status, result)
