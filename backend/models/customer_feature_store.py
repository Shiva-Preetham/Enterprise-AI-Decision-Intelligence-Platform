from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Float, Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import SCHEMA_ANALYTICS, Base


class CustomerFeatureStore(Base):
    """Customer-level Analytical Feature Store.
    
    Contains engineered features for ML model training and inference.
    """
    __tablename__ = "customer_feature_store"
    __table_args__ = {"schema": SCHEMA_ANALYTICS}

    customer_unique_id: Mapped[str] = mapped_column(String(32), primary_key=True)

    # RFM Features
    recency_days: Mapped[Optional[int]] = mapped_column(Integer)
    frequency_90d: Mapped[int] = mapped_column(Integer, default=0)
    monetary_90d: Mapped[float] = mapped_column(Float, default=0.0)
    avg_order_value: Mapped[float] = mapped_column(Float, default=0.0)
    total_lifetime_value: Mapped[float] = mapped_column(Float, default=0.0)
    frequency_lifetime: Mapped[int] = mapped_column(Integer, default=0)
    avg_lifetime_order_value: Mapped[float] = mapped_column(Float, default=0.0)

    # Purchase Features
    days_since_last_order: Mapped[Optional[int]] = mapped_column(Integer)
    order_gap_trend: Mapped[Optional[float]] = mapped_column(Float)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    avg_items_per_order: Mapped[float] = mapped_column(Float, default=0.0)

    # Payment Features
    preferred_payment_type: Mapped[Optional[str]] = mapped_column(String(50))
    avg_installments: Mapped[float] = mapped_column(Float, default=0.0)
    payment_type_changed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Delivery Features
    delivery_delay_avg: Mapped[Optional[float]] = mapped_column(Float)
    late_delivery_rate: Mapped[float] = mapped_column(Float, default=0.0)
    max_delivery_delay: Mapped[Optional[float]] = mapped_column(Float)

    # Review Features
    avg_review_score: Mapped[Optional[float]] = mapped_column(Float)
    last_review_score: Mapped[Optional[float]] = mapped_column(Float)
    review_score_trend: Mapped[Optional[float]] = mapped_column(Float)
    review_sentiment_score: Mapped[Optional[float]] = mapped_column(Float)
    has_negative_comment: Mapped[bool] = mapped_column(Boolean, default=False)
    negative_review_ratio: Mapped[float] = mapped_column(Float, default=0.0)

    # Product Features
    distinct_categories: Mapped[int] = mapped_column(Integer, default=0)
    category_entropy: Mapped[Optional[float]] = mapped_column(Float)
    dominant_category: Mapped[Optional[str]] = mapped_column(String(255))

    # Geographic Features
    customer_state: Mapped[Optional[str]] = mapped_column(String(2))
    customer_city: Mapped[Optional[str]] = mapped_column(String(255))

    # Target Label
    churn_label: Mapped[Optional[int]] = mapped_column(Integer)

    # Metadata
    feature_version: Mapped[str] = mapped_column(String(50))
    pipeline_version: Mapped[str] = mapped_column(String(50))
    computed_at: Mapped[datetime] = mapped_column(DateTime)
    data_snapshot_date: Mapped[datetime] = mapped_column(DateTime)
