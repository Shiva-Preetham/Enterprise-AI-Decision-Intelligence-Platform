"""
Enterprise AI Customer Intelligence Platform — Customer Repository.

All SQLAlchemy queries for customer-related operations. The service layer
calls these methods; SQL never appears in service or router code.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.models import Customer, CustomerFeatureStore, Order, Review


class CustomerRepository:
    """Database access layer for all customer queries.

    Args:
        session: An async SQLAlchemy session (injected per-request).
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Returns the Customer record for a given unique customer ID."""
        stmt = select(Customer).where(Customer.customer_unique_id == customer_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_customer_features(self, customer_id: str) -> Optional[CustomerFeatureStore]:
        """Returns the Feature Store record for a given unique customer ID."""
        stmt = select(CustomerFeatureStore).where(
            CustomerFeatureStore.customer_unique_id == customer_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_customers_paginated(
        self, skip: int = 0, limit: int = 100
    ) -> List[Customer]:
        """Returns a page of customers ordered by customer_unique_id.

        Args:
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.

        Returns:
            List of Customer ORM objects.
        """
        stmt = (
            select(Customer)
            .order_by(Customer.customer_unique_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_orders(
        self, customer_id: str, limit: int = 5
    ) -> List[Order]:
        """Returns the most recent orders for a customer, newest first."""
        stmt = (
            select(Order)
            .where(
                Order.customer_id.in_(
                    select(Customer.customer_id).where(
                        Customer.customer_unique_id == customer_id
                    )
                )
            )
            .order_by(Order.order_purchase_timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_reviews(
        self, customer_id: str, limit: int = 5
    ) -> List[Review]:
        """Returns the most recent reviews left by a customer, newest first."""
        stmt = (
            select(Review)
            .join(Order, Review.order_id == Order.order_id)
            .where(
                Order.customer_id.in_(
                    select(Customer.customer_id).where(
                        Customer.customer_unique_id == customer_id
                    )
                )
            )
            .order_by(Review.review_creation_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
