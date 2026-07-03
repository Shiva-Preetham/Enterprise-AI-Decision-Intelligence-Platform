"""
Enterprise AI Customer Intelligence Platform — Approval Service.
"""
import uuid
from .workflow_engine import WorkflowEngine
from .schemas import WorkflowSchema

class ApprovalService:
    """
    Manages human-in-the-loop approvals.
    """
    def __init__(self, workflow_engine: WorkflowEngine):
        self.workflow_engine = workflow_engine

    async def approve(self, workflow_id: uuid.UUID, approver_id: str, customer_id: str) -> WorkflowSchema:
        """
        Approves a pending workflow.
        """
        details = f"Approved by {approver_id}."
        return await self.workflow_engine.transition(workflow_id, "Approved", customer_id, details)

    async def reject(self, workflow_id: uuid.UUID, approver_id: str, customer_id: str, reason: str) -> WorkflowSchema:
        """
        Rejects (cancels) a pending workflow.
        """
        details = f"Rejected by {approver_id}. Reason: {reason}"
        return await self.workflow_engine.transition(workflow_id, "Cancelled", customer_id, details)
