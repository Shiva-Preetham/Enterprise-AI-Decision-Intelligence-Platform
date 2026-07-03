"""
Enterprise AI Customer Intelligence Platform — Prediction API Tests.

Tests the /api/v1/predict endpoints using FastAPI TestClient with mocked
ML services so no database or trained model is required.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from backend.main import app
from backend.api.dependencies import get_prediction_service, get_customer_repository


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


def test_predict_missing_customer_id_returns_422(client):
    """Pydantic validation should reject empty request body."""
    response = client.post("/api/v1/predict", json={})
    assert response.status_code == 422


def test_predict_invalid_content_type_returns_422(client):
    """Non-JSON body should fail schema validation."""
    response = client.post(
        "/api/v1/predict",
        content="not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_predict_returns_error_response_structure(client):
    """Error responses must follow the standard error envelope."""

    def _mock_repo():
        repo = MagicMock()
        repo.get_customer_features = MagicMock(return_value=None)
        return repo

    app.dependency_overrides[get_customer_repository] = _mock_repo

    response = client.post("/api/v1/predict", json={"customer_id": "fake_id_123"})
    # Customer not found → 404 or DB error → 500
    assert response.status_code in [404, 500]
    data = response.json()
    assert data["status"] == "error"
    assert "message" in data
    app.dependency_overrides.clear()
