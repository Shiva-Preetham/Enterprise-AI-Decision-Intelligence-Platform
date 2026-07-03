"""
Enterprise AI Customer Intelligence Platform — Customers API Tests.

Tests the /api/v1/customers endpoints with mocked database dependencies.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from backend.main import app
from backend.api.dependencies import get_customer_service
from backend.core.exceptions import ResourceNotFoundError


def _mock_customer_service_404():
    svc = MagicMock()
    svc.get_all_customers = AsyncMock(return_value=[])
    svc.get_customer_profile = AsyncMock(side_effect=ResourceNotFoundError("Customer 'fake' not found"))
    svc.get_customer_timeline = AsyncMock(side_effect=ResourceNotFoundError("Customer 'fake' not found"))
    return svc


@pytest.fixture
def client():
    app.dependency_overrides[get_customer_service] = _mock_customer_service_404
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


def test_list_customers_returns_200(client):
    response = client.get("/api/v1/customers")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "items" in data["data"]


def test_list_customers_supports_pagination_params(client):
    response = client.get("/api/v1/customers?skip=0&limit=10")
    assert response.status_code == 200


def test_list_customers_rejects_invalid_limit(client):
    response = client.get("/api/v1/customers?limit=99999")
    assert response.status_code == 422


def test_customer_profile_not_found_returns_404(client):
    response = client.get("/api/v1/customers/fake/profile")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert "not found" in data["message"].lower()


def test_customer_timeline_not_found_returns_404(client):
    response = client.get("/api/v1/customers/fake/timeline")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
