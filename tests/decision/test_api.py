import pytest
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch, MagicMock, AsyncMock

client = TestClient(app)

@patch("backend.api.v1.decisions.ReasoningEngine")
@patch("backend.api.v1.decisions.CustomerService")
@patch("backend.api.v1.decisions.DecisionRepository")
def test_recommend_endpoint_success(MockRepo, MockCustomerSvc, MockReasoning):
    # Setup mocks
    mock_repo = MockRepo.return_value
    mock_repo.get_customer_history = AsyncMock(return_value=[])
    
    # Needs a recommendation model for create_recommendation
    mock_rec = MagicMock()
    mock_rec.recommendation_id = "123e4567-e89b-12d3-a456-426614174000"
    mock_repo.create_recommendation = AsyncMock(return_value=mock_rec)
    
    mock_wf = MagicMock()
    mock_wf.workflow_id = "123e4567-e89b-12d3-a456-426614174000"
    mock_repo.create_workflow = AsyncMock(return_value=mock_wf)
    mock_repo.add_audit_log = AsyncMock()

    # The DI system in FastAPI might be tricky to mock via patch if Depends is used.
    # We can use app.dependency_overrides to safely mock.
    from backend.api.v1.decisions import get_repository, get_customer_service
    
    app.dependency_overrides[get_repository] = lambda: mock_repo
    
    mock_cust_svc = MagicMock()
    profile = MagicMock()
    profile.prediction = {"probability": 0.2} # Low risk
    profile.features = MagicMock()
    profile.features.model_dump.return_value = {"total_lifetime_value": 500}
    mock_cust_svc.get_customer_profile = AsyncMock(return_value=profile)
    
    app.dependency_overrides[get_customer_service] = lambda: mock_cust_svc
    
    # Mock Reasoning Engine
    mock_reasoning_inst = MockReasoning.return_value
    mock_reasoning_inst.generate_reasoning = AsyncMock(return_value=MagicMock(
        selected_action="no_action",
        confidence=0.9,
        business_justification="Low risk",
        expected_impact="None",
        estimated_cost=0
    ))
    
    response = client.post("/api/v1/decisions/recommend?customer_id=CUST-123")
    assert response.status_code == 200
    
    data = response.json()
    assert data["recommendation_type"] == "no_action"
    assert data["required_approval"] is False
    
    app.dependency_overrides.clear()
