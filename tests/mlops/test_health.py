import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "cache" in data
    # Might be degraded because DB is down in tests
    assert data["status"] in ["ok", "degraded"]
