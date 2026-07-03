from fastapi import APIRouter, Depends
from backend.services.model_service import ModelService
from backend.api.dependencies import get_model_service
from backend.core.responses import SuccessResponse

router = APIRouter(prefix="/model", tags=["Model"])

@router.get("/performance", response_model=SuccessResponse[dict])
async def get_model_performance(service: ModelService = Depends(get_model_service)):
    performance = service.get_performance_metrics()
    return SuccessResponse(
        message="Model performance metrics retrieved successfully",
        data=performance
    )
