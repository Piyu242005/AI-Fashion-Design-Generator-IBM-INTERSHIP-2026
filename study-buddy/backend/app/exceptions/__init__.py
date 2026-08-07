"""
Custom Exceptions — AI-Powered Study Buddy
============================================
Domain-specific exceptions mapped to HTTP status codes.
FastAPI exception handlers are registered in main.py.
"""

from __future__ import annotations

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found.",
        )


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Not authenticated.") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Access denied.") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ValidationError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class FileTooLargeError(HTTPException):
    def __init__(self, max_mb: int = 50) -> None:
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {max_mb} MB.",
        )


class UnsupportedFileTypeError(HTTPException):
    def __init__(self, ext: str = "") -> None:
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{ext}' is not supported. Use PDF, DOCX, PPTX or TXT.",
        )


class AIServiceError(HTTPException):
    def __init__(self, detail: str = "AI service unavailable. Please retry.") -> None:
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class RateLimitError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please wait and try again.",
        )
