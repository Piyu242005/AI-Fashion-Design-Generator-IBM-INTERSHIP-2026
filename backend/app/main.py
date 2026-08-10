"""
backend/app/main.py
=====================
AI Fashion Studio — FastAPI application entry point.

Startup validation:
  - Warns (does not crash) when Cloudflare credentials are missing so the
    app can still serve the HuggingFace route and health checks.
  - Logs configuration state without ever printing credential values.

Run:
  cd backend
  uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import base64
import logging
import os
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Load .env from project root (one level above /backend) ──────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from app.api.design import router as design_router          # noqa: E402
from app.services.cloudflare_ai import credentials_configured  # noqa: E402

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────
    cf_ok = credentials_configured()
    hf_ok = bool(os.getenv("HUGGINGFACE_API_TOKEN", ""))
    logger.info("=" * 55)
    logger.info("AI Fashion Studio API  v2.0.0  starting up")
    logger.info("  Cloudflare Workers AI : %s", "CONFIGURED" if cf_ok else "NOT CONFIGURED (set CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN)")
    logger.info("  HuggingFace (legacy)  : %s", "CONFIGURED" if hf_ok else "NOT CONFIGURED")
    logger.info("  Primary route         : POST /api/design   (Cloudflare)")
    logger.info("  Legacy route          : POST /api/generate-image  (HuggingFace)")
    logger.info("=" * 55)
    if not cf_ok and not hf_ok:
        logger.warning(
            "No image providers are configured. "
            "Set CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN in .env for image generation."
        )
    yield   # ── app runs here ──


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Fashion Studio API",
    version="2.0.0",
    description=(
        "Backend for AI Fashion Studio. "
        "Provides image generation via Cloudflare Workers AI (FLUX.1 Schnell) "
        "with a HuggingFace fallback route."
    ),
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Explicit allow-list — no wildcard in production.
# "null" covers browsers that open index.html directly from the filesystem
# (file:// pages send Origin: null).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite default
        "http://localhost:3000",    # CRA / alternate port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "null",                     # file:// origin — index.html opened directly
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(design_router)   # POST /api/design  (Cloudflare)

# ---------------------------------------------------------------------------
# HuggingFace legacy route  — preserved so existing frontend still works
# ---------------------------------------------------------------------------
HF_TOKEN  = os.getenv("HUGGINGFACE_API_TOKEN", "")
HF_MODEL  = os.getenv("HUGGINGFACE_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
HF_URL    = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


class _HFRequest(BaseModel):
    prompt: str
    negative_prompt: str = "blurry, low quality, text, watermark, ugly, distorted"
    width: int  = 768
    height: int = 768
    num_inference_steps: int = 4


class _HFResponse(BaseModel):
    image_base64: str
    model_used: str
    provider: str = "huggingface"


@app.post("/api/generate-image", response_model=_HFResponse, include_in_schema=False)
async def generate_image_hf(req: _HFRequest):
    """Legacy HuggingFace route — kept for backward compatibility."""
    if not HF_TOKEN:
        raise HTTPException(
            status_code=503,
            detail={
                "mock": True,
                "fallback_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80",
                "message": "HUGGINGFACE_API_TOKEN not set.",
            },
        )
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
        "X-Wait-For-Model": "true",
    }
    async with httpx.AsyncClient(timeout=HF_TIMEOUT) as client:
        try:
            resp = await client.post(
                HF_URL,
                json={"inputs": req.prompt, "parameters": {
                    "negative_prompt": req.negative_prompt,
                    "width": req.width,
                    "height": req.height,
                    "num_inference_steps": req.num_inference_steps,
                }},
                headers=headers,
            )
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="HuggingFace model timed out.")
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Network error calling HuggingFace.")

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="HuggingFace API error.")

    b64 = base64.b64encode(resp.content).decode("utf-8")
    return _HFResponse(image_base64=f"data:image/png;base64,{b64}", model_used=HF_MODEL)


# ---------------------------------------------------------------------------
# Health / root
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"status": "ok", "service": "AI Fashion Studio API", "version": "2.0.0"}


@app.get("/api/health")
def health():
    cf_ok = credentials_configured()
    hf_ok = bool(HF_TOKEN)
    return {
        "status": "ok",
        "providers": {
            "cloudflare": {"configured": cf_ok},
            "huggingface": {"configured": hf_ok, "model": HF_MODEL},
        },
    }


