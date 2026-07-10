"""
MLOps Lightweight Tracing Middleware.
Generates a trace_id per request and binds it to structlog contextvars.
"""
import uuid
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate a unique trace ID for this request
        trace_id = str(uuid.uuid4())
        
        # Set the trace ID in the request state so routes can access it if needed
        request.state.trace_id = trace_id
        
        # Bind it to structlog contextvars
        # Since structlog in backend/logging.py is configured with merge_contextvars,
        # this will automatically appear in all log statements for this async context.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(trace_id=trace_id, path=request.url.path)
        
        response = await call_next(request)
        
        # Add trace ID to the response headers
        response.headers["X-Trace-ID"] = trace_id
        
        return response
