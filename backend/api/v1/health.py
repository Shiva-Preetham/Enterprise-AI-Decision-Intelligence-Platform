"""
Enterprise AI Customer Intelligence Platform — Health Router (API v1).

Returns system status for monitoring and readiness probes.
Used by load balancers, Kubernetes liveness/readiness probes, and dashboards.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import text
from structlog import get_logger

from backend.api.dependencies import get_model_service, ml_globals
from backend.config import settings
from backend.core.responses import SuccessResponse
from backend.db.engine import async_engine
from backend.services.model_service import ModelService

logger = get_logger(__name__)
_startup_time = time.time()

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="System health check",
    description=(
        "Returns the health status of all platform components. "
        "Suitable for use as a Kubernetes readiness probe."
    ),
)
async def health_check(
    model_service: ModelService = Depends(get_model_service),
) -> SuccessResponse:
    # Database connectivity check
    db_status = "ok"
    db_error: str | None = None
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = "error"
        db_error = str(exc)
        logger.warning("health_check_db_failed", error=db_error)

    model_info = model_service.get_model_info()
    uptime_seconds = round(time.time() - _startup_time)

    return SuccessResponse(
        message="System health status",
        data={
            "api_status": "ok",
            "database_status": db_status,
            "database_error": db_error,
            "ml_model_loaded": ml_globals["predictor"] is not None,
            "application_version": "1.0.0",
            "environment": settings.APP_ENV,
            "pipeline_version": model_info.get("PipelineVersion", "unknown"),
            "feature_version": model_info.get("FeatureVersion", "unknown"),
            "uptime_seconds": uptime_seconds,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
