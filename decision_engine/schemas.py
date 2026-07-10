"""
Enterprise AI Customer Intelligence Platform — Decision Engine Schemas.
"""
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class PolicyDecision(BaseModel):
    decision: Literal["ALLOW", "DENY", "REQUIRE_APPROVAL"]
    allowed_actions: List[str]
    reason: str
    evaluated_policies: List[str]

class ReasoningOutput(BaseModel):
    selected_action: str
    confidence: float
    business_justification: str
    expected_impact: str
    estimated_cost: Optional[float] = None

class RecommendationSchema(BaseModel):
    recommendation_id: UUID
    customer_unique_id: str
    recommendation_type: str
    priority: Literal["low", "medium", "high"]
    confidence: float
    business_reason: str
    expected_impact: str
    estimated_cost: Optional[float] = None
    required_approval: bool
    generated_by: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class WorkflowSchema(BaseModel):
    workflow_id: UUID
    recommendation_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AuditSchema(BaseModel):
    audit_id: UUID
    workflow_id: Optional[UUID]
    customer_unique_id: str
    event_type: str
    details: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
        
class ApprovalRequest(BaseModel):
    approver_id: str
    
class RejectionRequest(BaseModel):
    approver_id: str
    reason: str
