from pydantic import BaseModel

class DashboardMetricsResponse(BaseModel):
    total_customers: int
    high_risk_customers: int
    average_clv: float
    average_review_score: float
    average_order_value: float
    average_churn_probability: float
    latest_feature_store_version: str
    model_version: str
