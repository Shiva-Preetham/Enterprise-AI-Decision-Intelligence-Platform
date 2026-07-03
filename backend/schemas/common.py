"""
Enterprise AI Customer Intelligence Platform — Common Schemas.

Shared Pydantic models used across multiple API endpoints.
"""

from __future__ import annotations

from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for paginated list endpoints."""

    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum records to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response.

    Uses Generic[T] so each endpoint can specify its own item type
    and get proper OpenAPI schema generation.
    """

    items: List[T]
    total: int = Field(..., description="Total items returned in this page")
    skip: int = Field(..., description="Offset applied")
    limit: int = Field(..., description="Limit applied")
