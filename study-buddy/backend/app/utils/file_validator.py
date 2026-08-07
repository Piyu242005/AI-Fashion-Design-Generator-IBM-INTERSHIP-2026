"""
File Validator — AI-Powered Study Buddy
=========================================
Security-first file validation before processing.
Checks: extension whitelist, file size, MIME magic bytes.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.config import settings
from app.exceptions import FileTooLargeError, UnsupportedFileTypeError

logger = logging.getLogger("study_buddy.validator")

# Magic bytes for each supported type
_MAGIC: dict[str, bytes] = {
    "pdf":  b"%PDF",
    "docx": b"PK\x03\x04",   # ZIP-based (OOXML)
    "pptx": b"PK\x03\x04",
    "txt":  b"",               # no magic bytes — accept any
}


def validate_upload(file_bytes: bytes, filename: str) -> str:
    """
    Validate an uploaded file for safety and compatibility.

    Args:
        file_bytes: Raw file content.
        filename:   Original filename from the client.

    Returns:
        Normalised file extension string (e.g. "pdf").

    Raises:
        UnsupportedFileTypeError: Extension not in whitelist.
        FileTooLargeError:        File exceeds MAX_UPLOAD_SIZE_MB.
    """
    # ── Extension check ────────────────────────────────────────────────────
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(ext)

    # ── Size check ─────────────────────────────────────────────────────────
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise FileTooLargeError(settings.MAX_UPLOAD_SIZE_MB)

    # ── Magic bytes check (skip for txt) ──────────────────────────────────
    expected_magic = _MAGIC.get(ext, b"")
    if expected_magic and not file_bytes.startswith(expected_magic):
        logger.warning("Magic bytes mismatch for '%s' — rejecting.", filename)
        raise UnsupportedFileTypeError(ext)

    logger.info("Validated upload: %s (%.2f MB)", filename, size_mb)
    return ext
