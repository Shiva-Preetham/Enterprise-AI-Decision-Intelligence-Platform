from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from structlog import get_logger

from backend.core.responses import ErrorResponse

logger = get_logger(__name__)

class PlatformError(Exception):
    """Base class for all application-specific errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ResourceNotFoundError(PlatformError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class ModelLoadError(PlatformError):
    def __init__(self, message: str = "Failed to load ML model"):
        super().__init__(message, status_code=500)

async def platform_exception_handler(request: Request, exc: PlatformError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.error("platform_error", error=exc.message, status_code=exc.status_code, request_id=request_id)
    response = ErrorResponse(
        message=exc.message,
        request_id=request_id
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump(mode="json"))

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.error("http_error", error=exc.detail, status_code=exc.status_code, request_id=request_id)
    response = ErrorResponse(
        message=exc.detail,
        request_id=request_id
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump(mode="json"))

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.exception("unhandled_server_error", error=str(exc), request_id=request_id)
    response = ErrorResponse(
        message="Internal server error",
        request_id=request_id
    )
    return JSONResponse(status_code=500, content=response.model_dump(mode="json"))
