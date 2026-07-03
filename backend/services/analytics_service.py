"""
Enterprise AI Customer Intelligence Platform — Analytics Service.

Orchestrates analytics and dashboard operations with caching.
"""

from __future__ import annotations

from structlog import get_logger

from backend.cache.keys import CacheKeys
from backend.cache.service import CacheService
from backend.repositories.analytics_repository import AnalyticsRepository
from backend.schemas.analytics import DashboardMetricsResponse
from backend.services.model_service import ModelService

logger = get_logger(__name__)

_RFM_SEGMENTS = {
    "Champions": "Bought recently, buy often and spend the most.",
    "Loyal Customers": "Buy on a regular basis.",
    "At Risk": "Bought often in the past, but not recently.",
    "Lost": "Haven't bought for a long time and show low engagement.",
}


class AnalyticsService:
    """Business logic for analytics with read-through caching.

    Args:
        repository: AnalyticsRepository instance (injected via DI).
        model_service: ModelService for reading model metadata.
        cache: CacheService instance (injected via DI).
    """

    def __init__(self, repository: AnalyticsRepository, model_service: ModelService, cache: CacheService = None) -> None:
        self.repository = repository
        self.model_service = model_service
        self.cache = cache or CacheService()

    async def get_dashboard_metrics(self) -> DashboardMetricsResponse:
        """Aggregates platform metrics with read-through caching.

        Cache flow:
            1. Check Redis for cached dashboard data.
            2. On miss, query database, build response, cache it (60s TTL).
            3. Return metrics.
        """
        cache_key = CacheKeys.dashboard()
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return DashboardMetricsResponse(**cached)

        # Cache miss — query from database
        total = await self.repository.get_total_customers()
        avg_metrics = await self.repository.get_average_metrics()
        high_risk_count = await self.repository.get_high_risk_customer_count()

        model_info = self.model_service.get_model_info()

        response = DashboardMetricsResponse(
            total_customers=total,
            high_risk_customers=high_risk_count,
            average_clv=avg_metrics["avg_clv"],
            average_review_score=avg_metrics["avg_review_score"],
            average_order_value=avg_metrics["avg_order_value"],
            average_churn_probability=avg_metrics.get("avg_churn_probability", 0.0),
            latest_feature_store_version=model_info.get("FeatureVersion", "1.0"),
            model_version=model_info.get("PipelineVersion", "1.0"),
        )

        # Short TTL — dashboard data changes frequently
        await self.cache.set(cache_key, response.model_dump(mode="json"), ttl=60)

        return response

    def get_rfm_segment_definitions(self) -> dict:
        """Returns RFM segment names with business definitions."""
        return {
            "segments": list(_RFM_SEGMENTS.keys()),
            "definitions": _RFM_SEGMENTS,
        }
