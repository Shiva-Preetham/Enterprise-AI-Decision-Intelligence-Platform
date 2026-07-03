from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    """Standardized API Response wrapper."""
    status: str = Field(..., description="Success or error status")
    message: str = Field(..., description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="UUID for tracing")
    data: Optional[T] = Field(None, description="Response payload")

    model_config = ConfigDict(populate_by_name=True)

class SuccessResponse(BaseResponse[T]):
    """Standard success response."""
    status: str = "success"

class ErrorResponse(BaseResponse[None]):
    """Standard error response."""
    status: str = "error"
