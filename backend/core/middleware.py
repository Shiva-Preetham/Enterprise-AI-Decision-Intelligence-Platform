import time
import uuid
from typing import Callable
from fastapi import Request, Response
from structlog import get_logger
from structlog.contextvars import clear_contextvars, bind_contextvars
from starlette.middleware.base import BaseHTTPMiddleware

logger = get_logger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Injects a UUID into every request and adds it to the structlog context."""
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        clear_contextvars()
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        bind_contextvars(request_id=request_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Logs the execution time and details for every request."""
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")
        
        logger.info("request_started", method=request.method, url=str(request.url), request_id=request_id)
        
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error("request_failed", error=str(e), request_id=request_id)
            raise e
            
        process_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            "request_completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            duration_ms=round(process_time_ms, 2),
            request_id=request_id
        )
        
        response.headers["X-Process-Time"] = str(process_time_ms)
        return response
