"""
api/try-on.py
=============
Vercel Python Serverless Function — POST /api/try-on

Accepts a multipart/form-data request with:
    person   — full-body person photo (JPEG / PNG / WebP, ≤ 10 MB)
    garment  — garment / clothing item image  (JPEG / PNG / WebP, ≤ 10 MB)

Returns JSON:
    { "success": true,  "image": "data:image/jpeg;base64,…", "provider": "idm-vton" }
    { "success": false, "error": { "code": "…", "message": "…" } }

How it works
------------
This function forwards the two uploaded images to the Hugging Face
IDM-VTON Gradio Space (yisol/IDM-VTON).  The Space runs on ZeroGPU and
goes to sleep after inactivity — so the connection is retried up to
CONNECT_RETRIES times with a short back-off before giving up.

Required Vercel Environment Variables:
    HF_TOKEN    — HuggingFace READ token (higher ZeroGPU quota)
    HF_SPACE_ID — optional, defaults to "yisol/IDM-VTON"
"""

from __future__ import annotations

import base64
import cgi
import io
import json
import logging
import os
import tempfile
import time
from http.server import BaseHTTPRequestHandler
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SPACE_ID            = os.getenv("HF_SPACE_ID", "yisol/IDM-VTON")
CONNECT_RETRIES     = 3
CONNECT_RETRY_DELAY = 10   # seconds
MAX_BYTES           = 10 * 1024 * 1024   # 10 MB per image
ALLOWED_TYPES       = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _json_error(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


def _ext_from_type(content_type: str) -> str:
    ct = (content_type or "").lower()
    if "jpeg" in ct or "jpg" in ct:
        return "jpg"
    if "png" in ct:
        return "png"
    if "webp" in ct:
        return "webp"
    return "jpg"


def _is_sleeping(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(k in msg for k in (
        "loading", "503", "unavailable", "space is sleeping",
        "waking up", "starting", "connection", "connect",
    ))


def _run_tryon(person_bytes: bytes, garment_bytes: bytes,
               person_ext: str, garment_ext: str) -> dict:
    """
    Synchronous wrapper around the gradio_client call.
    Returns the same dict shape as the JSON response.
    """
    try:
        from gradio_client import Client, handle_file  # type: ignore
    except ImportError:
        logger.error("gradio_client not installed.")
        return _json_error("DEPENDENCY_MISSING", "Virtual try-on failed. Please try again.")

    hf_token = os.getenv("HF_TOKEN", "").strip() or None
    if not hf_token:
        logger.warning("HF_TOKEN not set — using unauthenticated ZeroGPU quota.")

    with tempfile.TemporaryDirectory() as tmpdir:
        person_path  = Path(tmpdir) / f"person.{person_ext}"
        garment_path = Path(tmpdir) / f"garment.{garment_ext}"
        person_path.write_bytes(person_bytes)
        garment_path.write_bytes(garment_bytes)

        # ── Connect with retry ───────────────────────────────────────────────
        client = None
        last_exc: Exception | None = None

        for attempt in range(1, CONNECT_RETRIES + 1):
            try:
                logger.info("Connecting to %s (attempt %d/%d)…", SPACE_ID, attempt, CONNECT_RETRIES)
                client = Client(SPACE_ID, hf_token=hf_token)
                last_exc = None
                break
            except Exception as exc:
                last_exc = exc
                logger.warning("Connect attempt %d/%d failed: %s", attempt, CONNECT_RETRIES, str(exc)[:120])
                if attempt < CONNECT_RETRIES:
                    logger.info("Waiting %d s (Space may be waking up)…", CONNECT_RETRY_DELAY)
                    time.sleep(CONNECT_RETRY_DELAY)

        if client is None:
            if last_exc and _is_sleeping(last_exc):
                return _json_error(
                    "SPACE_LOADING",
                    "The IDM-VTON space is waking up from sleep. Please wait 30–60 seconds and try again.",
                )
            return _json_error(
                "SPACE_UNAVAILABLE",
                "IDM-VTON space is unreachable. Please try again shortly.",
            )

        # ── Submit job ───────────────────────────────────────────────────────
        try:
            job = client.submit(
                dict={
                    "background": handle_file(str(person_path)),
                    "layers":     [],
                    "composite":  None,
                },
                garm_img=handle_file(str(garment_path)),
                garment_des="",
                is_checked=True,
                is_checked_crop=False,
                denoise_steps=30,
                seed=42,
                api_name="/tryon",
            )
            outputs = job.result()
        except Exception as exc:
            err_str = str(exc).lower()
            logger.error("IDM-VTON job error: %s — %s", type(exc).__name__, str(exc)[:120])
            if any(k in err_str for k in ("quota", "exceeded", "limit")):
                return _json_error("QUOTA_EXCEEDED",
                                   "ZeroGPU daily quota reached. Try again tomorrow.")
            if any(k in err_str for k in ("loading", "503", "unavailable")):
                return _json_error("SPACE_LOADING",
                                   "IDM-VTON space is loading. Wait ~30 s and retry.")
            if "timeout" in err_str:
                return _json_error("TIMEOUT",
                                   "IDM-VTON timed out. The ZeroGPU queue may be busy — please retry.")
            return _json_error("TRYON_FAILED", "Virtual try-on failed. Please try again.")

        # ── Read result ──────────────────────────────────────────────────────
        try:
            result_path  = outputs[0] if isinstance(outputs, (list, tuple)) else outputs
            result_bytes = Path(result_path).read_bytes()
            b64  = base64.b64encode(result_bytes).decode("utf-8")
            mime = "image/jpeg" if result_bytes[:2] == b"\xff\xd8" else "image/png"
            return {"success": True, "image": f"data:{mime};base64,{b64}", "provider": "idm-vton"}
        except Exception as exc:
            logger.error("Could not read IDM-VTON result: %s", exc)
            return _json_error("PARSE_ERROR", "Virtual try-on failed. Please try again.")


# ---------------------------------------------------------------------------
# Vercel handler
# ---------------------------------------------------------------------------

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

    def do_POST(self) -> None:
        content_type = self.headers.get("Content-Type", "")
        length       = int(self.headers.get("Content-Length", 0))
        raw_body     = self.rfile.read(length) if length else b""

        # ── Parse multipart form ─────────────────────────────────────────────
        environ = {
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE":   content_type,
            "CONTENT_LENGTH": str(length),
        }
        try:
            form = cgi.FieldStorage(
                fp      = io.BytesIO(raw_body),
                headers = self.headers,
                environ = environ,
            )
        except Exception:
            self._send_json(400, _json_error("BAD_REQUEST", "Could not parse multipart form data."))
            return

        person_field  = form.get("person")
        garment_field = form.get("garment")

        if person_field is None or garment_field is None:
            self._send_json(400, _json_error(
                "MISSING_FILES",
                "Both 'person' and 'garment' image fields are required.",
            ))
            return

        person_bytes  = person_field.file.read()   if hasattr(person_field,  "file") else b""
        garment_bytes = garment_field.file.read()  if hasattr(garment_field, "file") else b""

        if not person_bytes or not garment_bytes:
            self._send_json(400, _json_error("EMPTY_FILE", "One or both uploaded files are empty."))
            return

        if len(person_bytes) > MAX_BYTES or len(garment_bytes) > MAX_BYTES:
            self._send_json(413, _json_error("FILE_TOO_LARGE", "Each image must be under 10 MB."))
            return

        person_ext  = _ext_from_type(getattr(person_field,  "type", ""))
        garment_ext = _ext_from_type(getattr(garment_field, "type", ""))

        logger.info(
            "POST /api/try-on  person=%d B  garment=%d B",
            len(person_bytes), len(garment_bytes),
        )

        # ── Call IDM-VTON ─────────────────────────────────────────────────────
        result = _run_tryon(person_bytes, garment_bytes, person_ext, garment_ext)

        if result.get("success"):
            self._send_json(200, result)
        else:
            code = result.get("error", {}).get("code", "")
            status_map = {
                "QUOTA_EXCEEDED":     429,
                "SPACE_LOADING":      503,
                "SPACE_UNAVAILABLE":  503,
                "DEPENDENCY_MISSING": 500,
                "TIMEOUT":            504,
            }
            self._send_json(status_map.get(code, 500), result)
