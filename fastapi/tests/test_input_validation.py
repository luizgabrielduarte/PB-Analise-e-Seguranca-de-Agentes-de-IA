import pytest
from sqlmodel import func, select

from models.database import Prediction, User


def _post(client, headers, body):
    return client.post("/predict", headers=headers, json=body)


def _count(session_factory, model):
    with session_factory() as session:
        return session.exec(select(func.count()).select_from(model)).one()


def test_predict_accepts_valid_payload(client, login):
    response = _post(client, login("user"), {"text": "Quero cancelar meu pedido"})

    assert response.status_code == 200
    assert response.json() == {
        "text": "Quero cancelar meu pedido",
        "intent": "cancellation_request",
    }


def test_predict_rejects_extra_field(client, login):
    response = _post(
        client, login("user"),
        {"text": "Quero cancelar meu pedido", "extra_field": "não deveria existir"},
    )

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == "extra_forbidden"
    assert error["loc"] == ["body", "extra_field"]


@pytest.mark.parametrize(
    "extra", [{"owner_id": 1}, {"intent": "refund_request"}, {"id": 999}, {"role": "admin"}]
)
def test_predict_rejects_mass_assignment_and_creates_nothing(
    client, login, session_factory, extra
):
    before = _count(session_factory, Prediction)

    response = _post(client, login("user"), {"text": "Preciso de ajuda", **extra})

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "extra_forbidden"
    assert _count(session_factory, Prediction) == before


@pytest.mark.parametrize(
    "body, error_type",
    [
        ({}, "missing"),
        ({"text": ""}, "string_too_short"),
        ({"text": "a" * 5001}, "string_too_long"),
    ],
    ids=["missing-text", "empty-text", "text-over-5000-chars"],
)
def test_predict_rejects_invalid_text(client, login, body, error_type):
    response = _post(client, login("user"), body)

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == error_type
    assert error["loc"] == ["body", "text"]


def test_predict_accepts_text_at_max_length(client, login):
    response = _post(client, login("user"), {"text": "a" * 5000})

    assert response.status_code == 200
    assert len(response.json()["text"]) == 5000


@pytest.mark.parametrize("value", [123, None, True, ["a"], {"a": 1}],
                         ids=["int", "null", "bool", "list", "object"])
def test_predict_rejects_wrong_type_for_text(client, login, value):
    response = _post(client, login("user"), {"text": value})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "text"]


def test_predict_rejects_malformed_json(client, login):
    response = client.post(
        "/predict",
        headers={**login("user"), "Content-Type": "application/json"},
        content='{"text": "sem fechar',
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "json_invalid"


def test_predict_rejects_non_json_body(client, login):
    response = client.post(
        "/predict", headers=login("user"), data={"text": "enviado como formulário"}
    )

    assert response.status_code == 422


@pytest.mark.parametrize("prediction_id", ["abc", "1.5", "1%20OR%201=1", "1;DROP%20TABLE%20users"])
def test_prediction_id_must_be_an_integer(client, login, prediction_id):
    response = client.get(f"/predict/{prediction_id}", headers=login("user"))

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "prediction_id"]


def test_sql_injection_in_text_is_stored_as_plain_data(client, login, session_factory):
    payload = "'); DROP TABLE users; --"
    users_before = _count(session_factory, User)

    response = _post(client, login("user"), {"text": payload})

    assert response.status_code == 200
    assert response.json()["text"] == payload
    assert _count(session_factory, User) == users_before
    assert client.post(
        "/auth/token", data={"username": "user", "password": "user123"}
    ).status_code == 200
