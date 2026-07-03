"""
Enterprise AI Customer Intelligence Platform — Application Entrypoint.

Configures and creates the FastAPI application instance. Handles:
- ML model loading on startup (once, not per-request).
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
    """FastAPI lifespan: runs at startup and shutdown.

    Startup loads all ML artifacts into the global singleton so they are
    available for every request without re-loading from disk each time.
    The API still starts successfully even if model files do not exist yet
    — the health endpoint will report `ML Model Loaded: false`.

    Shutdown logs the event for observability.
    """
    logger.info("application_startup", env=settings.APP_ENV, version="1.0.0")

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

    logger.info("application_shutdown")


app = FastAPI(
    title="Customer Intelligence Platform API",
    description=(
        "Enterprise-grade REST API exposing customer churn prediction, "
        "analytics, and SHAP explainability. Powered by FastAPI + SQLAlchemy + SHAP."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# Exception Handlers — order does not matter for handlers
# ---------------------------------------------------------------------------
app.add_exception_handler(PlatformError, platform_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# ---------------------------------------------------------------------------
# Middleware — order IS important (outermost = last added)
# RequestIDMiddleware must execute before ObservabilityMiddleware so the
# request_id is bound to structlog before any logging occurs.
# ---------------------------------------------------------------------------
app.add_middleware(ObservabilityMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if hasattr(settings, "CORS_ORIGINS") else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_DEBUG,
        log_level=settings.APP_LOG_LEVEL.lower(),
    )
