"""
Enterprise AI Customer Intelligence Platform — Analytics Repository.

All SQLAlchemy queries for analytics operations. Services call methods here;
raw SQL never appears in the Service or Router layers.
"""

from __future__ import annotations

from typing import Dict

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from structlog import get_logger

from backend.models import Customer, CustomerFeatureStore

logger = get_logger(__name__)


class AnalyticsRepository:
    """Database access layer for analytics and aggregation queries.

    Args:
        session: An async SQLAlchemy session (injected per-request).
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_total_customers(self) -> int:
        """Returns the total number of unique customers."""
        stmt = select(func.count(Customer.customer_unique_id.distinct()))
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_high_risk_customer_count(self) -> int:
        """Returns the number of customers flagged as churn risk (churn_label=1)."""
        stmt = select(func.count(CustomerFeatureStore.customer_unique_id)).where(
            CustomerFeatureStore.churn_label == 1
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_average_metrics(self) -> Dict[str, float]:
        """Aggregates key KPIs from the Customer Feature Store.

        Returns:
            Dict with avg_clv, avg_review_score, avg_order_value,
            and avg_churn_probability (churn_label mean used as proxy).
        """
        stmt = select(
            func.avg(CustomerFeatureStore.total_lifetime_value).label("avg_clv"),
            func.avg(CustomerFeatureStore.avg_review_score).label("avg_review_score"),
            func.avg(CustomerFeatureStore.avg_order_value).label("avg_order_value"),
            func.avg(CustomerFeatureStore.churn_label).label("avg_churn_probability"),
        )
        result = await self.session.execute(stmt)
        row = result.first()

        return {
            "avg_clv": round(float(row.avg_clv), 2) if row and row.avg_clv else 0.0,
            "avg_review_score": round(float(row.avg_review_score), 2) if row and row.avg_review_score else 0.0,
            "avg_order_value": round(float(row.avg_order_value), 2) if row and row.avg_order_value else 0.0,
            "avg_churn_probability": round(float(row.avg_churn_probability), 4) if row and row.avg_churn_probability else 0.0,
        }
