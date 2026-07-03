from pydantic import BaseModel

class PredictionRequest(BaseModel):
    customer_id: str

class PredictionResponse(BaseModel):
    customer_id: str
    probability: float
    predicted_label: int
    risk_category: str

class SHAPExplanationResponse(BaseModel):
    customer_id: str
    top_features: dict
    positive_contributors: dict
    negative_contributors: dict
    business_explanation: str
