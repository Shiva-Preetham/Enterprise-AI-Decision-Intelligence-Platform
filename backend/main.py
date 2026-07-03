from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from structlog import get_logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.core.middleware import RequestIDMiddleware, ObservabilityMiddleware
from backend.core.exceptions import PlatformError, global_exception_handler, http_exception_handler, platform_exception_handler
from backend.api.v1.router import api_router
from backend.api.dependencies import ml_globals
from backend.config import settings

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown logic.
    Loads ML models into memory once so they don't block requests.
    """
    logger.info("application_startup", env=settings.APP_ENV)
    
    # Load ML artifacts globally
    try:
        from ml.model_loader import ModelLoader
        loader = ModelLoader()
        ml_globals["predictor"] = loader.model
        ml_globals["explainer"] = loader.explainer
        ml_globals["feature_names"] = loader.feature_names
        logger.info("ml_models_loaded_successfully")
    except Exception as e:
        logger.error("ml_model_load_failed", error=str(e))
        # Don't crash the app if models aren't ready, the API should still start
        # so we can fix it or upload models later.
    
    yield
    
    logger.info("application_shutdown")

app = FastAPI(
    title="Customer Intelligence Platform API",
    description="Enterprise REST API for Customer Churn Prediction and Analytics.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception Handlers
app.add_exception_handler(PlatformError, platform_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Middleware
# Order matters: RequestID must be first to ensure all subsequent logs have it
app.add_middleware(ObservabilityMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=settings.APP_DEBUG)
