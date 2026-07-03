"""
Enterprise AI Customer Intelligence Platform — Customers Router (API v1).

Thin HTTP layer. All business logic delegated to CustomerService.
Routers must never call repositories directly.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.dependencies import get_customer_service
from backend.core.responses import SuccessResponse
from backend.schemas.common import PaginatedResponse, PaginationParams
from backend.schemas.customer import CustomerProfileResponse
from backend.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get(
    "",
    response_model=SuccessResponse[PaginatedResponse],
    summary="List customers",
    description="Returns a paginated list of customers from the database.",
)
async def list_customers(
    params: PaginationParams = Depends(),
    service: CustomerService = Depends(get_customer_service),
) -> SuccessResponse:
    customers = await service.get_all_customers(params.skip, params.limit)
    return SuccessResponse(
        message="Customers retrieved successfully",
        data=PaginatedResponse(
            items=customers,
            total=len(customers),
            skip=params.skip,
            limit=params.limit,
        ),
    )


@router.get(
    "/{customer_id}/profile",
    response_model=SuccessResponse[CustomerProfileResponse],
    summary="Customer 360 profile",
    description=(
        "Returns the complete Customer 360 profile: demographics, Feature Store values, "
        "and a real-time churn prediction if the ML model is loaded."
    ),
)
async def get_customer_profile(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service),
) -> SuccessResponse:
    profile = await service.get_customer_profile(customer_id)
    return SuccessResponse(
        message="Customer profile retrieved successfully",
        data=profile,
    )


@router.get(
    "/{customer_id}/timeline",
    response_model=SuccessResponse[dict],
    summary="Customer event timeline",
    description="Returns a chronological list of orders and reviews for a customer.",
)
async def get_customer_timeline(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service),
) -> SuccessResponse:
    timeline = await service.get_customer_timeline(customer_id)
    return SuccessResponse(
        message="Customer timeline retrieved successfully",
        data=timeline,
    )
