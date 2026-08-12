"""
backend/app/schemas/product.py
================================
Pydantic schemas for the product recommendation feature.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Internal normalised product (returned to the client)
# ---------------------------------------------------------------------------
class Product(BaseModel):
    name:                 str
    brand:                Optional[str]  = None
    price:                Optional[float] = None
    currency:             str            = "INR"
    image:                Optional[str]  = None
    url:                  Optional[str]  = None
    category:             Optional[str]  = None
    rating:               Optional[float] = None
    source:               str            = "H&M"
    recommendation_score: Optional[int]  = Field(
        default=None,
        ge=0, le=100,
        description="Weighted match score 0-100 based on category/color/budget/style.",
    )


# ---------------------------------------------------------------------------
# API query parameters (validated by FastAPI)
# ---------------------------------------------------------------------------
class ProductSearchParams(BaseModel):
    query:    str           = Field(..., min_length=2, max_length=200,
                                   description="Free-text search query, e.g. 'black cotton shirt'")
    category: Optional[str] = Field(default=None, max_length=80)
    color:    Optional[str] = Field(default=None, max_length=80)
    budget:   Optional[float] = Field(default=None, gt=0,
                                      description="Maximum price in INR")
    limit:    int           = Field(default=5, ge=1, le=10)


# ---------------------------------------------------------------------------
# API response envelope
# ---------------------------------------------------------------------------
class ProductSearchResponse(BaseModel):
    success:  bool         = True
    products: List[Product] = []
    query:    Optional[str] = None
    source:   str          = "H&M via RapidAPI"
