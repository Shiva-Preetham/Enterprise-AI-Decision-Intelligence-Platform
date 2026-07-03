"""
Enterprise AI Customer Intelligence Platform — Prediction Schemas.

Pydantic V2 DTOs for prediction and explanation endpoints.
All fields include descriptions for OpenAPI documentation.
"""

from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Request body for the POST /predict endpoint."""

    customer_id: str = Field(
        ...,
        description="Unique customer identifier (customer_unique_id from the Feature Store)",
        examples=["d3aba4b6d2dc37ea0b5c8e2fd2a39897"],
    )


class PredictionResponse(BaseModel):
    """Churn prediction result for a single customer."""

    customer_id: str = Field(..., description="Customer unique identifier")
    probability: float = Field(..., ge=0.0, le=1.0, description="Churn probability (0–1)")
    predicted_label: int = Field(..., description="Binary label: 1=churn, 0=retain")
    risk_category: str = Field(
        ...,
        description="Risk category: Low Risk | Medium Risk | High Risk | Very High Risk",
    )


class SHAPExplanationResponse(BaseModel):
    """SHAP feature attribution for a single customer's churn score."""

    customer_id: str = Field(..., description="Customer unique identifier")
    top_features: Dict[str, float] = Field(
        ..., description="Top 10 most impactful features by absolute SHAP value"
    )
    positive_contributors: Dict[str, float] = Field(
        ..., description="Features pushing the churn probability UP"
    )
    negative_contributors: Dict[str, float] = Field(
        ..., description="Features pushing the churn probability DOWN (protective)"
    )
    business_explanation: str = Field(
        ..., description="Human-readable summary of the primary churn drivers"
    )
