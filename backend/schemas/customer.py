from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    customer_unique_id: str
    customer_zip_code_prefix: int
    customer_city: str
    customer_state: str

class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

class FeatureStoreResponse(BaseModel):
    recency_days: Optional[float]
    frequency_90d: Optional[float]
    total_lifetime_value: Optional[float]
    avg_order_value: Optional[float]
    churn_label: Optional[int]
    
    model_config = ConfigDict(from_attributes=True)

class CustomerProfileResponse(BaseModel):
    customer: CustomerResponse
    features: Optional[FeatureStoreResponse]
    prediction: Optional[dict] = None
