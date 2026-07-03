from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")

class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
