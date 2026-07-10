"""
MLOps SQLAlchemy Models.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from datetime import datetime
from backend.db.base import Base

class ModelRegistryModel(Base):
    __tablename__ = "model_registry"
    
    model_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(Integer, nullable=False, unique=True)
    training_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    dataset_version = Column(String, nullable=False)
    feature_version = Column(String, nullable=False)
    pipeline_version = Column(String, nullable=False)
    hyperparameters = Column(Text, nullable=False) # Stored as JSON string
    metrics = Column(Text, nullable=False) # Stored as JSON string
    shap_summary = Column(Text, nullable=False) # Stored as JSON string
    deployment_status = Column(String, nullable=False, default="staging") # production, staging, archived
    filename = Column(String, nullable=False)

class ExperimentModel(Base):
    __tablename__ = "experiments"
    
    experiment_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    duration_seconds = Column(Float, nullable=False)
    params = Column(Text, nullable=False)
    metrics = Column(Text, nullable=False)
    dataset_ref = Column(String, nullable=False)
    feature_count = Column(Integer, nullable=False)
    algorithm = Column(String, nullable=False)
    cv_scores = Column(Text, nullable=False)

class DriftReportModel(Base):
    __tablename__ = "drift_reports"
    
    report_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    reference_window_start = Column(DateTime(timezone=True), nullable=False)
    reference_window_end = Column(DateTime(timezone=True), nullable=False)
    current_window_start = Column(DateTime(timezone=True), nullable=False)
    current_window_end = Column(DateTime(timezone=True), nullable=False)
    feature_stats = Column(Text, nullable=False) # Stored as JSON string
    is_alert = Column(Boolean, nullable=False, default=False)

class AlertModel(Base):
    __tablename__ = "alerts"
    
    alert_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    alert_type = Column(String, nullable=False) # drift, quality, error_rate
    severity = Column(String, nullable=False) # warning, critical
    details = Column(Text, nullable=False) # JSON string
    status = Column(String, nullable=False, default="new") # new, resolved
