"""
Enterprise AI Customer Intelligence Platform — Analytics API Tests.

Tests the /api/v1/analytics endpoints with mocked dependencies.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from backend.main import app
from backend.api.dependencies import get_analytics_service


def _mock_analytics_service():
    from backend.schemas.analytics import DashboardMetricsResponse
    svc = MagicMock()
    svc.get_dashboard_metrics = AsyncMock(
        return_value=DashboardMetricsResponse(
            total_customers=1000,
            high_risk_customers=150,
            average_clv=350.0,
            average_review_score=4.1,
            average_order_value=120.0,
            average_churn_probability=0.15,
            latest_feature_store_version="1.0",
            model_version="1.0",
        )
    )
    svc.get_rfm_segment_definitions = MagicMock(return_value={
        "segments": ["Champions", "Loyal Customers", "At Risk", "Lost"],
        "definitions": {},
    })
    return svc


@pytest.fixture
def client():
    app.dependency_overrides[get_analytics_service] = _mock_analytics_service
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


def test_dashboard_returns_200(client):
    response = client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 200


def test_dashboard_response_structure(client):
    response = client.get("/api/v1/analytics/dashboard")
    data = response.json()
    assert data["status"] == "success"
    payload = data["data"]
    assert "total_customers" in payload
    assert "high_risk_customers" in payload
    assert "average_clv" in payload
    assert "average_churn_probability" in payload
    assert "model_version" in payload


def test_rfm_returns_200(client):
    response = client.get("/api/v1/analytics/rfm")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "segments" in data["data"]
