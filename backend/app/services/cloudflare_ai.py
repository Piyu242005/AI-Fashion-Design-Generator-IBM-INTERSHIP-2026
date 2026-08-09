"""
backend/app/services/cloudflare_ai.py
======================================
Handles all communication with Cloudflare Workers AI.

  Model  : @cf/black-forest-labs/flux-1-schnell
  Docs   : https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/

Security rules enforced here:
  - Credentials loaded from environment only; never accepted as arguments.
  - Raw Cloudflare error bodies are NEVER forwarded to the caller.
  - Token value is NEVER logged, printed, or included in exception messages.
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CF_MODEL         = "@cf/black-forest-labs/flux-1-schnell"
CF_API_BASE      = "https://api.cloudflare.com/client/v4/accounts"
CF_TIMEOUT       = httpx.Timeout(90.0, connect=10.0)   # FLUX can be slow on cold start
SAFE_ERROR_MSG   = "Unable to generate the fashion design. Please try again."


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------
@dataclass
class GenerationResult:
    success: bool
    image_base64: Optional[str] = None   # "data:image/png;base64,…" when success
    error_code: Optional[str]   = None
    error_message: Optional[str] = None


def _get_credentials() -> tuple[str, str]:
    """
    Read Cloudflare credentials from the environment.
    Raises RuntimeError if either variable is missing.
    The values themselves are never logged.
    """
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
    api_token  = os.getenv("CLOUDFLARE_API_TOKEN",  "").strip()

    if not account_id:
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID environment variable is not set.")
    if not api_token:
        raise RuntimeError("CLOUDFLARE_API_TOKEN environment variable is not set.")

    return account_id, api_token


def credentials_configured() -> bool:
    """Return True only when both Cloudflare credentials are present."""
    return bool(
        os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
        and os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
    )


async def generate_fashion_image(prompt: str) -> GenerationResult:
    """
    Call Cloudflare Workers AI → FLUX.1 Schnell and return a GenerationResult.

    Args:
        prompt: The fashion design prompt (already validated by the API layer).

    Returns:
        GenerationResult with success=True and image_base64 set on success,
        or success=False with a safe error message on any failure.
    """
    try:
        account_id, api_token = _get_credentials()
    except RuntimeError as exc:
        # Config error — log on server, return safe message to client
        logger.error("Cloudflare credentials missing: %s", exc)
        return GenerationResult(
            success=False,
            error_code="CONFIGURATION_ERROR",
            error_message=SAFE_ERROR_MSG,
        )

    url = f"{CF_API_BASE}/{account_id}/ai/run/{CF_MODEL}"
    headers = {
        # Token value intentionally never logged
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    payload = {"prompt": prompt}

    try:
        async with httpx.AsyncClient(timeout=CF_TIMEOUT) as client:
            response = await client.post(url, json=payload, headers=headers)
    except httpx.TimeoutException:
        logger.warning("Cloudflare Workers AI request timed out for prompt hash=%s", hash(prompt))
        return GenerationResult(
            success=False,
            error_code="TIMEOUT",
            error_message=SAFE_ERROR_MSG,
        )
    except httpx.RequestError as exc:
        # Network-level error — safe to log type/message, not the token
        logger.error("Network error calling Cloudflare AI: %s", type(exc).__name__)
        return GenerationResult(
            success=False,
            error_code="NETWORK_ERROR",
            error_message=SAFE_ERROR_MSG,
        )

    # ── Handle HTTP errors ──────────────────────────────────────────────────
    if response.status_code == 401:
        logger.error("Cloudflare AI returned 401 — check CLOUDFLARE_API_TOKEN permissions.")
        return GenerationResult(
            success=False,
            error_code="AUTH_ERROR",
            error_message=SAFE_ERROR_MSG,
        )

    if response.status_code == 403:
        logger.error("Cloudflare AI returned 403 — token lacks Workers AI permission.")
        return GenerationResult(
            success=False,
            error_code="PERMISSION_ERROR",
            error_message=SAFE_ERROR_MSG,
        )

    if response.status_code == 429:
        logger.warning("Cloudflare AI rate limit hit.")
        return GenerationResult(
            success=False,
            error_code="RATE_LIMITED",
            error_message="Generation is temporarily unavailable. Please try again shortly.",
        )

    if response.status_code != 200:
        # Log status code only — never the response body (may contain account info)
        logger.error("Cloudflare AI returned unexpected status: %d", response.status_code)
        return GenerationResult(
            success=False,
            error_code="IMAGE_GENERATION_FAILED",
            error_message=SAFE_ERROR_MSG,
        )

    # ── Parse response ──────────────────────────────────────────────────────
    # Cloudflare FLUX.1-schnell returns raw PNG bytes (not JSON).
    content_type = response.headers.get("content-type", "")
    if "image" in content_type or len(response.content) > 1000:
        # Raw image bytes
        b64 = base64.b64encode(response.content).decode("utf-8")
        return GenerationResult(
            success=True,
            image_base64=f"data:image/png;base64,{b64}",
        )

    # Fallback: try JSON envelope (Cloudflare sometimes wraps in {result: {image: "..."}})
    try:
        data = response.json()
        # Handle both {result: {image: "base64..."}} and {image: "base64..."}
        result = data.get("result", data)
        raw_b64 = result.get("image", "")
        if not raw_b64:
            raise ValueError("No image field in response")
        # Normalise — strip data URI prefix if already present
        if raw_b64.startswith("data:"):
            return GenerationResult(success=True, image_base64=raw_b64)
        return GenerationResult(
            success=True,
            image_base64=f"data:image/png;base64,{raw_b64}",
        )
    except Exception:
        logger.error("Could not parse Cloudflare AI response (unexpected format).")
        return GenerationResult(
            success=False,
            error_code="PARSE_ERROR",
            error_message=SAFE_ERROR_MSG,
        )
