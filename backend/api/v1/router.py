from fastapi import APIRouter

from backend.api.v1.health import router as health_router
from backend.api.v1.customers import router as customers_router
from backend.api.v1.predictions import router as predictions_router
from backend.api.v1.analytics import router as analytics_router
from backend.api.v1.models import router as models_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(customers_router)
api_router.include_router(predictions_router)
api_router.include_router(analytics_router)
api_router.include_router(models_router)
