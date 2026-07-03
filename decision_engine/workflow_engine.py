"""
Enterprise AI Customer Intelligence Platform — Workflow Engine.
"""
import uuid
from typing import Optional
from .models import WorkflowModel
from .schemas import WorkflowSchema, RecommendationSchema
from .repository import DecisionRepository
from .audit_service import AuditService
from .exceptions import InvalidTransitionError

class WorkflowEngine:
    """
    Simple persistent state machine managing the lifecycle of a recommendation.
    States: Created -> PendingApproval/Approved -> Executing -> Completed/Failed/Cancelled
    """
    
    VALID_TRANSITIONS = {
        "Created": ["PendingApproval", "Approved", "Cancelled"],
        "PendingApproval": ["Approved", "Cancelled"],
        "Approved": ["Executing", "Cancelled"],
        "Executing": ["Completed", "Failed"],
    }
    
    def __init__(self, repository: DecisionRepository, audit_service: AuditService):
        self.repository = repository
        self.audit_service = audit_service

    async def initialize_workflow(self, recommendation: RecommendationSchema) -> WorkflowSchema:
        """
        Initializes a new workflow for a recommendation.
        """
        initial_status = "PendingApproval" if recommendation.required_approval else "Approved"
        
        model = WorkflowModel(
            recommendation_id=recommendation.recommendation_id,
            status=initial_status
        )
        persisted = await self.repository.create_workflow(model)
        
        await self.audit_service.log_event(
            customer_id=recommendation.customer_unique_id,
            event_type="workflow_initialized",
            details=f"Workflow initialized in state: {initial_status}",
            workflow_id=persisted.workflow_id
        )
        
        return WorkflowSchema.model_validate(persisted)

    async def transition(self, workflow_id: uuid.UUID, new_status: str, customer_id: str, details: str = "") -> WorkflowSchema:
        """
        Transitions the workflow to a new state if valid.
        """
        workflow = await self.repository.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found.")
            
        current_status = workflow.status
        if new_status not in self.VALID_TRANSITIONS.get(current_status, []):
            raise InvalidTransitionError(f"Cannot transition from {current_status} to {new_status}")
            
        updated = await self.repository.update_workflow_status(workflow_id, new_status)
        
        await self.audit_service.log_event(
            customer_id=customer_id,
            event_type=f"transition_{new_status.lower()}",
            details=f"State changed from {current_status} to {new_status}. {details}",
            workflow_id=workflow_id
        )
        
        return WorkflowSchema.model_validate(updated)
