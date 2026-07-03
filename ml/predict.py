import pandas as pd
from typing import Dict, Any

from ml.config import RISK_BINS, RISK_LABELS
from ml.model_loader import ModelLoader

class Predictor:
    """Prediction pipeline for generating churn risks."""
    
    def __init__(self):
        self.model, self.preprocessor, self.feature_names = ModelLoader.load_artifacts()

    def predict(self, customer_features: pd.DataFrame) -> Dict[str, Any]:
        """Runs the prediction pipeline for a new customer feature vector."""
        # Ensure column order matches training
        # We assume customer_features has the required columns (excluding ID/metadata, handled by preprocessor or beforehand)
        
        # Transform data
        X_transformed = self.preprocessor.transform(customer_features)
        
        # Predict probability of churn (class 1)
        prob = float(self.model.predict_proba(X_transformed)[0, 1])
        label = int(self.model.predict(X_transformed)[0])
        
        # Determine Risk Category
        risk_category = RISK_LABELS[0]
        for i in range(len(RISK_BINS) - 1):
            if RISK_BINS[i] <= prob <= RISK_BINS[i+1]:
                risk_category = RISK_LABELS[i]
                break
                
        return {
            "Probability": prob,
            "PredictedLabel": label,
            "RiskCategory": risk_category
        }
