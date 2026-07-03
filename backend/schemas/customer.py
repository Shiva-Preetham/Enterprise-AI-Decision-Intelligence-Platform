"""
Enterprise AI Customer Intelligence Platform — Customer Schemas.

Pydantic V2 DTOs for the Customer API layer. These are the only objects
returned to API clients — SQLAlchemy ORM models never cross the service boundary.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CustomerResponse(BaseModel):
    """Public representation of a customer record."""

    customer_unique_id: str = Field(..., description="Canonical business customer identifier")
    customer_zip_code_prefix: str = Field(..., description="ZIP code prefix (5 digits)")
    customer_city: str = Field(..., description="Customer city")
    customer_state: str = Field(..., description="Customer state (2-letter code)")

    model_config = ConfigDict(from_attributes=True)


class FeatureStoreResponse(BaseModel):
    """Feature Store values for a single customer.

    Exposes the most important analytical features. Metadata fields
    (feature_version, pipeline_version, computed_at) are intentionally
    excluded from the API response.
    """

    # RFM Features
    recency_days: Optional[int] = Field(None, description="Days since last purchase")
    frequency_90d: Optional[int] = Field(None, description="Number of orders in last 90 days")
    frequency_lifetime: Optional[int] = Field(None, description="Total lifetime orders")
    monetary_90d: Optional[float] = Field(None, description="Revenue in last 90 days (BRL)")
    total_lifetime_value: Optional[float] = Field(None, description="Total lifetime spend (BRL)")
    avg_order_value: Optional[float] = Field(None, description="Average order value (BRL)")

    # Review Features
    avg_review_score: Optional[float] = Field(None, description="Average review score (1–5)")
    last_review_score: Optional[float] = Field(None, description="Most recent review score")
    review_score_trend: Optional[float] = Field(None, description="Trend in review scores (positive = improving)")
    negative_review_ratio: Optional[float] = Field(None, description="Fraction of reviews rated 1–2")

    # Delivery Features
    late_delivery_rate: Optional[float] = Field(None, description="Fraction of orders delivered late")
    delivery_delay_avg: Optional[float] = Field(None, description="Average delivery delay in days")

    # Payment Features
    preferred_payment_type: Optional[str] = Field(None, description="Most used payment method")
    avg_installments: Optional[float] = Field(None, description="Average number of installments")

    # Target
    churn_label: Optional[int] = Field(None, description="Binary churn label (1=churned, 0=retained)")

    model_config = ConfigDict(from_attributes=True)


class CustomerProfileResponse(BaseModel):
    """Complete Customer 360 profile.

    Aggregates demographic data, Feature Store metrics, and an optional
    real-time churn prediction into a single response.
    """

    customer: CustomerResponse
    features: Optional[FeatureStoreResponse] = None
    prediction: Optional[dict] = None
