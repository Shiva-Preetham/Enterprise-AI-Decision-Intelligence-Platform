from fastapi import APIRouter, Depends
from backend.services.prediction_service import PredictionService
from backend.api.dependencies import get_prediction_service, get_customer_repository
from backend.repositories.customer_repository import CustomerRepository
from backend.core.responses import SuccessResponse
from backend.core.exceptions import ResourceNotFoundError
from backend.schemas.prediction import PredictionRequest, PredictionResponse, SHAPExplanationResponse

router = APIRouter(prefix="/predict", tags=["Predictions"])

@router.post("", response_model=SuccessResponse[PredictionResponse])
async def create_prediction(
    request: PredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
    customer_repo: CustomerRepository = Depends(get_customer_repository)
):
    features = await customer_repo.get_customer_features(request.customer_id)
    if not features:
        raise ResourceNotFoundError(f"Feature store data not found for {request.customer_id}")
        
    prediction = prediction_service.predict(request.customer_id, features)
    return SuccessResponse(
        message="Prediction successful",
        data=prediction
    )

@router.get("/{customer_id}/explanation", response_model=SuccessResponse[SHAPExplanationResponse])
async def get_explanation(
    customer_id: str,
    prediction_service: PredictionService = Depends(get_prediction_service),
    customer_repo: CustomerRepository = Depends(get_customer_repository)
):
    features = await customer_repo.get_customer_features(customer_id)
    if not features:
        raise ResourceNotFoundError(f"Feature store data not found for {customer_id}")
        
    explanation = prediction_service.explain(customer_id, features)
    return SuccessResponse(
        message="Explanation generated successfully",
        data=explanation
    )
