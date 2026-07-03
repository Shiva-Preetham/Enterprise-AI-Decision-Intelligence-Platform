import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from decision_engine.workflow_engine import WorkflowEngine
from decision_engine.exceptions import InvalidTransitionError
from decision_engine.models import WorkflowModel

@pytest.mark.asyncio
async def test_workflow_initialization_requires_approval():
    repo = AsyncMock()
    audit = AsyncMock()
    we = WorkflowEngine(repo, audit)
    
    rec = MagicMock()
    rec.required_approval = True
    rec.recommendation_id = uuid.uuid4()
    
    persisted = WorkflowModel(workflow_id=uuid.uuid4(), recommendation_id=rec.recommendation_id, status="PendingApproval")
    repo.create_workflow.return_value = persisted
    
    wf = await we.initialize_workflow(rec)
    assert wf.status == "PendingApproval"
    audit.log_event.assert_called_once()

@pytest.mark.asyncio
async def test_invalid_transition():
    repo = AsyncMock()
    audit = AsyncMock()
    we = WorkflowEngine(repo, audit)
    
    wf_id = uuid.uuid4()
    mock_wf = MagicMock()
    mock_wf.status = "Created"
    repo.get_workflow.return_value = mock_wf
    
    with pytest.raises(InvalidTransitionError):
        # Cannot transition from Created to Completed directly
        await we.transition(wf_id, "Completed", "CUST-123")
