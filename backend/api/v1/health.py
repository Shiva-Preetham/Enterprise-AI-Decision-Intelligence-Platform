from fastapi import APIRouter, Depends
from typing import Dict, Any

from backend.api.dependencies import ml_globals, get_model_service
from backend.services.model_service import ModelService
from backend.core.responses import SuccessResponse
from backend.db.engine import async_engine
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=SuccessResponse[Dict[str, Any]])
async def health_check(model_service: ModelService = Depends(get_model_service)):
    db_status = "ok"
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = str(e)
        
    model_info = model_service.get_model_info()

    return SuccessResponse(
        message="System Health Status",
        data={
            "API Status": "ok",
            "Database Status": db_status,
            "ML Model Loaded": ml_globals["predictor"] is not None,
            "Application Version": "1.0.0",
            "Pipeline Version": model_info.get("PipelineVersion", "Unknown"),
            "Feature Version": model_info.get("FeatureVersion", "Unknown")
        }
    )
