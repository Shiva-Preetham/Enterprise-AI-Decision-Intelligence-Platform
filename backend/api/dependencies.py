from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import async_session_factory
from backend.repositories.customer_repository import CustomerRepository
from backend.repositories.analytics_repository import AnalyticsRepository
from backend.services.customer_service import CustomerService
from backend.services.analytics_service import AnalyticsService
from backend.services.model_service import ModelService
from backend.services.prediction_service import PredictionService

# Global cache for ML models (loaded at startup)
ml_globals = {
    "predictor": None,
    "explainer": None,
    "feature_names": None
}

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

def get_customer_repository(session: AsyncSession = Depends(get_db)) -> CustomerRepository:
    return CustomerRepository(session)

def get_analytics_repository(session: AsyncSession = Depends(get_db)) -> AnalyticsRepository:
    return AnalyticsRepository(session)

def get_model_service() -> ModelService:
    return ModelService()

def get_prediction_service() -> PredictionService:
    return PredictionService(
        predictor_instance=ml_globals["predictor"],
        explainer_instance=ml_globals["explainer"],
        feature_names=ml_globals["feature_names"]
    )

def get_customer_service(
    repository: CustomerRepository = Depends(get_customer_repository),
    prediction_service: PredictionService = Depends(get_prediction_service)
) -> CustomerService:
    return CustomerService(repository, prediction_service)

def get_analytics_service(
    repository: AnalyticsRepository = Depends(get_analytics_repository),
    model_service: ModelService = Depends(get_model_service)
) -> AnalyticsService:
    return AnalyticsService(repository, model_service)
