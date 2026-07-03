import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_chat_endpoint_guardrail_rejection():
    # Test that the API correctly rejects bad input before hitting the graph
    response = client.post(
        "/api/v1/agent/chat",
        json={"question": "select * from users;"}
    )
    
    assert response.status_code == 400
    assert "SQL" in response.json()["detail"]
    
def test_chat_endpoint_missing_question():
    response = client.post(
        "/api/v1/agent/chat",
        json={}
    )
    assert response.status_code == 422 # Validation Error
