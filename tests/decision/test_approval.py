import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from decision_engine.approval_service import ApprovalService
from decision_engine.workflow_engine import WorkflowEngine
from decision_engine.exceptions import InvalidTransitionError

@pytest.mark.asyncio
async def test_approval_flow():
    we = AsyncMock(spec=WorkflowEngine)
    we.transition.return_value = MagicMock(status="Approved")
    
    svc = ApprovalService(we)
    wf_id = uuid.uuid4()
    
    res = await svc.approve(wf_id, "admin123", "CUST-123")
    assert res.status == "Approved"
    we.transition.assert_called_with(wf_id, "Approved", "CUST-123", "Approved by admin123.")

@pytest.mark.asyncio
async def test_rejection_flow():
    we = AsyncMock(spec=WorkflowEngine)
    we.transition.return_value = MagicMock(status="Cancelled")
    
    svc = ApprovalService(we)
    wf_id = uuid.uuid4()
    
    res = await svc.reject(wf_id, "admin123", "CUST-123", "Too expensive")
    assert res.status == "Cancelled"
    we.transition.assert_called_with(wf_id, "Cancelled", "CUST-123", "Rejected by admin123. Reason: Too expensive")
