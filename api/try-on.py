"""
api/try-on.py
=============
Vercel Python Serverless Function — POST /api/try-on

Accepts multipart/form-data:
    person              — full-body person photo  (JPEG / PNG / WebP, ≤ 10 MB)
    garment             — garment / clothing item (JPEG / PNG / WebP, ≤ 10 MB)
    garment_description — optional text describing the garment (improves VTON quality)

Returns JSON:
    { "success": true,  "image": "data:image/jpeg;base64,…", "provider": "idm-vton" }
    { "success": false, "error": { "code": "…", "message": "…" } }

How it works
------------
Uses gradio_client to call the Hugging Face IDM-VTON Gradio Space.
gradio_client handles the ZeroGPU cold-start handshake and SSE queue protocol
automatically, so we only need to supply the parameters.

Required Vercel Environment Variables:
    HF_TOKEN    — HuggingFace READ token (strongly recommended)
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
from http.server import BaseHTTPRequestHandler
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SPACE_ID  = os.getenv("HF_SPACE_ID", "yisol/IDM-VTON")
MAX_BYTES = 10 * 1024 * 1024   # 10 MB per image

# How many times to retry connecting to the Space when it is sleeping/loading.
CONNECT_RETRIES     = 3
CONNECT_RETRY_DELAY = 15   # seconds between connection retries

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


def _is_space_sleeping(exc: Exception) -> bool:
    msg = str(exc).lower()
    return (
        "loading" in msg or "503" in msg or "unavailable" in msg
        or "space is sleeping" in msg or "waking up" in msg
        or "starting" in msg or "connection" in msg
    )


def _run_tryon(person_bytes: bytes, garment_bytes: bytes,
               person_ext: str, garment_ext: str,
               garment_description: str = "") -> dict:
    """
    Call IDM-VTON via gradio_client.  Handles ZeroGPU cold-starts with retries.
    """
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        logger.error("gradio_client not installed")
        return _json_error("DEPENDENCY_MISSING",
                           "Virtual try-on service is not configured. Please contact support.")

    hf_token = os.getenv("HF_TOKEN", "").strip() or None
    if not hf_token:
        logger.warning("HF_TOKEN not set — using unauthenticated quota.")

    with tempfile.TemporaryDirectory() as tmpdir:
        person_path  = Path(tmpdir) / f"person.{person_ext}"
        garment_path = Path(tmpdir) / f"garment.{garment_ext}"
        person_path.write_bytes(person_bytes)
        garment_path.write_bytes(garment_bytes)

        # ── Connect to Space (retry on cold-start) ───────────────────────────
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
                logger.warning("Connect attempt %d/%d failed: %s — %s",
                               attempt, CONNECT_RETRIES, type(exc).__name__, str(exc)[:120])
                if attempt < CONNECT_RETRIES:
                    import time
                    logger.info("Waiting %d s for Space to wake up…", CONNECT_RETRY_DELAY)
                    time.sleep(CONNECT_RETRY_DELAY)

        if client is None:
            logger.error("Cannot connect to %s after %d attempts", SPACE_ID, CONNECT_RETRIES)
            if last_exc and _is_space_sleeping(last_exc):
                return _json_error("SPACE_LOADING",
                                   "The IDM-VTON space is waking up from sleep. "
                                   "Please wait 30–60 seconds and try again.")
            return _json_error("SPACE_UNAVAILABLE",
                               "IDM-VTON space is unreachable. Please try again shortly.")

        # ── Submit job ───────────────────────────────────────────────────────
        try:
            job = client.submit(
                dict={
                    "background": handle_file(str(person_path)),
                    "layers":     [],
                    "composite":  None,
                },
                garm_img=handle_file(str(garment_path)),
                # A meaningful description improves garment representation
                garment_des=garment_description.strip() if garment_description else "",
                is_checked=True,
                # Enable auto-crop so the model handles varied person image compositions
                is_checked_crop=True,
                # 40 steps gives better quality while keeping latency reasonable
                denoise_steps=40,
                seed=42,
                api_name="/tryon",
            )
            outputs = job.result()

        except Exception as exc:
            err_str = str(exc).lower()
            logger.error("IDM-VTON job error: %s — %s", type(exc).__name__, str(exc)[:120])
            if "quota" in err_str or "exceeded" in err_str or "limit" in err_str:
                return _json_error("QUOTA_EXCEEDED",
                                   "ZeroGPU daily quota reached. Try again tomorrow.")
            if "loading" in err_str or "503" in err_str or "unavailable" in err_str:
                return _json_error("SPACE_LOADING",
                                   "IDM-VTON space is loading. Wait ~30 s and retry.")
            if "timeout" in err_str:
                return _json_error("TIMEOUT",
                                   "IDM-VTON timed out. The GPU queue is busy — please retry.")
            return _json_error("TRYON_FAILED",
                               "Virtual try-on failed. Please try again.")

        # ── Encode result image ──────────────────────────────────────────────
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

        person_field       = form.get("person")
        garment_field      = form.get("garment")
        desc_field         = form.get("garment_description")
        garment_description = (desc_field.value if hasattr(desc_field, "value") else str(desc_field or "")).strip()

        if person_field is None or garment_field is None:
            self._send_json(400, _json_error(
                "MISSING_FILES",
                "Both 'person' and 'garment' image fields are required.",
            ))
            return

        person_bytes  = person_field.file.read()  if hasattr(person_field,  "file") else b""
        garment_bytes = garment_field.file.read() if hasattr(garment_field, "file") else b""

        if not person_bytes or not garment_bytes:
            self._send_json(400, _json_error("EMPTY_FILE", "One or both uploaded files are empty."))
            return

        if len(person_bytes) > MAX_BYTES or len(garment_bytes) > MAX_BYTES:
            self._send_json(413, _json_error("FILE_TOO_LARGE", "Each image must be under 10 MB."))
            return

        person_ext  = _ext_from_type(getattr(person_field,  "type", ""))
        garment_ext = _ext_from_type(getattr(garment_field, "type", ""))

        logger.info("POST /api/try-on  person=%d B  garment=%d B  desc=%r  space=%s",
                    len(person_bytes), len(garment_bytes), garment_description[:60], SPACE_ID)

        # ── Call IDM-VTON ─────────────────────────────────────────────────────
        result = _run_tryon(person_bytes, garment_bytes, person_ext, garment_ext, garment_description)

        if result.get("success"):
            self._send_json(200, result)
        else:
            code = result.get("error", {}).get("code", "")
            status_map = {
                "QUOTA_EXCEEDED":     429,
                "SPACE_LOADING":      503,
                "SPACE_UNAVAILABLE":  503,
                "TIMEOUT":            504,
            }
            self._send_json(status_map.get(code, 500), result)
