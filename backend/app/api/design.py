"""
backend/app/api/design.py
===========================
POST /api/design  —  Generate a fashion image via Cloudflare Workers AI.

Flow:
  1. Validate prompt (Pydantic).
  2. Check Cloudflare credentials are configured.
  3. Call cloudflare_ai.generate_fashion_image().
  4. Return DesignResponse on success, ErrorResponse on failure.
  5. NEVER forward raw Cloudflare errors or credentials to the client.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.design import DesignRequest, DesignResponse, ErrorDetail, ErrorResponse
from app.services.cloudflare_ai import credentials_configured, generate_fashion_image

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/api/design",
    response_model=DesignResponse,
    responses={
        200: {"model": DesignResponse},
        503: {"model": ErrorResponse, "description": "Cloudflare credentials not configured"},
        422: {"description": "Validation error — prompt too short / too long"},
        500: {"model": ErrorResponse, "description": "Image generation failed"},
    },
    summary="Generate a fashion design image",
    description=(
        "Accepts a plain-language fashion prompt. "
        "Enhances it via Gemini (if configured), then calls Cloudflare FLUX.1-Schnell. "
        "Returns a base64-encoded PNG as a data URI."
    ),
)
async def generate_design(req: DesignRequest) -> JSONResponse:
    # ── Guard: credentials must be present ──────────────────────────────────
    if not credentials_configured():
        logger.error("POST /api/design called but Cloudflare credentials are not configured.")
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="CONFIGURATION_ERROR",
                    message="Image generation service is not configured. Contact the administrator.",
                )
            ).model_dump(),
        )

    logger.info("Generating fashion design (prompt length=%d)", len(req.prompt))

    result = await generate_fashion_image(req.prompt)

    if result.success and result.image_base64:
        return JSONResponse(
            status_code=200,
            content=DesignResponse(image=result.image_base64).model_dump(),
        )

    # Failure — use safe message from the service layer
    error_code    = result.error_code    or "IMAGE_GENERATION_FAILED"
    error_message = result.error_message or "Unable to generate the fashion design. Please try again."

    logger.warning("Design generation failed: code=%s", error_code)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetail(code=error_code, message=error_message)
        ).model_dump(),
    )
