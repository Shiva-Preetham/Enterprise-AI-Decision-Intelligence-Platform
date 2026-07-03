"""
Enterprise AI Customer Intelligence Platform — Analytics Service.

Orchestrates all analytics and dashboard operations.
Business logic lives here; routers delegate to this service.
"""

from __future__ import annotations

from structlog import get_logger

from backend.repositories.analytics_repository import AnalyticsRepository
from backend.schemas.analytics import DashboardMetricsResponse
from backend.services.model_service import ModelService

logger = get_logger(__name__)

# RFM Segment definitions — stable across sprints
_RFM_SEGMENTS = {
    "Champions": "Bought recently, buy often and spend the most.",
    "Loyal Customers": "Buy on a regular basis.",
    "At Risk": "Bought often in the past, but not recently.",
    "Lost": "Haven't bought for a long time and show low engagement.",
}


class AnalyticsService:
    """Business logic for analytics and dashboard APIs.

    Args:
        repository: AnalyticsRepository instance (injected via DI).
        model_service: ModelService for reading model metadata.
    """

    def __init__(self, repository: AnalyticsRepository, model_service: ModelService) -> None:
        self.repository = repository
        self.model_service = model_service

    async def get_dashboard_metrics(self) -> DashboardMetricsResponse:
        """Aggregates all high-level platform metrics for the dashboard.

        Note on high_risk_customers: This field requires a count query on the
        analytics.customer_feature_store using churn_label=1 (Feature Store must
        be populated). The analytics_repository will be extended in Sprint 5.

        Returns:
            DashboardMetricsResponse with all platform KPIs.
        """
        total = await self.repository.get_total_customers()
        avg_metrics = await self.repository.get_average_metrics()
        high_risk_count = await self.repository.get_high_risk_customer_count()

        model_info = self.model_service.get_model_info()

        return DashboardMetricsResponse(
            total_customers=total,
            high_risk_customers=high_risk_count,
            average_clv=avg_metrics["avg_clv"],
            average_review_score=avg_metrics["avg_review_score"],
            average_order_value=avg_metrics["avg_order_value"],
            average_churn_probability=avg_metrics.get("avg_churn_probability", 0.0),
            latest_feature_store_version=model_info.get("FeatureVersion", "1.0"),
            model_version=model_info.get("PipelineVersion", "1.0"),
        )

    def get_rfm_segment_definitions(self) -> dict:
        """Returns RFM segment names with business definitions.

        This is a static reference — actual customer-level RFM segmentation
        will be added in Sprint 5 when the analytics repository is extended.
        """
        return {
            "segments": list(_RFM_SEGMENTS.keys()),
            "definitions": _RFM_SEGMENTS,
        }
