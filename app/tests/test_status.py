from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)


def test_get_status():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert response.json() == {
        "successful": True,
        "data": {"status": "ok"},
        "message": "Successfully performed a status check.",
    }
