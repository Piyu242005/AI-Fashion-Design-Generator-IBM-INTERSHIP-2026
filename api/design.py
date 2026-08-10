"""
api/design.py
=============
Vercel Python Serverless Function — POST /api/design

Calls Cloudflare Workers AI to generate a fashion image.
Credentials must be set as Vercel Environment Variables:
  CLOUDFLARE_ACCOUNT_ID
  CLOUDFLARE_API_TOKEN
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import base64
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CF_DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_API_BASE      = "https://api.cloudflare.com/client/v4/accounts"
SAFE_ERROR_MSG   = "Unable to generate the fashion design. Please try again."

ALLOWED_MODELS = {
    "@cf/black-forest-labs/flux-1-schnell",
    "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    "@cf/lykon/dreamshaper-8-lcm",
    "@cf/bytedance/stable-diffusion-xl-lightning",
}

CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _json_error(status: int, code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


def _call_cloudflare(prompt: str, model: str) -> dict:
    """
    Synchronously call Cloudflare Workers AI using stdlib urllib.
    Returns a dict with {success, image} or {success, error}.
    """
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    api_token  = os.environ.get("CLOUDFLARE_API_TOKEN",  "").strip()

    if not account_id or not api_token:
        return _json_error(500, "CONFIGURATION_ERROR", SAFE_ERROR_MSG)

    url     = f"{CF_API_BASE}/{account_id}/ai/run/{model}"
    payload = json.dumps({"prompt": prompt}).encode("utf-8")
    req     = urllib.request.Request(
        url,
        data    = payload,
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type":  "application/json",
        },
        method  = "POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            status       = resp.status
            content_type = resp.headers.get("Content-Type", "")
            body         = resp.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            return _json_error(401, "AUTH_ERROR", SAFE_ERROR_MSG)
        if exc.code == 403:
            return _json_error(403, "PERMISSION_ERROR", SAFE_ERROR_MSG)
        if exc.code == 429:
            return _json_error(429, "RATE_LIMITED",
                               "Generation is temporarily unavailable. Please try again shortly.")
        return _json_error(exc.code, "IMAGE_GENERATION_FAILED", SAFE_ERROR_MSG)
    except Exception:
        return _json_error(500, "NETWORK_ERROR", SAFE_ERROR_MSG)

    # ── Parse response ─────────────────────────────────────────────────────
    # Cloudflare returns either JSON envelope or raw image bytes
    if "application/json" in content_type or (body and body[:1] == b"{"):
        try:
            data    = json.loads(body)
            result  = data.get("result", data)
            raw_b64 = result.get("image", "")
            if not raw_b64:
                raise ValueError("No image field")
            if raw_b64.startswith("data:"):
                return {"success": True, "image": raw_b64}
            mime = "image/jpeg" if raw_b64.startswith("/9j/") else "image/png"
            return {"success": True, "image": f"data:{mime};base64,{raw_b64}"}
        except Exception:
            return _json_error(500, "PARSE_ERROR", SAFE_ERROR_MSG)

    if "image" in content_type:
        b64  = base64.b64encode(body).decode("utf-8")
        mime = content_type.split(";")[0].strip() or "image/png"
        return {"success": True, "image": f"data:{mime};base64,{b64}"}

    # Unknown — try JSON, then fall back to raw bytes
    try:
        data    = json.loads(body)
        result  = data.get("result", data)
        raw_b64 = result.get("image", "")
        if raw_b64:
            mime = "image/jpeg" if raw_b64.startswith("/9j/") else "image/png"
            return {"success": True, "image": f"data:{mime};base64,{raw_b64}"}
    except Exception:
        pass

    b64 = base64.b64encode(body).decode("utf-8")
    return {"success": True, "image": f"data:image/png;base64,{b64}"}


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

    def do_OPTIONS(self) -> None:  # preflight
        self.send_response(204)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_POST(self) -> None:
        # Read body
        length = int(self.headers.get("Content-Length", 0))
        raw    = self.rfile.read(length) if length else b"{}"

        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json(400, _json_error(400, "INVALID_JSON", "Request body must be valid JSON."))
            return

        prompt = (body.get("prompt") or "").strip()
        if len(prompt) < 5:
            self._send_json(400, _json_error(400, "VALIDATION_ERROR",
                                             "Prompt must be at least 5 characters."))
            return
        if len(prompt) > 500:
            self._send_json(400, _json_error(400, "VALIDATION_ERROR",
                                             "Prompt must be at most 500 characters."))
            return

        model = (body.get("model") or CF_DEFAULT_MODEL).strip()
        if model not in ALLOWED_MODELS:
            model = CF_DEFAULT_MODEL

        result = _call_cloudflare(prompt, model)

        if result.get("success"):
            self._send_json(200, result)
        else:
            error_code = result.get("error", {}).get("code", "")
            if error_code in ("AUTH_ERROR", "PERMISSION_ERROR", "CONFIGURATION_ERROR"):
                self._send_json(500, result)
            elif error_code == "RATE_LIMITED":
                self._send_json(429, result)
            else:
                self._send_json(502, result)
