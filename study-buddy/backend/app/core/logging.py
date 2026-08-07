"""
Structured Logging — AI-Powered Study Buddy
=============================================
Configures a JSON-compatible logger using Python's stdlib logging.
Every log record includes timestamp, level, module, and message.
In production, logs are written to file + stdout.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from app.config import settings


def setup_logging() -> logging.Logger:
    """
    Configure the root application logger.
    Returns the configured logger instance.
    """
    # Ensure log directory exists
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Format: timestamp | level | module | message
    fmt = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
    ]

    # File handler (non-fatal if unavailable)
    try:
        handlers.append(logging.FileHandler(settings.LOG_FILE, encoding="utf-8"))
    except OSError:
        pass

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=fmt,
        datefmt=date_fmt,
        handlers=handlers,
        force=True,
    )

    # Suppress noisy third-party loggers in production
    if not settings.DEBUG:
        for noisy in ("httpx", "httpcore", "chromadb", "urllib3"):
            logging.getLogger(noisy).setLevel(logging.WARNING)

    logger = logging.getLogger("study_buddy")
    logger.info("Logging initialised — level=%s", settings.LOG_LEVEL)
    return logger


# Module-level logger instance
logger: logging.Logger = logging.getLogger("study_buddy")
