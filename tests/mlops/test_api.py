import pytest
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch

client = TestClient(app)

def test_mlops_api_security():
    # Calling mlops without JWT or API key should return 401
    response = client.get("/api/v1/mlops/models")
    assert response.status_code == 401

def test_mlops_api_with_auth():
    # Pass a simulated token
    headers = {"Authorization": "Bearer test-token"}
    response = client.get("/api/v1/mlops/models", headers=headers)
    # Could be 200 or 500 if DB is down, but shouldn't be 401
    assert response.status_code != 401
