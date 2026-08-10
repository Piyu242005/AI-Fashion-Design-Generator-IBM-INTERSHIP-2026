"""
backend/app/main.py — AI Fashion Studio FastAPI entry point.

Run:
  cd backend && uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# ── Load .env from project root (one level above /backend) ──────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from app.api.design import router as design_router          # noqa: E402
from app.services.cloudflare_ai import credentials_configured  # noqa: E402
from app.schemas.design import ALLOWED_MODELS, DEFAULT_MODEL    # noqa: E402

# ---------------------------------------------------------------------------
# Rate limiter — 2 image generations per minute per IP
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

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
    cf_ok = credentials_configured()
    logger.info("=" * 50)
    logger.info("AI Fashion Studio API  v2.0.0")
    logger.info("  Cloudflare Workers AI : %s", "CONFIGURED" if cf_ok else "NOT CONFIGURED")
    logger.info("  Route: POST /api/design")
    logger.info("=" * 50)
    if not cf_ok:
        logger.warning("Set CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN in .env")
    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Fashion Studio API",
    version="2.0.0",
    description="AI Fashion Studio — image generation via Cloudflare Workers AI.",
    lifespan=lifespan,
)

# ── Rate limiter middleware ───────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    lambda req, exc: JSONResponse(
        status_code=429,
        content={"success": False, "error": {"code": "RATE_LIMITED", "message": "Too many requests. Please wait a moment and try again."}},
    ),
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
        # ── Production ────────────────────────────────────────────────
        "https://ai-fashion-design-generator-ibm-intership-2026.vercel.app",
        "https://ai-fashion-design-generator-ibm.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(design_router)   # POST /api/design  (Cloudflare)


# ---------------------------------------------------------------------------
# Health / root
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"status": "ok", "service": "AI Fashion Studio API", "version": "2.0.0"}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "provider": "cloudflare",
        "configured": credentials_configured(),
    }


@app.get("/api/models")
def models():
    """Return the list of supported image generation models."""
    return {
        "default": DEFAULT_MODEL,
        "models": [
            {"id": m, "label": m.split("/")[-1]}
            for m in sorted(ALLOWED_MODELS)
        ],
    }


