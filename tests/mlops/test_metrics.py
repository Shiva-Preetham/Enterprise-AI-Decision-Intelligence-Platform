import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "model_inference_duration_seconds" in response.text
