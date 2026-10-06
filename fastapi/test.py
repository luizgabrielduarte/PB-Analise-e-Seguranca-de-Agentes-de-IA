from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def get_token(username, password):
    response = client.post(
        "/auth/token",
        data={
            "username": username,
            "password": password,
        }
    )

    return response.json()["access_token"]


def test_predict_without_token():
    response = client.post(
        "/predict",
        json={
            "text": "Quero cancelar meu pedido"
        }
    )

    assert response.status_code == 401


def test_access_other_user_prediction():
    token = get_token("user", "user123")

    response = client.get(
        "/predict/1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_predict_rejects_extra_field():
    token = get_token("admin", "admin123")

    response = client.post(
        "/predict",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "text": "Quero cancelar meu pedido",
            "extra_field": "não deveria existir"
        }
    )

    assert response.status_code == 422