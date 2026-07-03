from fastapi import APIRouter, Depends
from backend.services.customer_service import CustomerService
from backend.api.dependencies import get_customer_service
from backend.core.responses import SuccessResponse
from backend.schemas.customer import CustomerProfileResponse
from backend.schemas.common import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("", response_model=SuccessResponse[PaginatedResponse])
async def list_customers(
    params: PaginationParams = Depends(),
    service: CustomerService = Depends(get_customer_service)
):
    customers = await service.repository.get_customers_paginated(params.skip, params.limit)
    return SuccessResponse(
        message="Customers retrieved successfully",
        data=PaginatedResponse(
            items=customers,
            total=len(customers),
            skip=params.skip,
            limit=params.limit
        )
    )

@router.get("/{customer_id}/profile", response_model=SuccessResponse[CustomerProfileResponse])
async def get_customer_profile(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service)
):
    profile = await service.get_customer_profile(customer_id)
    return SuccessResponse(
        message="Customer profile retrieved successfully",
        data=profile
    )

@router.get("/{customer_id}/timeline", response_model=SuccessResponse[dict])
async def get_customer_timeline(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service)
):
    timeline = await service.get_customer_timeline(customer_id)
    return SuccessResponse(
        message="Customer timeline retrieved successfully",
        data=timeline
    )
