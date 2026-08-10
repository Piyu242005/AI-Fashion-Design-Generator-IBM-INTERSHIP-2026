"""
api/health.py
=============
Vercel Python Serverless Function — GET /api/health
"""

from http.server import BaseHTTPRequestHandler
import json
import os

CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


class handler(BaseHTTPRequestHandler):

    def _send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self) -> None:
        cf_configured = bool(
            os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
            and os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
        )
        self._send_json(200, {
            "status":           "ok",
            "service":          "ai-fashion-design-generator",
            "cloudflare_ready": cf_configured,
        })
