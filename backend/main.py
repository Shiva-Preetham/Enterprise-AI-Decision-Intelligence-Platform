"""
Enterprise AI Customer Intelligence Platform — Application Entrypoint.

Configures and creates the FastAPI application instance. Handles:
- ML model loading on startup (once, not per-request).
- Redis connection pool lifecycle.
- Middleware registration (RequestID, Observability, CORS).
- Global exception handlers.
- API router mounting under /api/v1/.

To run locally:
    uvicorn backend.main:app --reload

To run in production:
    gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --workers 4
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from structlog import get_logger

from backend.api.dependencies import ml_globals
from backend.api.v1.router import api_router
from backend.cache.client import shutdown_redis, startup_redis
from backend.config import settings
from backend.core.exceptions import (
    PlatformError,
    global_exception_handler,
    http_exception_handler,
    platform_exception_handler,
)
from backend.core.middleware import ObservabilityMiddleware, RequestIDMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: startup and shutdown.

    Startup:
        1. Connect to Redis (cache + Celery result backend).
        2. Load ML artifacts into the global singleton.

    Shutdown:
        1. Close Redis connection pool.
    """
    logger.info("application_startup", env=settings.APP_ENV, version="1.0.0")

    # --- Redis ---
    await startup_redis()

    # --- ML Artifacts ---
    try:
        from ml.model_loader import ModelLoader

        loader = ModelLoader()
        if loader.is_loaded:
            ml_globals["predictor"] = loader.model
            ml_globals["preprocessor"] = loader.preprocessor
            ml_globals["explainer"] = loader.explainer
            ml_globals["feature_names"] = loader.feature_names
            logger.info(
                "ml_models_loaded_successfully",
                algorithm=type(loader.model).__name__,
            )
        else:
            logger.warning(
                "ml_model_artifacts_not_found",
                hint="Run `python -m ml.train_pipeline` to generate model files.",
            )
    except Exception as exc:
        logger.error("ml_model_load_failed", error=str(exc))

    yield

    # --- Shutdown ---
    await shutdown_redis()
    logger.info("application_shutdown")


app = FastAPI(
    title="Customer Intelligence Platform API",
    description=(
        "Enterprise-grade REST API exposing customer churn prediction, "
        "analytics, background task management, and SHAP explainability. "
        "Powered by FastAPI + SQLAlchemy + Redis + Celery + SHAP."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------
app.add_exception_handler(PlatformError, platform_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(ObservabilityMiddleware)
app.add_middleware(RequestIDMiddleware)

from mlops.health import router as health_router
from mlops.metrics import router as metrics_router
from mlops.tracing import TracingMiddleware
from mlops.security import SecurityHeadersMiddleware, SimulatedJWTMiddleware

# MLOps Middlewares
app.add_middleware(TracingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SimulatedJWTMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(api_router)
app.include_router(health_router)
app.include_router(metrics_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_DEBUG,
        log_level=settings.APP_LOG_LEVEL.lower(),
    )
