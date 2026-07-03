"""
Enterprise AI Customer Intelligence Platform — Audit Service.
"""
from typing import Optional, List
import uuid
import json
from .models import DecisionHistoryModel
from .repository import DecisionRepository
from .schemas import AuditSchema

class AuditService:
    """
    Ensures every state transition and policy decision is appended to the audit log.
    """
    def __init__(self, repository: DecisionRepository):
        self.repository = repository

    async def log_event(
        self, 
        customer_id: str, 
        event_type: str, 
        details: str, 
        workflow_id: Optional[uuid.UUID] = None
    ) -> AuditSchema:
        
        # Ensure details are a string (JSON stringify if dict)
        if isinstance(details, dict):
            details = json.dumps(details, default=str)
            
        model = DecisionHistoryModel(
            customer_unique_id=customer_id,
            event_type=event_type,
            details=details,
            workflow_id=workflow_id
        )
        
        persisted = await self.repository.add_audit_log(model)
        return AuditSchema.model_validate(persisted)

    async def get_workflow_audit_trail(self, workflow_id: uuid.UUID) -> List[AuditSchema]:
        history = await self.repository.get_workflow_audit(workflow_id)
        return [AuditSchema.model_validate(h) for h in history]

    async def get_customer_decision_history(self, customer_id: str) -> List[AuditSchema]:
        history = await self.repository.get_customer_history(customer_id)
        return [AuditSchema.model_validate(h) for h in history]
