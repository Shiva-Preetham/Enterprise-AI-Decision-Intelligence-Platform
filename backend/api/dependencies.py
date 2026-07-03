"""
Enterprise AI Customer Intelligence Platform — API Dependencies.

Defines all FastAPI Depends() providers for database sessions, repositories,
services, cache, and the ML singleton.
"""

from __future__ import annotations

from functools import lru_cache
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.cache.service import CacheService
from backend.db.session import AsyncSessionFactory
from backend.repositories.analytics_repository import AnalyticsRepository
from backend.repositories.customer_repository import CustomerRepository
from backend.services.analytics_service import AnalyticsService
from backend.services.customer_service import CustomerService
from backend.services.model_service import ModelService
from backend.services.prediction_service import PredictionService

# ---------------------------------------------------------------------------
# ML Singleton — loaded once at startup via lifespan(), never per-request.
# ---------------------------------------------------------------------------
ml_globals: dict = {
    "predictor": None,
    "explainer": None,
    "feature_names": None,
    "preprocessor": None,
}


# ---------------------------------------------------------------------------
# Database Session
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a fresh async database session per request, closed on exit."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def get_cache_service() -> CacheService:
    """Returns a CacheService instance. Stateless, safe to create per-request."""
    return CacheService()


# ---------------------------------------------------------------------------
# Repositories
# ---------------------------------------------------------------------------

def get_customer_repository(
    session: AsyncSession = Depends(get_db),
) -> CustomerRepository:
    return CustomerRepository(session)


def get_analytics_repository(
    session: AsyncSession = Depends(get_db),
) -> AnalyticsRepository:
    return AnalyticsRepository(session)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_model_service() -> ModelService:
    """Singleton: reads model_metadata.json once, not per-request."""
    return ModelService()


def get_prediction_service() -> PredictionService:
    """Returns a PredictionService backed by globally cached ML artifacts."""
    return PredictionService(
        predictor_instance=ml_globals["predictor"],
        preprocessor_instance=ml_globals["preprocessor"],
        explainer_instance=ml_globals["explainer"],
        feature_names=ml_globals["feature_names"],
    )


def get_customer_service(
    repository: CustomerRepository = Depends(get_customer_repository),
    prediction_service: PredictionService = Depends(get_prediction_service),
    cache: CacheService = Depends(get_cache_service),
) -> CustomerService:
    return CustomerService(repository, prediction_service, cache)


def get_analytics_service(
    repository: AnalyticsRepository = Depends(get_analytics_repository),
    model_service: ModelService = Depends(get_model_service),
    cache: CacheService = Depends(get_cache_service),
) -> AnalyticsService:
    return AnalyticsService(repository, model_service, cache)
