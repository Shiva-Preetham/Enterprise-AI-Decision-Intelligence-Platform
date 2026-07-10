from fastapi.testclient import TestClient
from backend.main import app
import traceback

try:
    client = TestClient(app)
    response = client.post("/api/v1/agent/chat", json={"question": "hello"})
    print("STATUS:", response.status_code)
    print("BODY:", response.json())
except Exception as e:
    traceback.print_exc()
