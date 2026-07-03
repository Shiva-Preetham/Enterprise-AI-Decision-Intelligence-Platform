from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Dict, Any

from backend.models import CustomerFeatureStore, Customer

class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_total_customers(self) -> int:
        stmt = select(func.count(Customer.customer_unique_id))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_average_metrics(self) -> Dict[str, float]:
        stmt = select(
            func.avg(CustomerFeatureStore.total_lifetime_value).label("avg_clv"),
            func.avg(CustomerFeatureStore.avg_review_score).label("avg_review_score"),
            func.avg(CustomerFeatureStore.avg_order_value).label("avg_order_value")
        )
        result = await self.session.execute(stmt)
        row = result.first()
        return {
            "avg_clv": float(row.avg_clv) if row and row.avg_clv else 0.0,
            "avg_review_score": float(row.avg_review_score) if row and row.avg_review_score else 0.0,
            "avg_order_value": float(row.avg_order_value) if row and row.avg_order_value else 0.0,
        }
