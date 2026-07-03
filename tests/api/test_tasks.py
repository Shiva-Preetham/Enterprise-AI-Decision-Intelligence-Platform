"""
Tests for Tasks API Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from backend.main import app

@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

@patch("workers.tasks.training.retrain_model.delay")
def test_trigger_train(mock_delay, client):
    mock_result = MagicMock()
    mock_result.id = "test-task-123"
    mock_delay.return_value = mock_result
    
    response = client.post("/api/v1/tasks/train")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["task_id"] == "test-task-123"
    assert data["data"]["status"] == "QUEUED"

@patch("workers.celery_app.app.AsyncResult")
def test_get_task_status_pending(mock_async_result, client):
    mock_result = MagicMock()
    mock_result.state = "PENDING"
    mock_async_result.return_value = mock_result
    
    response = client.get("/api/v1/tasks/test-task-123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["status"] == "PENDING"

@patch("workers.celery_app.app.AsyncResult")
def test_get_task_status_success(mock_async_result, client):
    mock_result = MagicMock()
    mock_result.state = "SUCCESS"
    mock_result.result = {"duration_seconds": 12.5, "status": "completed"}
    mock_async_result.return_value = mock_result
    
    response = client.get("/api/v1/tasks/test-task-123")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "SUCCESS"
    assert data["data"]["result"]["status"] == "completed"
    assert data["data"]["duration_seconds"] == 12.5
