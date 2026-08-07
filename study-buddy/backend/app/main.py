"""
main.py — AI-Powered Study Buddy FastAPI Application
======================================================
Application factory and lifecycle management.

Start server:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.config import settings
from app.core.logging import setup_logging
from app.database import init_db
from app.exceptions import (
    AIServiceError, FileTooLargeError, NotFoundError,
    RateLimitError, UnauthorizedError, UnsupportedFileTypeError,
)
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routers import auth, chat, dashboard, documents, flashcards, quiz, summary

# ---------------------------------------------------------------------------
# Rate limiter — shared singleton; import from here in routers
# ---------------------------------------------------------------------------
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)

# ---------------------------------------------------------------------------
# Logging — initialise before anything else
# ---------------------------------------------------------------------------
setup_logging()
logger = logging.getLogger("study_buddy.main")


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Run startup tasks, yield to application, run shutdown tasks."""
    # ── Startup ────────────────────────────────────────────────────────────
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)

    # Ensure required directories exist
    settings.data_dir      # creates ./data/
    settings.upload_path   # creates ./uploads/
    settings.chroma_path   # creates ./chroma_db/

    # Initialise database tables
    await init_db()
    logger.info("Database initialised.")

    yield  # Application runs here

    # ── Shutdown ───────────────────────────────────────────────────────────
    logger.info("%s shutting down.", settings.APP_NAME)


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-Powered Study Buddy API — Generative AI study assistant "
        "with RAG, quizzes, flashcards, and document summarisation."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

# CORS — allow Streamlit frontend origins (wildcard-free, browser-compatible)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter — enforces RATE_LIMIT_PER_MINUTE from config
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request logger (adds X-Request-ID + timing logs)
app.add_middleware(RequestLoggerMiddleware)

# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again."},
    )


# ---------------------------------------------------------------------------
# Routers — all prefixed under /api/v1 for safe future versioning
# ---------------------------------------------------------------------------

_V1 = "/api/v1"

app.include_router(auth.router,        prefix=_V1)
app.include_router(documents.router,   prefix=_V1)
app.include_router(chat.router,        prefix=_V1)
app.include_router(quiz.router,        prefix=_V1)
app.include_router(summary.router,     prefix=_V1)
app.include_router(flashcards.router,  prefix=_V1)
app.include_router(dashboard.router,   prefix=_V1)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Liveness probe for Render and monitoring tools."""
    return {
        "status":  "ok",
        "app":     settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env":     settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root() -> dict:
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs":    "/docs",
        "health":  "/health",
    }
