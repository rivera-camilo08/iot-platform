from fastapi.testclient import TestClient
from iot_platform.app.main import app

client = TestClient(app)


def test_register_user():
    res = client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
    })
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "test@example.com"
    assert "id" in body


def test_login():
    res = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert "refresh_token" in body
