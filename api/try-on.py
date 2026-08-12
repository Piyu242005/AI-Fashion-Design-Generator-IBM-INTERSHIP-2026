"""
api/try-on.py
=============
Vercel Python Serverless Function — POST /api/try-on

Accepts multipart/form-data:
    person   — full-body person photo  (JPEG / PNG / WebP, ≤ 10 MB)
    garment  — garment / clothing item (JPEG / PNG / WebP, ≤ 10 MB)

Returns JSON:
    { "success": true,  "image": "data:image/jpeg;base64,…", "provider": "idm-vton" }
    { "success": false, "error": { "code": "…", "message": "…" } }

How it works
------------
Calls the Hugging Face IDM-VTON Gradio Space entirely over HTTPS using
only Python stdlib (urllib + email.mime for multipart) — no gradio_client,
no websockets, no heavy dependencies.

Gradio REST flow (Gradio ≥ 3.x queue protocol):
  1. POST {space}/upload          → upload both images, get server-side paths
  2. POST {space}/queue/join      → enqueue the /tryon job, get event_id
  3. GET  {space}/queue/data      → SSE stream, read until process_completed

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
import random
import string
import time
import urllib.error
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from http.server import BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_RAW_SPACE   = os.getenv("HF_SPACE_ID", "yisol/IDM-VTON")
# Convert  "owner/repo"  →  "https://owner-repo.hf.space"
_SPACE_SLUG  = _RAW_SPACE.replace("/", "-").lower()
SPACE_BASE   = f"https://{_SPACE_SLUG}.hf.space"

MAX_BYTES    = 10 * 1024 * 1024   # 10 MB per image
POLL_TIMEOUT = 90                  # seconds to wait for the GPU job
POLL_SLEEP   = 3                   # seconds between status polls

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


def _session_hash() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=10))


def _hf_headers() -> dict:
    h: dict = {"Content-Type": "application/json"}
    token = os.getenv("HF_TOKEN", "").strip()
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _upload_image(image_bytes: bytes, filename: str) -> str:
    """
    Upload one image to the Gradio Space /upload endpoint.
    Returns the server-side file path string.
    """
    url = f"{SPACE_BASE}/upload"

    # Build a multipart/form-data body using email.mime
    boundary = "----GradioFormBoundary" + "".join(
        random.choices(string.ascii_letters + string.digits, k=16)
    )
    body_lines = []
    body_lines.append(f"--{boundary}\r\n")
    body_lines.append(
        f'Content-Disposition: form-data; name="files"; filename="{filename}"\r\n'
    )
    ext = filename.rsplit(".", 1)[-1].lower()
    mime_type = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    body_lines.append(f"Content-Type: {mime_type}\r\n")
    body_lines.append("\r\n")

    header_bytes = "".join(body_lines).encode()
    footer_bytes = f"\r\n--{boundary}--\r\n".encode()
    raw_body = header_bytes + image_bytes + footer_bytes

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(raw_body)),
    }
    token = os.getenv("HF_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=raw_body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    # Response is a list of file path strings
    return data[0] if isinstance(data, list) else data


def _run_tryon(person_bytes: bytes, garment_bytes: bytes,
               person_ext: str, garment_ext: str) -> dict:
    """
    Full Gradio REST flow: upload → enqueue → poll → decode result.
    """
    token = os.getenv("HF_TOKEN", "").strip()
    auth_header = {"Authorization": f"Bearer {token}"} if token else {}

    # ── 1. Upload both images ────────────────────────────────────────────────
    try:
        person_path  = _upload_image(person_bytes,  f"person.{person_ext}")
        garment_path = _upload_image(garment_bytes, f"garment.{garment_ext}")
        logger.info("Uploaded person=%s  garment=%s", person_path, garment_path)
    except urllib.error.HTTPError as exc:
        status = exc.code
        logger.error("Upload failed HTTP %d", status)
        if status in (503, 502):
            return _json_error("SPACE_LOADING",
                               "IDM-VTON space is waking up. Wait ~30 s and retry.")
        return _json_error("SPACE_UNAVAILABLE",
                           "IDM-VTON space is unreachable. Please try again shortly.")
    except Exception as exc:
        logger.error("Upload error: %s", exc)
        return _json_error("SPACE_UNAVAILABLE",
                           "IDM-VTON space is unreachable. Please try again shortly.")

    # ── 2. Enqueue the /tryon job ────────────────────────────────────────────
    session = _session_hash()
    payload = {
        "fn_index": 0,          # /tryon is fn_index 0 on yisol/IDM-VTON
        "session_hash": session,
        "data": [
            # param 0: dict — ImageEditor value (background = person image)
            {
                "background": {"path": person_path, "url": None, "orig_name": f"person.{person_ext}", "is_stream": False},
                "layers": [],
                "composite": None,
            },
            # param 1: garm_img
            {"path": garment_path, "url": None, "orig_name": f"garment.{garment_ext}", "is_stream": False},
            # param 2: garment_des
            "",
            # param 3: is_checked
            True,
            # param 4: is_checked_crop
            False,
            # param 5: denoise_steps
            30,
            # param 6: seed
            42,
        ],
    }

    try:
        join_url = f"{SPACE_BASE}/queue/join"
        req_headers = {"Content-Type": "application/json"}
        req_headers.update(auth_header)
        req = urllib.request.Request(
            join_url,
            data=json.dumps(payload).encode(),
            headers=req_headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            join_data = json.loads(resp.read())
        event_id = join_data.get("event_id")
        logger.info("Queued job event_id=%s session=%s", event_id, session)
    except Exception as exc:
        logger.error("Queue join failed: %s", exc)
        return _json_error("SPACE_UNAVAILABLE",
                           "IDM-VTON space is unreachable. Please try again shortly.")

    # ── 3. Poll /queue/status until process_completed ────────────────────────
    status_url = f"{SPACE_BASE}/queue/status"
    deadline   = time.time() + POLL_TIMEOUT

    while time.time() < deadline:
        try:
            poll_req = urllib.request.Request(status_url, headers=auth_header)
            with urllib.request.urlopen(poll_req, timeout=15) as resp:
                status_data = json.loads(resp.read())
        except Exception as exc:
            logger.warning("Poll error: %s", exc)
            time.sleep(POLL_SLEEP)
            continue

        # Find our event in the queue
        queue_list = status_data.get("queue_data", [])
        for item in queue_list:
            if item.get("event_id") != event_id:
                continue
            status = item.get("status", "")
            logger.info("Job status: %s", status)
            if status == "process_completed":
                output = item.get("output", {})
                return _extract_result(output)
            if status in ("error", "process_errored"):
                return _json_error("TRYON_FAILED",
                                   "IDM-VTON processing failed. Please try again.")

        time.sleep(POLL_SLEEP)

    return _json_error("TIMEOUT",
                       "IDM-VTON timed out. The GPU queue is busy — please retry.")


def _extract_result(output: dict) -> dict:
    """
    Pull the result image out of the Gradio output dict and return
    it as a base64 data URI.
    """
    try:
        data = output.get("data", [])
        # output[0] is the result image, output[1] is the mask
        result = data[0] if data else None
        if result is None:
            raise ValueError("No data in output")

        # Gradio can return either a URL string or a dict with a "url" key
        if isinstance(result, dict):
            img_url = result.get("url") or result.get("path", "")
        else:
            img_url = str(result)

        if img_url.startswith("data:"):
            # Already a data URI
            return {"success": True, "image": img_url, "provider": "idm-vton"}

        # Fetch the image from the space
        token = os.getenv("HF_TOKEN", "").strip()
        fetch_headers = {}
        if token:
            fetch_headers["Authorization"] = f"Bearer {token}"

        # Relative URL → prepend space base
        if img_url.startswith("/"):
            img_url = SPACE_BASE + img_url

        req = urllib.request.Request(img_url, headers=fetch_headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            img_bytes = resp.read()

        b64  = base64.b64encode(img_bytes).decode("utf-8")
        mime = "image/jpeg" if img_bytes[:2] == b"\xff\xd8" else "image/png"
        return {"success": True, "image": f"data:{mime};base64,{b64}", "provider": "idm-vton"}

    except Exception as exc:
        logger.error("Could not extract result: %s", exc)
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

        logger.info("POST /api/try-on  person=%d B  garment=%d B  space=%s",
                    len(person_bytes), len(garment_bytes), SPACE_BASE)

        # ── Call IDM-VTON via Gradio REST ─────────────────────────────────────
        result = _run_tryon(person_bytes, garment_bytes, person_ext, garment_ext)

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
