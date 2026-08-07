"""
Request Logger Middleware — AI-Powered Study Buddy
====================================================
Logs every incoming HTTP request with method, path, status, and duration.
Adds X-Request-ID header to every response for traceability.
"""

from __future__ import annotations

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Log request method, path, status code, and response time."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        # Attach request ID for downstream use
        request.state.request_id = request_id

        response: Response = await call_next(request)

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "%s %s → %d  [%dms]  id=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            request_id,
        )
        return response
