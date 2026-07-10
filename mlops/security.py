"""
MLOps Security Middleware.
Provides simulated JWT validation and rate limiting for MLOps endpoints.
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from backend.config import settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard security headers to all responses."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

class SimulatedJWTMiddleware(BaseHTTPMiddleware):
    """
    Simulates JWT validation for the MLOps endpoints.
    In a real system, this would decode the JWT using settings.JWT_SECRET.
    Here, we just check if an Authorization header exists for /api/v1/mlops routes.
    """
    async def dispatch(self, request: Request, call_next):
        # Only protect the MLOps API routes, not public /metrics or /health
        if request.url.path.startswith("/api/v1/mlops"):
            auth_header = request.headers.get("Authorization")
            api_key = request.headers.get("X-API-Key")
            
            # Simple simulation: require either an API Key or a Bearer token
            if not auth_header and not api_key:
                from fastapi.responses import JSONResponse
                return JSONResponse(status_code=401, content={"detail": "Unauthorized: Missing API Key or JWT."})
                
            if auth_header and not auth_header.startswith("Bearer "):
                from fastapi.responses import JSONResponse
                return JSONResponse(status_code=401, content={"detail": "Unauthorized: Invalid token format."})
                
        return await call_next(request)
