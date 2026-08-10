"""
backend/app/schemas/design.py
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, field_validator

ALLOWED_MODELS = {
    "@cf/black-forest-labs/flux-1-schnell",
    "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    "@cf/lykon/dreamshaper-8-lcm",
    "@cf/bytedance/stable-diffusion-xl-lightning",
}
DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"


class DesignRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500)
    model: Optional[str] = Field(default=None)

    @field_validator("prompt")
    @classmethod
    def strip_and_check(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Prompt is too short.")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if v not in ALLOWED_MODELS:
            raise ValueError(f"Unknown model '{v}'. Allowed: {', '.join(sorted(ALLOWED_MODELS))}")
        return v


class DesignResponse(BaseModel):
    success: bool = True
    image: str = Field(..., description="Base64-encoded image as a data URI.")
    provider: str = Field(default="cloudflare")


class ErrorDetail(BaseModel):
    code: str
    message: str
    fallback_url: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
