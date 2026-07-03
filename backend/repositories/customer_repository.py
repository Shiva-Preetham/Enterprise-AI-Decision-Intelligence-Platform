from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional, List

from backend.models import Customer, CustomerFeatureStore, Order, Review

class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        stmt = select(Customer).where(Customer.customer_unique_id == customer_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_customer_features(self, customer_id: str) -> Optional[CustomerFeatureStore]:
        stmt = select(CustomerFeatureStore).where(CustomerFeatureStore.customer_unique_id == customer_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_customers_paginated(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        stmt = select(Customer).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_recent_orders(self, customer_id: str, limit: int = 5) -> List[Order]:
        stmt = select(Order).where(Order.customer_id.in_(
            select(Customer.customer_id).where(Customer.customer_unique_id == customer_id)
        )).order_by(Order.order_purchase_timestamp.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_reviews(self, customer_id: str, limit: int = 5) -> List[Review]:
        # Reviews are joined to orders
        stmt = select(Review).join(Order, Review.order_id == Order.order_id).where(
            Order.customer_id.in_(
                select(Customer.customer_id).where(Customer.customer_unique_id == customer_id)
            )
        ).order_by(Review.review_creation_date.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
