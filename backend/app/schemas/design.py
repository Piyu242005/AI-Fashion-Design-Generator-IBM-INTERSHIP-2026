"""
backend/app/schemas/design.py
===============================
Pydantic request / response models for the /api/design endpoint.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator

# All valid Cloudflare Workers AI image model IDs.
ALLOWED_MODELS = {
    "@cf/black-forest-labs/flux-1-schnell",
    "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    "@cf/lykon/dreamshaper-8-lcm",
    "@cf/bytedance/stable-diffusion-xl-lightning",
}
DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------
class DesignRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Fashion design prompt in plain language.",
        examples=["Modern Indian half-saree in pastel pink and gold"],
    )
    model: Optional[str] = Field(
        default=None,
        description=(
            "Cloudflare Workers AI model ID to use for image generation. "
            f"Defaults to {DEFAULT_MODEL}."
        ),
        examples=list(ALLOWED_MODELS),
    )

    @field_validator("prompt")
    @classmethod
    def strip_and_check(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Prompt is too short. Please describe the design in more detail.")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if v not in ALLOWED_MODELS:
            raise ValueError(
                f"Unknown model '{v}'. "
                f"Allowed values: {', '.join(sorted(ALLOWED_MODELS))}"
            )
        return v


# ---------------------------------------------------------------------------
# Success response
# ---------------------------------------------------------------------------
class DesignResponse(BaseModel):
    success: bool = True
    image: str = Field(..., description="Base64-encoded image as a data URI.")
    provider: str = Field(default="cloudflare", description="Which AI provider generated the image.")


# ---------------------------------------------------------------------------
# Error detail  (nested inside ErrorResponse)
# ---------------------------------------------------------------------------
class ErrorDetail(BaseModel):
    code: str
    message: str


# ---------------------------------------------------------------------------
# Error response
# ---------------------------------------------------------------------------
class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
