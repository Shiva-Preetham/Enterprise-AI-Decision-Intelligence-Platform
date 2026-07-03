from typing import List
from backend.repositories.customer_repository import CustomerRepository
from backend.schemas.customer import CustomerProfileResponse, CustomerResponse, FeatureStoreResponse
from backend.core.exceptions import ResourceNotFoundError

class CustomerService:
    def __init__(self, repository: CustomerRepository, prediction_service=None):
        self.repository = repository
        self.prediction_service = prediction_service

    async def get_customer_profile(self, customer_id: str) -> CustomerProfileResponse:
        customer = await self.repository.get_customer(customer_id)
        if not customer:
            raise ResourceNotFoundError(f"Customer {customer_id} not found")
            
        features = await self.repository.get_customer_features(customer_id)
        
        customer_resp = CustomerResponse.model_validate(customer)
        feature_resp = FeatureStoreResponse.model_validate(features) if features else None
        
        prediction = None
        if self.prediction_service and features:
            try:
                prediction_model = self.prediction_service.predict(customer_id, features)
                prediction = prediction_model.model_dump()
            except Exception:
                prediction = None

        return CustomerProfileResponse(
            customer=customer_resp,
            features=feature_resp,
            prediction=prediction
        )

    async def get_customer_timeline(self, customer_id: str) -> dict:
        """Returns chronological events for a customer."""
        orders = await self.repository.get_recent_orders(customer_id)
        reviews = await self.repository.get_recent_reviews(customer_id)
        
        # Simplified timeline logic for the dashboard
        return {
            "recent_orders": [{"id": o.order_id, "status": o.order_status} for o in orders],
            "recent_reviews": [{"id": r.review_id, "score": r.review_score} for r in reviews]
        }
