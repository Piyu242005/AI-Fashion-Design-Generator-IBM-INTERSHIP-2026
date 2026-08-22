"""Vercel serverless endpoint for IDM-VTON virtual try-on.

Uses Hugging Face's current Gradio REST queue API directly instead of the
legacy gradio_client SSE transport. This avoids the common /queue/data
connection failure reported by older Gradio clients and works with the
current yisol/IDM-VTON Space API.
"""
from __future__ import annotations

import base64
import json
import logging
import os
import tempfile
import time
import uuid
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

SPACE_ID = os.getenv("HF_SPACE_ID", "yisol/IDM-VTON")
SPACE_URL = os.getenv("HF_SPACE_URL", "https://yisol-idm-vton.hf.space").rstrip("/")
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
MAX_BYTES = 10 * 1024 * 1024
CONNECT_TIMEOUT = 20
QUEUE_TIMEOUT = 95
POLL_INTERVAL = 2

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def _json_error(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


def _headers(content_type: str | None = None) -> dict:
    headers = {"User-Agent": "AI-Fashion-Studio/1.0", "Accept": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def _http(req: Request, timeout: int):
    try:
        return urlopen(req, timeout=timeout)
    except HTTPError as exc:
        body = exc.read(1200).decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def _multipart_upload(person_path: str, garment_path: str) -> tuple[str, str]:
    """Upload both files through Gradio's current /gradio_api/upload endpoint."""
    boundary = f"----AIFashionStudio{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for path in (person_path, garment_path):
        data = Path(path).read_bytes()
        filename = Path(path).name
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="files"; filename="{filename}"\r\n'.encode(),
            b"Content-Type: application/octet-stream\r\n\r\n",
            data,
            b"\r\n",
        ])
    chunks.append(f"--{boundary}--\r\n".encode())
    body = b"".join(chunks)
    req = Request(
        f"{SPACE_URL}/gradio_api/upload",
        data=body,
        headers=_headers(f"multipart/form-data; boundary={boundary}"),
        method="POST",
    )
    with _http(req, CONNECT_TIMEOUT) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError(f"Unexpected upload response: {payload!r}")
    return str(payload[0]), str(payload[1])


def _submit(person_file: str, garment_file: str, description: str) -> str:
    # The current IDM-VTON app defines /tryon as:
    # start_tryon(dict, garm_img, garment_des, is_checked, is_checked_crop,
    #             denoise_steps, seed)
    data = [
        {
            "background": person_file,
            "layers": [],
            "composite": None,
        },
        garment_file,
        description[:200] or "fashion garment",
        True,
        True,
        30,
        42,
    ]
    req = Request(
        f"{SPACE_URL}/gradio_api/call/tryon",
        data=json.dumps({"data": data}).encode("utf-8"),
        headers=_headers("application/json"),
        method="POST",
    )
    with _http(req, CONNECT_TIMEOUT) as response:
        payload = json.loads(response.read().decode("utf-8"))
    event_id = payload.get("event_id") if isinstance(payload, dict) else None
    if not event_id:
        raise RuntimeError(f"No event_id returned by IDM-VTON: {payload!r}")
    return event_id


def _wait_for_result(event_id: str):
    """Read Gradio SSE until complete/error, without using legacy /queue/data."""
    req = Request(
        f"{SPACE_URL}/gradio_api/call/tryon/{event_id}",
        headers={**_headers(), "Accept": "text/event-stream"},
        method="GET",
    )
    deadline = time.monotonic() + QUEUE_TIMEOUT
    with _http(req, QUEUE_TIMEOUT) as response:
        buffer = ""
        while time.monotonic() < deadline:
            chunk = response.read(4096)
            if not chunk:
                break
            buffer += chunk.decode("utf-8", errors="replace")
            while "\n\n" in buffer:
                block, buffer = buffer.split("\n\n", 1)
                event = None
                data_text = None
                for line in block.splitlines():
                    if line.startswith("event:"):
                        event = line[6:].strip()
                    elif line.startswith("data:"):
                        data_text = line[5:].strip()
                if not data_text:
                    continue
                try:
                    data = json.loads(data_text)
                except json.JSONDecodeError:
                    data = data_text
                if event == "error":
                    raise RuntimeError(str(data))
                if event == "complete":
                    return data
                if event == "generating":
                    continue
    raise TimeoutError("IDM-VTON generation timed out while waiting for the GPU queue.")


def _download_result(result) -> bytes:
    """Extract the first image URL/path from Gradio's output and download it."""
    value = result
    if isinstance(result, list):
        if not result:
            raise RuntimeError("IDM-VTON returned no output.")
        value = result[0]
    if isinstance(value, dict):
        value = value.get("path") or value.get("url") or value.get("image") or value.get("data")
    if not isinstance(value, str):
        raise RuntimeError(f"Unexpected IDM-VTON output: {value!r}")
    if value.startswith("data:image/"):
        return base64.b64decode(value.split(",", 1)[1])
    url = value if value.startswith("http") else urljoin(f"{SPACE_URL}/", value.lstrip("/"))
    req = Request(url, headers=_headers(), method="GET")
    with _http(req, CONNECT_TIMEOUT) as response:
        return response.read()


