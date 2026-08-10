"""
backend/app/services/huggingface_ai.py
=======================================
Calls the HuggingFace Inference API for image generation.
Supported models (text-to-image):
  - black-forest-labs/FLUX.1-schnell  (fast, high quality)
  - stabilityai/stable-diffusion-xl-base-1.0
  - runwayml/stable-diffusion-v1-5
"""
from __future__ import annotations
import base64, logging, os
from dataclasses import dataclass
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

HF_API_BASE = "https://api-inference.huggingface.co/models"
HF_TIMEOUT  = httpx.Timeout(90.0, connect=10.0)
SAFE_ERROR  = "Unable to generate the fashion design. Please try again."

@dataclass
class HFResult:
    success: bool
    image_base64: Optional[str] = None
    error_code: Optional[str]   = None
    error_message: Optional[str]= None


def hf_configured() -> bool:
    return bool(os.getenv("HUGGINGFACE_API_TOKEN", "").strip())


async def generate_hf_image(prompt: str, model: str) -> HFResult:
    token = os.getenv("HUGGINGFACE_API_TOKEN", "").strip()
    if not token:
        return HFResult(success=False, error_code="NOT_CONFIGURED", error_message=SAFE_ERROR)

    url = f"{HF_API_BASE}/{model}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Wait-For-Model": "true",
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "blurry, low quality, text, watermark, ugly, distorted",
            "width": 768, "height": 768,
            "num_inference_steps": 4,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=HF_TIMEOUT) as client:
            resp = await client.post(url, json=payload, headers=headers)
    except httpx.TimeoutException:
        logger.warning("HuggingFace timeout for model %s", model)
        return HFResult(success=False, error_code="TIMEOUT", error_message=SAFE_ERROR)
    except httpx.RequestError as exc:
        logger.error("HuggingFace network error: %s", type(exc).__name__)
        return HFResult(success=False, error_code="NETWORK_ERROR", error_message=SAFE_ERROR)

    if resp.status_code == 503:
        return HFResult(success=False, error_code="MODEL_LOADING",
                        error_message="Model is loading, please retry in ~20 s.")
    if resp.status_code != 200:
        logger.error("HuggingFace returned %d for model %s", resp.status_code, model)
        return HFResult(success=False, error_code="API_ERROR", error_message=SAFE_ERROR)

    # HF returns raw image bytes
    b64 = base64.b64encode(resp.content).decode("utf-8")
    ct  = resp.headers.get("content-type", "image/jpeg")
    mime = ct.split(";")[0].strip() if "image" in ct else "image/png"
    return HFResult(success=True, image_base64=f"data:{mime};base64,{b64}")
