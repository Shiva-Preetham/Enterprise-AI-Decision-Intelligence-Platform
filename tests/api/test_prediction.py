import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_predict_validation_error():
    response = client.post("/api/v1/predict", json={})
    assert response.status_code == 422

def test_predict_customer_not_found():
    response = client.post("/api/v1/predict", json={"customer_id": "fake"})
    assert response.status_code in [404, 500]
