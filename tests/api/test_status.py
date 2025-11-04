from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_status():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert response.json() == {
        "successful": True,
        "data": {"status": "ok"},
        "message": "Successfully performed a status check.",
    }


# def test_get_docs_redirect():
#     response = client.get("/api/v1/docs", follow_redirects=False)
#     assert response.status_code == 308
#     assert response.headers["location"] == "/docs"


# def test_get_redoc_redirect():
#     response = client.get("/api/v1/redoc", follow_redirects=False)
#     assert response.status_code == 308
#     assert response.headers["location"] == "/redoc"
