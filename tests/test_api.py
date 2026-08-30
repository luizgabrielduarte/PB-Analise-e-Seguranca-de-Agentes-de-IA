from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_requires_auth():
    response = client.post("/predict", json={"text": "quero cancelar"})
    assert response.status_code == 401


def test_token_and_predict():
    token_response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]

    response = client.post(
        "/predict",
        json={"text": "Quero cancelar minha compra"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["intent"] == "cancellation_request"
