from fastapi import APIRouter, Depends
from backend.services.analytics_service import AnalyticsService
from backend.api.dependencies import get_analytics_service
from backend.core.responses import SuccessResponse
from backend.schemas.analytics import DashboardMetricsResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard", response_model=SuccessResponse[DashboardMetricsResponse])
async def get_dashboard(service: AnalyticsService = Depends(get_analytics_service)):
    metrics = await service.get_dashboard_metrics()
    return SuccessResponse(
        message="Dashboard metrics retrieved successfully",
        data=metrics
    )

@router.get("/rfm", response_model=SuccessResponse[dict])
async def get_rfm_segments(service: AnalyticsService = Depends(get_analytics_service)):
    # Placeholder for RFM endpoint implementation
    return SuccessResponse(
        message="RFM segments retrieved successfully",
        data={
            "segments": ["Champions", "Loyal", "At Risk", "Lost"],
            "distribution": {"Champions": 25, "Loyal": 35, "At Risk": 20, "Lost": 20}
        }
    )
