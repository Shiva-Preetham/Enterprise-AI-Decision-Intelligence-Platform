"""
Enterprise AI Customer Intelligence Platform — Customer Service.

Orchestrates customer-related business operations with read-through caching.
Routers call this service, never the repository directly.
"""

from __future__ import annotations

from typing import List

from structlog import get_logger

from backend.cache.keys import CacheKeys
from backend.cache.service import CacheService
from backend.core.exceptions import ResourceNotFoundError
from backend.repositories.customer_repository import CustomerRepository
from backend.schemas.customer import CustomerProfileResponse, CustomerResponse, FeatureStoreResponse

logger = get_logger(__name__)


class CustomerService:
    """Business logic for all customer operations with caching.

    Architecture: Router -> CustomerService -> CustomerRepository -> Database
                                            -> CacheService -> Redis

    Args:
        repository: CustomerRepository instance (injected via DI).
        prediction_service: Optional PredictionService for churn inference.
        cache: CacheService instance (injected via DI).
    """

    def __init__(self, repository: CustomerRepository, prediction_service=None, cache: CacheService = None) -> None:
        self.repository = repository
        self.prediction_service = prediction_service
        self.cache = cache or CacheService()

    async def get_all_customers(self, skip: int = 0, limit: int = 100) -> List:
        """Returns a paginated list of customers."""
        return await self.repository.get_customers_paginated(skip, limit)

    async def get_customer_profile(self, customer_id: str) -> CustomerProfileResponse:
        """Builds a complete Customer 360 profile with read-through caching.

        Cache flow:
            1. Check Redis for cached profile.
            2. On miss, query database, build profile, cache it.
            3. Return the profile.
        """
        # Read-through cache
        cache_key = CacheKeys.customer(customer_id)
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return CustomerProfileResponse(**cached)

        # Cache miss — build from database
        customer = await self.repository.get_customer(customer_id)
        if not customer:
            raise ResourceNotFoundError(f"Customer '{customer_id}' not found")

        features = await self.repository.get_customer_features(customer_id)

        customer_resp = CustomerResponse.model_validate(customer)
        feature_resp = FeatureStoreResponse.model_validate(features) if features else None

        prediction = None
        if self.prediction_service and features:
            try:
                prediction_model = self.prediction_service.predict(customer_id, features)
                prediction = prediction_model.model_dump()
            except Exception as exc:
                logger.warning(
                    "prediction_unavailable_for_profile",
                    customer_id=customer_id,
                    error=str(exc),
                )

        profile = CustomerProfileResponse(
            customer=customer_resp,
            features=feature_resp,
            prediction=prediction,
        )

        # Populate cache
        await self.cache.set(cache_key, profile.model_dump(mode="json"), ttl=300)

        return profile

    async def get_customer_timeline(self, customer_id: str) -> dict:
        """Returns chronological events for a customer."""
        customer = await self.repository.get_customer(customer_id)
        if not customer:
            raise ResourceNotFoundError(f"Customer '{customer_id}' not found")

        orders = await self.repository.get_recent_orders(customer_id)
        reviews = await self.repository.get_recent_reviews(customer_id)

        return {
            "customer_id": customer_id,
            "recent_orders": [
                {
                    "order_id": o.order_id,
                    "status": o.order_status,
                    "purchase_date": str(o.order_purchase_timestamp),
                }
                for o in orders
            ],
            "recent_reviews": [
                {
                    "review_id": r.review_id,
                    "score": r.review_score,
                    "created_at": str(r.review_creation_date),
                }
                for r in reviews
            ],
        }
