from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_healthcheck_ok() -> None:
    response = client.get("/api/v1/healthcheck")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "backend"
    assert "version" in body