def _run_tryon(person_bytes: bytes, garment_bytes: bytes, person_ext: str,
               garment_ext: str, description: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        person_path = str(Path(tmp) / f"person.{person_ext}")
        garment_path = str(Path(tmp) / f"garment.{garment_ext}")
        Path(person_path).write_bytes(person_bytes)
        Path(garment_path).write_bytes(garment_bytes)

        try:
            logger.info("IDM-VTON upload: %s", SPACE_URL)
            person_file, garment_file = _multipart_upload(person_path, garment_path)
            logger.info("IDM-VTON queue submission")
            event_id = _submit(person_file, garment_file, description)
            logger.info("IDM-VTON event_id=%s", event_id)
            result = _wait_for_result(event_id)
            result_bytes = _download_result(result)
            if not result_bytes:
                raise RuntimeError("IDM-VTON returned an empty image.")
            mime = "image/jpeg" if result_bytes[:2] == b"\xff\xd8" else "image/png"
            encoded = base64.b64encode(result_bytes).decode("utf-8")
            return {"success": True, "image": f"data:{mime};base64,{encoded}", "provider": "idm-vton"}
        except TimeoutError as exc:
            logger.error("IDM-VTON timeout: %s", exc)
            return _json_error("TIMEOUT", "IDM-VTON is taking too long. The GPU queue may be busy; please retry.")
        except Exception as exc:
            message = str(exc)
            lower = message.lower()
            logger.exception("IDM-VTON request failed")
            if "401" in lower or "403" in lower:
                return _json_error("AUTH_ERROR", "Hugging Face rejected the request. Check HF_TOKEN in Vercel.")
            if "429" in lower or "quota" in lower or "exceeded" in lower:
                return _json_error("QUOTA_EXCEEDED", "Hugging Face/ZeroGPU quota is currently exhausted. Please retry later.")
            if "503" in lower or "sleep" in lower or "loading" in lower or "unavailable" in lower:
                return _json_error("SPACE_LOADING", "IDM-VTON is waking up. Please wait 30–60 seconds and retry.")
            return _json_error("TRYON_FAILED", f"IDM-VTON request failed: {message[:300]}")


def _ext(content_type: str) -> str:
    ct = (content_type or "").lower()
    if "png" in ct: return "png"
    if "webp" in ct: return "webp"
    return "jpg"


def _parse_multipart(content_type: str, raw: bytes):
    """Use python-multipart and return (person, garment, description, types)."""
    from multipart import MultipartParser
    boundary = next((p.strip()[9:].strip('"') for p in content_type.split(";") if p.strip().startswith("boundary=")), "")
    if not boundary:
        raise ValueError("Missing multipart boundary")
    fields = {}
    def on_field(field): fields[field.field_name.decode()] = field.value.decode("utf-8", errors="replace")
    def on_file(field): fields[field.field_name.decode()] = (field.file_object.read(), dict(field.headers))
    parser = MultipartParser(boundary.encode(), on_field=on_field, on_file=on_file)
    parser.write(raw)
    parser.finalize()
    person = fields.get("person")
    garment = fields.get("garment")
    if not isinstance(person, tuple) or not isinstance(garment, tuple):
        raise ValueError("Both person and garment files are required")
    ptype = person[1].get(b"Content-Type", b"").decode() if person[1] else ""
    gtype = garment[1].get(b"Content-Type", b"").decode() if garment[1] else ""
    desc = fields.get("garment_description", "")
    return person[0], garment[0], str(desc), ptype, gtype


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for k, v in CORS_HEADERS.items(): self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        for k, v in CORS_HEADERS.items(): self.send_header(k, v)
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BYTES * 2 + 1024 * 1024:
                self._send(413, _json_error("FILE_TOO_LARGE", "The uploaded images are too large."))
                return
            content_type = self.headers.get("Content-Type", "")
            raw = self.rfile.read(length)
            person, garment, description, ptype, gtype = _parse_multipart(content_type, raw)
            if len(person) > MAX_BYTES or len(garment) > MAX_BYTES:
                self._send(413, _json_error("FILE_TOO_LARGE", "Each image must be under 10 MB."))
                return
            result = _run_tryon(person, garment, _ext(ptype), _ext(gtype), description)
            if result.get("success"):
                self._send(200, result)
                return
            code = result.get("error", {}).get("code", "TRYON_FAILED")
            status = {"AUTH_ERROR": 401, "QUOTA_EXCEEDED": 429, "SPACE_LOADING": 503, "TIMEOUT": 504}.get(code, 500)
            self._send(status, result)
        except Exception as exc:
            logger.exception("Try-on handler error")
            self._send(400, _json_error("BAD_REQUEST", f"Could not process try-on request: {str(exc)[:300]}"))
