"""
backend/app/api/products.py
============================
GET /api/products/search  — AI Fashion Product Recommendations

Accepts query parameters:
    query    : str   — search query (required, min 2 chars)
    category : str   — optional category hint
    color    : str   — optional color hint
    budget   : float — optional max price in INR
    limit    : int   — max results to return (1-10, default 5)

Returns JSON matching ProductSearchResponse schema.

The RAPIDAPI_KEY is kept strictly server-side and never returned
to or accepted from the client.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.schemas.product import ProductSearchResponse
from app.services.product_api import rapidapi_configured, search_products

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/api/products/search",
    response_model=ProductSearchResponse,
    summary="Search fashion products via RapidAPI H&M",
    response_description="List of normalised, ranked fashion products",
)
@limiter.limit("10/minute")
async def products_search(
    request:  Request,
    query:    str           = Query(..., min_length=2, max_length=200,
                                   description="Search query, e.g. 'black cotton shirt'"),
    category: Optional[str] = Query(default=None, max_length=80),
    color:    Optional[str] = Query(default=None, max_length=80),
    budget:   Optional[float] = Query(default=None, gt=0,
                                      description="Max price in INR"),
    limit:    int           = Query(default=5, ge=1, le=10),
) -> JSONResponse:

    if not rapidapi_configured():
        logger.warning("GET /api/products/search — RAPIDAPI_KEY not configured.")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": {
                    "code":    "NOT_CONFIGURED",
                    "message": "Product recommendations are temporarily unavailable.",
                },
            },
        )

    logger.info(
        "GET /api/products/search query=%r category=%r color=%r budget=%s limit=%d",
        query[:60], category, color, budget, limit,
    )

    products = await search_products(
        query=query,
        category=category,
        color=color,
        budget=budget,
        limit=limit,
    )

    return JSONResponse(
        status_code=200,
        content=ProductSearchResponse(
            success=True,
            products=products,
            query=query,
            source="H&M via RapidAPI",
        ).model_dump(),
    )
