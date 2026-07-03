"""
Enterprise AI Customer Intelligence Platform — Prediction Service.

Orchestrates inference requests using globally cached ML artifacts.
Predictions are real — the preprocessor and model are invoked end-to-end.
SHAP explanations are computed from the loaded SHAP explainer.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from structlog import get_logger

from backend.core.exceptions import ModelLoadError
from backend.models import CustomerFeatureStore
from backend.schemas.prediction import PredictionResponse, SHAPExplanationResponse
from ml.config import RISK_BINS, RISK_LABELS

logger = get_logger(__name__)


class PredictionService:
    """Runs inference and SHAP explanation using globally loaded ML artifacts.

    Receives the predictor, preprocessor, and explainer via constructor injection
    from the startup lifespan. This ensures the model is loaded exactly once.

    Args:
        predictor_instance: Trained sklearn-compatible classifier.
        preprocessor_instance: Fitted ColumnTransformer used during training.
        explainer_instance: Fitted SHAP explainer (optional).
        feature_names: Ordered list of feature column names.
    """

    def __init__(
        self,
        predictor_instance,
        preprocessor_instance,
        explainer_instance,
        feature_names,
    ) -> None:
        self.predictor = predictor_instance
        self.preprocessor = preprocessor_instance
        self.explainer = explainer_instance
        self.feature_names = feature_names

    def _get_risk_category(self, probability: float) -> str:
        """Maps a churn probability to a human-readable risk label."""
        for i in range(len(RISK_BINS) - 1):
            if RISK_BINS[i] <= probability < RISK_BINS[i + 1]:
                return RISK_LABELS[i]
        return RISK_LABELS[-1]  # Very High Risk

    def _orm_to_dataframe(self, features: CustomerFeatureStore) -> pd.DataFrame:
        """Converts a CustomerFeatureStore ORM row to a single-row DataFrame.

        Only selects columns that were present during training, in order.
        Missing features default to 0.0 (safe fallback for imputer-trained columns).
        """
        feature_dict = {f: getattr(features, f, 0.0) for f in (self.feature_names or [])}
        return pd.DataFrame([feature_dict])

    def predict(self, customer_id: str, features: CustomerFeatureStore) -> PredictionResponse:
        """Runs end-to-end inference for a single customer.

        Args:
            customer_id: The unique customer identifier (for tracing).
            features: The customer's feature store row.

        Returns:
            PredictionResponse with probability, label, and risk category.

        Raises:
            ModelLoadError: If the model or preprocessor is not loaded.
        """
        if self.predictor is None or self.preprocessor is None:
            raise ModelLoadError(
                "ML model artifacts are not loaded. Run ml/train_pipeline.py first."
            )

        try:
            df = self._orm_to_dataframe(features)
            X_transformed = self.preprocessor.transform(df)
            prob = float(self.predictor.predict_proba(X_transformed)[0, 1])
            label = int(self.predictor.predict(X_transformed)[0])
            risk_category = self._get_risk_category(prob)

            logger.info(
                "prediction_generated",
                customer_id=customer_id,
                probability=round(prob, 4),
                risk_category=risk_category,
            )

            return PredictionResponse(
                customer_id=customer_id,
                probability=round(prob, 4),
                predicted_label=label,
                risk_category=risk_category,
            )
        except Exception as exc:
            logger.error("prediction_failed", customer_id=customer_id, error=str(exc))
            raise ModelLoadError(f"Prediction failed for customer {customer_id}: {exc}") from exc

    def explain(self, customer_id: str, features: CustomerFeatureStore) -> SHAPExplanationResponse:
        """Generates a SHAP explanation for a single customer.

        Args:
            customer_id: The unique customer identifier.
            features: The customer's feature store row.

        Returns:
            SHAPExplanationResponse with positive and negative feature contributors.

        Raises:
            ModelLoadError: If the SHAP explainer is not loaded.
        """
        if self.explainer is None:
            raise ModelLoadError(
                "SHAP explainer is not loaded. Run ml/train_pipeline.py first."
            )

        try:
            df = self._orm_to_dataframe(features)
            X_transformed = self.preprocessor.transform(df)
            X_df = pd.DataFrame(X_transformed, columns=self.feature_names)
            shap_values = self.explainer(X_df)

            # Extract per-feature SHAP values for the single customer
            shap_dict = dict(zip(self.feature_names, shap_values.values[0].tolist()))
            positive = {k: v for k, v in shap_dict.items() if v > 0}
            negative = {k: v for k, v in shap_dict.items() if v < 0}

            # Sort by absolute impact
            top_features = dict(
                sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
            )

            # Generate a human-readable business explanation
            top_positive = max(positive, key=positive.get, default="N/A") if positive else "N/A"
            top_negative = min(negative, key=negative.get, default="N/A") if negative else "N/A"
            explanation = (
                f"The primary churn driver is '{top_positive}' (pushes risk up). "
                f"The strongest protective factor is '{top_negative}' (reduces risk)."
            )

            return SHAPExplanationResponse(
                customer_id=customer_id,
                top_features=top_features,
                positive_contributors=positive,
                negative_contributors=negative,
                business_explanation=explanation,
            )
        except Exception as exc:
            logger.error("shap_explanation_failed", customer_id=customer_id, error=str(exc))
            raise ModelLoadError(f"SHAP explanation failed for customer {customer_id}: {exc}") from exc
