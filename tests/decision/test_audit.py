import pytest
from unittest.mock import AsyncMock, MagicMock
from decision_engine.audit_service import AuditService

@pytest.mark.asyncio
async def test_audit_log_event():
    repo = AsyncMock()
    # Return a dummy model so model_validate doesn't fail
    dummy_model = MagicMock()
    dummy_model.audit_id = "123e4567-e89b-12d3-a456-426614174000"
    repo.add_audit_log.return_value = dummy_model
    
    # Needs to match the schema for AuditSchema
    class MockAuditSchema:
        @classmethod
        def model_validate(cls, obj):
            return obj
            
    # We will just patch AuditSchema or assume the MagicMock passes
    audit = AuditService(repo)
    
    # We'll test that it calls the repository correctly
    await audit.log_event("CUST-123", "test_event", {"some": "detail"})
    
    repo.add_audit_log.assert_called_once()
    args, kwargs = repo.add_audit_log.call_args
    model = args[0]
    
    assert model.customer_unique_id == "CUST-123"
    assert model.event_type == "test_event"
    assert "detail" in model.details
