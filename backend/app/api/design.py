"""
backend/app/api/design.py
===========================
POST /api/design — unified image generation endpoint.

Routing by model ID prefix:
  @cf/...     → Cloudflare Workers AI
  hf/...      → HuggingFace Inference API
  google/...  → Google Imagen (via Gemini API key)
  (none)      → defaults to Cloudflare
"""

from __future__ import annotations
import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.design import (
    DEFAULT_MODEL, DesignRequest, DesignResponse,
    ErrorDetail, ErrorResponse,
)
from app.services.cloudflare_ai import credentials_configured, generate_fashion_image
from app.services.huggingface_ai import hf_configured, generate_hf_image
from app.services.google_ai import google_configured, generate_google_image

logger = logging.getLogger(__name__)
router = APIRouter()

FALLBACK_URL = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80"


def _provider(model_id: str) -> str:
    """Return 'cloudflare', 'huggingface', or 'google' from model prefix."""
    if model_id.startswith("hf/"):
        return "huggingface"
    if model_id.startswith("google/"):
        return "google"
    return "cloudflare"


def _hf_model_id(model_id: str) -> str:
    """Strip the 'hf/' prefix to get the raw HF repo ID."""
    return model_id[len("hf/"):]


def _google_model_id(model_id: str) -> str:
    """Strip the 'google/' prefix to get the raw Google model name."""
    return model_id[len("google/"):]


def _error(code: str, message: str, status: int = 500, fallback: bool = False) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content=ErrorResponse(
            error=ErrorDetail(
                code=code,
                message=message,
                fallback_url=FALLBACK_URL if fallback else None,
            )
        ).model_dump(),
    )


@router.post(
    "/api/design",
    response_model=DesignResponse,
    responses={
        200: {"model": DesignResponse},
        503: {"model": ErrorResponse, "description": "Provider not configured"},
        500: {"model": ErrorResponse, "description": "Generation failed"},
    },
    summary="Generate a fashion design image",
    description=(
        "Routes to Cloudflare Workers AI (@cf/), HuggingFace (hf/), "
        "or Google Imagen (google/) based on the model ID prefix."
    ),
)
async def generate_design(req: DesignRequest) -> JSONResponse:
    model_id = req.model or DEFAULT_MODEL
    provider = _provider(model_id)

    logger.info("POST /api/design  provider=%s  model=%s  prompt_len=%d",
                provider, model_id, len(req.prompt))

    # ── Cloudflare ───────────────────────────────────────────────────────────
    if provider == "cloudflare":
        if not credentials_configured():
            logger.warning("Cloudflare not configured, falling back to placeholder.")
            return _error("NOT_CONFIGURED",
                          "Cloudflare credentials not set — using placeholder image.",
                          status=503, fallback=True)
        result = await generate_fashion_image(req.prompt, model_id)
        if result.success and result.image_base64:
            return JSONResponse(status_code=200, content=DesignResponse(
                image=result.image_base64, provider="cloudflare").model_dump())
        return _error(result.error_code or "GENERATION_FAILED",
                      result.error_message or "Generation failed.", fallback=True)

    # ── HuggingFace ──────────────────────────────────────────────────────────
    if provider == "huggingface":
        if not hf_configured():
            return _error("NOT_CONFIGURED",
                          "HUGGINGFACE_API_TOKEN not set — add it to .env.",
                          status=503, fallback=True)
        hf_id = _hf_model_id(model_id)
        result = await generate_hf_image(req.prompt, hf_id)
        if result.success and result.image_base64:
            return JSONResponse(status_code=200, content=DesignResponse(
                image=result.image_base64, provider="huggingface").model_dump())
        return _error(result.error_code or "GENERATION_FAILED",
                      result.error_message or "Generation failed.", fallback=True)

    # ── Google Imagen ────────────────────────────────────────────────────────
    if provider == "google":
        if not google_configured():
            return _error("NOT_CONFIGURED",
                          "VITE_GEMINI_API_KEY not set — add it to .env.",
                          status=503, fallback=True)
        g_id = _google_model_id(model_id)
        result = await generate_google_image(req.prompt, g_id)
        if result.success and result.image_base64:
            return JSONResponse(status_code=200, content=DesignResponse(
                image=result.image_base64, provider="google").model_dump())
        return _error(result.error_code or "GENERATION_FAILED",
                      result.error_message or "Generation failed.", fallback=True)

    return _error("UNKNOWN_PROVIDER", f"Unknown provider for model: {model_id}", status=400)
