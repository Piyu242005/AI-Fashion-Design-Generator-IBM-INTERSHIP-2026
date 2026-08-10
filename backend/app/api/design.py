"""
backend/app/api/design.py — Cloudflare Workers AI only.
"""
from __future__ import annotations
import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.design import DEFAULT_MODEL, DesignRequest, DesignResponse, ErrorDetail, ErrorResponse
from app.services.cloudflare_ai import credentials_configured, generate_fashion_image

logger = logging.getLogger(__name__)
router = APIRouter()

FALLBACK_URL = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80"


@router.post("/api/design", response_model=DesignResponse,
             summary="Generate a fashion design image via Cloudflare Workers AI")
async def generate_design(req: DesignRequest) -> JSONResponse:
    if not credentials_configured():
        logger.warning("Cloudflare not configured.")
        return JSONResponse(status_code=503, content=ErrorResponse(
            error=ErrorDetail(code="NOT_CONFIGURED",
                              message="Cloudflare credentials not set.",
                              fallback_url=FALLBACK_URL)).model_dump())

    model_id = req.model or DEFAULT_MODEL
    logger.info("POST /api/design model=%s prompt_len=%d", model_id, len(req.prompt))

    result = await generate_fashion_image(req.prompt, model_id)

    if result.success and result.image_base64:
        return JSONResponse(status_code=200, content=DesignResponse(
            image=result.image_base64, provider="cloudflare").model_dump())

    return JSONResponse(status_code=500, content=ErrorResponse(
        error=ErrorDetail(code=result.error_code or "GENERATION_FAILED",
                          message=result.error_message or "Generation failed.",
                          fallback_url=FALLBACK_URL)).model_dump())
