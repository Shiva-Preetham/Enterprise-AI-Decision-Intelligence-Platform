"""
Enterprise AI Customer Intelligence Platform — Decision Engine ORM Models.
"""
from datetime import datetime
import uuid
from sqlalchemy import String, Float, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column
from backend.db.base import Base

class RecommendationModel(Base):
    __tablename__ = "recommendations"

    recommendation_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    customer_unique_id: Mapped[str] = mapped_column(String, index=True)
    recommendation_type: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String) # low, medium, high
    confidence: Mapped[float] = mapped_column(Float)
    business_reason: Mapped[str] = mapped_column(Text)
    expected_impact: Mapped[str] = mapped_column(Text)
    estimated_cost: Mapped[float] = mapped_column(Float, nullable=True)
    required_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_by: Mapped[str] = mapped_column(String) # policy_engine, llm_reasoning
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class WorkflowModel(Base):
    __tablename__ = "workflows"

    workflow_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    recommendation_id: Mapped[uuid.UUID] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String) # Created, PendingApproval, Approved, Executing, Completed, Failed, Cancelled
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExecutionModel(Base):
    __tablename__ = "executions"

    execution_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(index=True)
    executor_type: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String) # Success, Failed
    result_payload: Mapped[str] = mapped_column(Text, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class DecisionHistoryModel(Base):
    __tablename__ = "decision_history"

    audit_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=True)
    customer_unique_id: Mapped[str] = mapped_column(String, index=True)
    event_type: Mapped[str] = mapped_column(String) # recommendation_created, policy_evaluated, approval_granted, executed, etc.
    details: Mapped[str] = mapped_column(Text) # JSON serialized
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
