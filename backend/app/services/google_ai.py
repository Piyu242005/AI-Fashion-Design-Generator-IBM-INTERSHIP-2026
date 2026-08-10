"""
backend/app/services/google_ai.py
===================================
Calls the Google Gemini API for image generation.
Supported model: imagen-3.0-generate-002 (Imagen 3, paid tier)

Note: gemini-2.5-flash / gemini-2.0-flash are TEXT-only on free tier.
Imagen 3 requires billing enabled on the Google Cloud project.
Falls back gracefully with a clear error if not configured.
"""
from __future__ import annotations
import base64, logging, os
from dataclasses import dataclass
from typing import Optional
import httpx

logger = logging.getLogger(__name__)
SAFE_ERROR = "Unable to generate the fashion design. Please try again."

GOOGLE_IMAGEN_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:predict"
)

@dataclass
class GoogleResult:
    success: bool
    image_base64: Optional[str] = None
    error_code: Optional[str]   = None
    error_message: Optional[str]= None


def google_configured() -> bool:
    return bool(os.getenv("VITE_GEMINI_API_KEY", "").strip())


async def generate_google_image(prompt: str, model: str) -> GoogleResult:
    """
    Call Google Imagen via the Gemini API key.
    model should be e.g. 'imagen-3.0-generate-002'.
    """
    key = os.getenv("VITE_GEMINI_API_KEY", "").strip()
    if not key:
        return GoogleResult(success=False, error_code="NOT_CONFIGURED", error_message=SAFE_ERROR)

    url = GOOGLE_IMAGEN_URL.format(model=model) + f"?key={key}"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1},
    }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
            resp = await client.post(url, json=payload,
                                     headers={"Content-Type": "application/json"})
    except httpx.TimeoutException:
        return GoogleResult(success=False, error_code="TIMEOUT", error_message=SAFE_ERROR)
    except httpx.RequestError as exc:
        logger.error("Google AI network error: %s", type(exc).__name__)
        return GoogleResult(success=False, error_code="NETWORK_ERROR", error_message=SAFE_ERROR)

    if resp.status_code == 400:
        logger.warning("Google Imagen 400 — check API key / billing: %s", resp.text[:200])
        return GoogleResult(success=False, error_code="BILLING_REQUIRED",
                            error_message="Google Imagen requires billing. Enable it at console.cloud.google.com.")
    if resp.status_code != 200:
        logger.error("Google Imagen returned %d", resp.status_code)
        return GoogleResult(success=False, error_code="API_ERROR", error_message=SAFE_ERROR)

    try:
        data = resp.json()
        # Response: {"predictions":[{"bytesBase64Encoded":"...","mimeType":"image/png"}]}
        pred = data["predictions"][0]
        raw_b64 = pred.get("bytesBase64Encoded", "")
        mime    = pred.get("mimeType", "image/png")
        if not raw_b64:
            raise ValueError("Empty image in response")
        return GoogleResult(success=True, image_base64=f"data:{mime};base64,{raw_b64}")
    except Exception as exc:
        logger.error("Failed to parse Google Imagen response: %s", exc)
        return GoogleResult(success=False, error_code="PARSE_ERROR", error_message=SAFE_ERROR)
