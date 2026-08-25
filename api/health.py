"""
api/health.py
=============
Vercel Python Serverless Function — GET /api/health

Returns non-secret service readiness information for monitoring and debugging.
"""

from http.server import BaseHTTPRequestHandler
import json
import os

SERVICE_VERSION = os.environ.get("APP_VERSION", "1.0.0")
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def _configured(*names: str) -> bool:
    return all(os.environ.get(name, "").strip() for name in names)


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()

    def do_GET(self) -> None:
        services = {
            "cloudflare": _configured("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN"),
            "gemini": _configured("GEMINI_API_KEY"),
            "huggingface": _configured("HF_TOKEN"),
            "rapidapi": _configured("RAPIDAPI_KEY"),
        }
        ready = services["cloudflare"] and services["gemini"]
        self._send_json(200 if ready else 503, {
            "status": "ok" if ready else "degraded",
            "service": "ai-fashion-design-generator",
            "version": SERVICE_VERSION,
            "services": services,
        })
