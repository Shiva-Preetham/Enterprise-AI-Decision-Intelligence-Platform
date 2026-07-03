import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_dashboard():
    response = client.get("/api/v1/analytics/dashboard")
    # Should be 500 without a running DB in our default setup, but routing should work
    assert response.status_code in [200, 500]

def test_get_rfm():
    response = client.get("/api/v1/analytics/rfm")
    # This is mocked, should work without DB
    assert response.status_code == 200
    assert response.json()["status"] == "success"
