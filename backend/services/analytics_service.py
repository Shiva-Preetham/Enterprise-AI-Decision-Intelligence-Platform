from backend.repositories.analytics_repository import AnalyticsRepository
from backend.schemas.analytics import DashboardMetricsResponse
from backend.services.model_service import ModelService

class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository, model_service: ModelService):
        self.repository = repository
        self.model_service = model_service

    async def get_dashboard_metrics(self) -> DashboardMetricsResponse:
        total = await self.repository.get_total_customers()
        avg_metrics = await self.repository.get_average_metrics()
        
        # We would typically get high_risk_customers from the Feature Store or Predictions table
        # For now, simulated based on total to ensure API functions
        high_risk_customers = int(total * 0.15)
        
        model_info = self.model_service.get_model_info()
        
        return DashboardMetricsResponse(
            total_customers=total,
            high_risk_customers=high_risk_customers,
            average_clv=avg_metrics["avg_clv"],
            average_review_score=avg_metrics["avg_review_score"],
            average_order_value=avg_metrics["avg_order_value"],
            average_churn_probability=0.25, # Simulated
            latest_feature_store_version=model_info.get("FeatureVersion", "1.0"),
            model_version=model_info.get("PipelineVersion", "1.0")
        )
