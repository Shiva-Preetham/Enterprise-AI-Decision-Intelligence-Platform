"""
MLOps Repository layer for direct database access.
"""
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, update

from .models import ModelRegistryModel, ExperimentModel, DriftReportModel, AlertModel

class MLOpsRepository:
    """Repository handling all database access for the MLOps schema."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    # --- Model Registry ---
    async def create_model_version(self, model: ModelRegistryModel) -> ModelRegistryModel:
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_model_by_version(self, version: int) -> Optional[ModelRegistryModel]:
        stmt = select(ModelRegistryModel).where(ModelRegistryModel.version == version)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_model(self) -> Optional[ModelRegistryModel]:
        stmt = select(ModelRegistryModel).order_by(desc(ModelRegistryModel.version)).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_production_model(self) -> Optional[ModelRegistryModel]:
        stmt = select(ModelRegistryModel).where(ModelRegistryModel.deployment_status == "production").order_by(desc(ModelRegistryModel.version)).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_models(self) -> List[ModelRegistryModel]:
        stmt = select(ModelRegistryModel).order_by(desc(ModelRegistryModel.version))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_deployment_status(self, version: int, status: str) -> Optional[ModelRegistryModel]:
        stmt = select(ModelRegistryModel).where(ModelRegistryModel.version == version)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.deployment_status = status
            await self.session.commit()
            await self.session.refresh(model)
        return model

    # --- Experiments ---
    async def create_experiment(self, exp: ExperimentModel) -> ExperimentModel:
        self.session.add(exp)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def get_recent_experiments(self, limit: int = 10) -> List[ExperimentModel]:
        stmt = select(ExperimentModel).order_by(desc(ExperimentModel.timestamp)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --- Drift Reports ---
    async def create_drift_report(self, report: DriftReportModel) -> DriftReportModel:
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_recent_drift_reports(self, limit: int = 5) -> List[DriftReportModel]:
        stmt = select(DriftReportModel).order_by(desc(DriftReportModel.timestamp)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --- Alerts ---
    async def create_alert(self, alert: AlertModel) -> AlertModel:
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def get_recent_alerts(self, limit: int = 20) -> List[AlertModel]:
        stmt = select(AlertModel).order_by(desc(AlertModel.timestamp)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --- External Data Access (for MLOps use only) ---
    async def get_all_customer_features(self) -> List[Any]:
        from backend.models.customer_feature_store import CustomerFeatureStore
        stmt = select(CustomerFeatureStore)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def check_database_health(self) -> None:
        from sqlalchemy import text
        await self.session.execute(text("SELECT 1"))
