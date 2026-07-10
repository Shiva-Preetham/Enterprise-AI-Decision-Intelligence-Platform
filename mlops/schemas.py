"""
MLOps Pydantic Schemas.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class ModelRegistrySchema(BaseModel):
    model_id: uuid.UUID
    version: int
    training_timestamp: datetime
    dataset_version: str
    feature_version: str
    pipeline_version: str
    hyperparameters: str
    metrics: str
    shap_summary: str
    deployment_status: str
    filename: str

    model_config = ConfigDict(from_attributes=True)

class ExperimentSchema(BaseModel):
    experiment_id: uuid.UUID
    run_id: str
    timestamp: datetime
    duration_seconds: float
    params: str
    metrics: str
    dataset_ref: str
    feature_count: int
    algorithm: str
    cv_scores: str

    model_config = ConfigDict(from_attributes=True)

class DriftReportSchema(BaseModel):
    report_id: uuid.UUID
    timestamp: datetime
    reference_window_start: datetime
    reference_window_end: datetime
    current_window_start: datetime
    current_window_end: datetime
    feature_stats: str
    is_alert: bool

    model_config = ConfigDict(from_attributes=True)

class AlertSchema(BaseModel):
    alert_id: uuid.UUID
    timestamp: datetime
    alert_type: str
    severity: str
    details: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class DataQualityReport(BaseModel):
    timestamp: datetime
    total_rows: int
    missing_value_rates: Dict[str, float]
    duplicate_rows: int
    out_of_range_features: List[str]
    schema_mismatches: List[str]
    overall_status: str
