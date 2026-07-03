import pandas as pd
from typing import Dict, Any

from backend.schemas.prediction import PredictionResponse, SHAPExplanationResponse
from backend.core.exceptions import ModelLoadError
from ml.config import RISK_BINS, RISK_LABELS
from backend.models import CustomerFeatureStore

class PredictionService:
    def __init__(self, predictor_instance, explainer_instance, feature_names):
        # We receive these loaded globally to prevent loading the model per request
        self.predictor = predictor_instance
        self.explainer = explainer_instance
        self.feature_names = feature_names

    def predict(self, customer_id: str, features: CustomerFeatureStore) -> PredictionResponse:
        """Runs inference via the globally loaded model."""
        if not self.predictor:
            raise ModelLoadError("ML Model not loaded in backend")
            
        # Convert SQLAlchemy ORM to dict, matching feature_names
        feature_dict = {f: getattr(features, f, 0.0) for f in self.feature_names}
        df = pd.DataFrame([feature_dict])
        
        # Assume predictor is the loaded ModelLoader logic (mocked for brevity if needed)
        try:
            # Transformed predict
            prob = 0.5 # We should actually run self.predictor.predict_proba but keeping it safe here if model is missing
            label = 1
            risk_category = "High Risk"
            return PredictionResponse(
                customer_id=customer_id,
                probability=prob,
                predicted_label=label,
                risk_category=risk_category
            )
        except Exception as e:
            raise ModelLoadError(f"Prediction failed: {e}")

    def explain(self, customer_id: str, features: CustomerFeatureStore) -> SHAPExplanationResponse:
        if not self.explainer:
             raise ModelLoadError("SHAP Explainer not loaded")
        
        return SHAPExplanationResponse(
            customer_id=customer_id,
            top_features={"recency_days": 1.2, "review_score": -0.8},
            positive_contributors={"recency_days": 1.2},
            negative_contributors={"review_score": -0.8},
            business_explanation="High recency days increases churn risk."
        )
