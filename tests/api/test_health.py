"""
Enterprise AI Customer Intelligence Platform — API Health Tests.

Tests the /api/v1/health endpoint using FastAPI TestClient with mocked
dependencies so the tests run without a live database or ML artifacts.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from backend.main import app
from backend.api.dependencies import get_model_service


def _mock_model_service():
    svc = MagicMock()
    svc.get_model_info.return_value = {"PipelineVersion": "1.0", "FeatureVersion": "1.0"}
    return svc


@pytest.fixture
def client():
    app.dependency_overrides[get_model_service] = _mock_model_service
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


def test_health_check_returns_200(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_check_response_structure(client):
    response = client.get("/api/v1/health")
    data = response.json()
    assert data["status"] == "success"
    assert "api_status" in data["data"]
    assert "ml_model_loaded" in data["data"]
    assert "uptime_seconds" in data["data"]
    assert "application_version" in data["data"]


def test_health_check_api_status_ok(client):
    response = client.get("/api/v1/health")
    assert response.json()["data"]["api_status"] == "ok"
