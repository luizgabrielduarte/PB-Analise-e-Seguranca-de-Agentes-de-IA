import pytest
from sqlmodel import select

from conftest import ADMIN_ID, MARIA_ID, USER_ID
from models.database import Prediction

ACCESS_MATRIX = [
    pytest.param("user", 2, 200, id="user->own"),
    pytest.param("user", 1, 403, id="user->admin's"),
    pytest.param("user", 3, 403, id="user->maria's"),
    pytest.param("maria", 3, 200, id="maria->own"),
    pytest.param("maria", 2, 403, id="maria->user's"),
    pytest.param("maria", 1, 403, id="maria->admin's"),
    pytest.param("admin", 1, 200, id="admin->own"),
]


@pytest.mark.parametrize("username, prediction_id, expected_status", ACCESS_MATRIX)
def test_prediction_access_matrix(client, login, username, prediction_id, expected_status):
    response = client.get(f"/predict/{prediction_id}", headers=login(username))

    assert response.status_code == expected_status


def test_owner_receives_full_prediction(client, login):
    response = client.get("/predict/2", headers=login("user"))

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "text": "Preciso de ajuda com meu produto",
        "intent": "technical_issue",
        "owner_id": USER_ID,
    }


def test_forbidden_response_does_not_leak_the_resource(client, login):
    response = client.get("/predict/1", headers=login("user"))

    assert response.status_code == 403
    assert response.json() == {"detail": "Acesso negado"}
    # Nada do conteúdo do admin pode aparecer na resposta.
    assert "Quero cancelar meu pedido" not in response.text
    assert "cancellation_request" not in response.text


def test_user_cannot_read_prediction_created_by_another_user(client, login, session_factory):
    created = client.post(
        "/predict", headers=login("maria"), json={"text": "Preciso de reembolso urgente"}
    )
    assert created.status_code == 200

    with session_factory() as session:
        prediction = session.exec(
            select(Prediction).where(Prediction.text == "Preciso de reembolso urgente")
        ).one()
    assert prediction.owner_id == MARIA_ID

    stolen = client.get(f"/predict/{prediction.id}", headers=login("user"))
    assert stolen.status_code == 403
    assert "reembolso urgente" not in stolen.text

    owner = client.get(f"/predict/{prediction.id}", headers=login("maria"))
    assert owner.status_code == 200
    assert owner.json()["owner_id"] == MARIA_ID


def test_predictions_are_always_owned_by_the_token_user(client, login, session_factory):
    client.post("/predict", headers=login("user"), json={"text": "Dúvida sobre fatura"})

    with session_factory() as session:
        prediction = session.exec(
            select(Prediction).where(Prediction.text == "Dúvida sobre fatura")
        ).one()
    assert prediction.owner_id == USER_ID
    assert prediction.owner_id != ADMIN_ID


def test_enumerating_ids_only_exposes_own_predictions(client, login):
    headers = login("user")

    statuses = {i: client.get(f"/predict/{i}", headers=headers).status_code for i in (1, 2, 3)}

    assert statuses == {1: 403, 2: 200, 3: 403}


def test_nonexistent_prediction_returns_404(client, login):
    response = client.get("/predict/9999", headers=login("user"))

    assert response.status_code == 404
    assert response.json() == {"detail": "Prediction não encontrada"}
