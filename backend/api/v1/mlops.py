"""
Enterprise AI Customer Intelligence Platform — MLOps API Router.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import get_async_session

from mlops.repository import MLOpsRepository
from mlops.model_registry import ModelRegistry
from mlops.schemas import ModelRegistrySchema, ExperimentSchema, DriftReportSchema, AlertSchema
from mlops.data_quality import DataQualityChecker
from mlops.drift_detection import DriftDetector

router = APIRouter(prefix="/mlops", tags=["MLOps"])

def get_repository(session: AsyncSession = Depends(get_async_session)) -> MLOpsRepository:
    return MLOpsRepository(session)

@router.get("/models")
async def list_models(repo: MLOpsRepository = Depends(get_repository)):
    models = await repo.get_all_models()
    return [ModelRegistrySchema.model_validate(m) for m in models]

@router.get("/models/{version}", response_model=ModelRegistrySchema)
async def get_model(version: int, repo: MLOpsRepository = Depends(get_repository)):
    model = await repo.get_model_by_version(version)
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found.")
    return ModelRegistrySchema.model_validate(model)

@router.post("/models/{version}/rollback", response_model=ModelRegistrySchema)
async def rollback_model(version: int, repo: MLOpsRepository = Depends(get_repository)):
    registry = ModelRegistry(repo)
    try:
        prev_model = await registry.rollback(version)
        return ModelRegistrySchema.model_validate(prev_model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/experiments")
async def list_experiments(repo: MLOpsRepository = Depends(get_repository)):
    exps = await repo.get_recent_experiments()
    return [ExperimentSchema.model_validate(e) for e in exps]

@router.get("/drift")
async def get_drift(repo: MLOpsRepository = Depends(get_repository)):
    drifts = await repo.get_recent_drift_reports()
    return [DriftReportSchema.model_validate(d) for d in drifts]

@router.get("/data-quality")
async def get_data_quality(session: AsyncSession = Depends(get_async_session)):
    checker = DataQualityChecker(session)
    report = await checker.run_checks()
    return report

@router.get("/alerts")
async def list_alerts(repo: MLOpsRepository = Depends(get_repository)):
    alerts = await repo.get_recent_alerts()
    return [AlertSchema.model_validate(a) for a in alerts]
