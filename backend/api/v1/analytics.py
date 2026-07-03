"""
Enterprise AI Customer Intelligence Platform — Analytics Router (API v1).

All business logic delegated to AnalyticsService. No hardcoded values here.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.dependencies import get_analytics_service
from backend.core.responses import SuccessResponse
from backend.schemas.analytics import DashboardMetricsResponse
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/dashboard",
    response_model=SuccessResponse[DashboardMetricsResponse],
    summary="Dashboard metrics",
    description=(
        "Returns all high-level platform KPIs in a single request: "
        "total customers, high-risk count, average CLV, review scores, "
        "churn probability, and active model version. "
        "Designed to power the React dashboard with one network call."
    ),
)
async def get_dashboard(
    service: AnalyticsService = Depends(get_analytics_service),
) -> SuccessResponse:
    metrics = await service.get_dashboard_metrics()
    return SuccessResponse(
        message="Dashboard metrics retrieved successfully",
        data=metrics,
    )


@router.get(
    "/rfm",
    response_model=SuccessResponse[dict],
    summary="RFM segment overview",
    description=(
        "Returns the RFM segment definitions. "
        "Customer-level segmentation will be added in Sprint 5."
    ),
)
async def get_rfm_segments(
    service: AnalyticsService = Depends(get_analytics_service),
) -> SuccessResponse:
    data = service.get_rfm_segment_definitions()
    return SuccessResponse(
        message="RFM segment definitions retrieved successfully",
        data=data,
    )
