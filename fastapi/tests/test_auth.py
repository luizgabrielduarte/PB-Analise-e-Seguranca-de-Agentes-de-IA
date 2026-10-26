import time

import pytest
from jose import jwt

from conftest import PASSWORDS
from security.jwt import ALGORITHM, SECRET_KEY


def test_login_with_valid_credentials_returns_bearer_token(client):
    response = client.post(
        "/auth/token",
        data={"username": "user", "password": PASSWORDS["user"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]

    # O JWT emitido identifica o usuário certo e tem expiração futura.
    claims = jwt.decode(body["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert claims["sub"] == "user"
    assert claims["role"] == "user"
    assert claims["exp"] > time.time()


def test_login_with_wrong_password_is_rejected(client):
    response = client.post(
        "/auth/token",
        data={"username": "user", "password": "senha-errada"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Usuário ou senha incorretos"}
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert "access_token" not in response.text


def test_login_does_not_reveal_whether_user_exists(client):
    wrong_password = client.post(
        "/auth/token", data={"username": "user", "password": "senha-errada"}
    )
    unknown_user = client.post(
        "/auth/token", data={"username": "ninguem", "password": "senha-errada"}
    )

    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json()


@pytest.mark.parametrize(
    "username",
    ["admin' OR '1'='1", "admin' --", "' OR 1=1 --", "admin\" OR \"\"=\""],
)
def test_login_rejects_sql_injection_in_username(client, username):
    response = client.post(
        "/auth/token", data={"username": username, "password": "qualquer"}
    )

    assert response.status_code == 401
    assert "access_token" not in response.text


def test_login_rejects_sql_injection_in_password(client):
    response = client.post(
        "/auth/token", data={"username": "admin", "password": "' OR '1'='1"}
    )

    assert response.status_code == 401
    assert "access_token" not in response.text


@pytest.mark.parametrize(
    "form",
    [
        {"username": "user"},                 # sem senha
        {"password": PASSWORDS["user"]},      # sem usuário
        {},                                   # vazio
    ],
    ids=["missing-password", "missing-username", "empty-form"],
)
def test_login_with_incomplete_form_returns_422(client, form):
    response = client.post("/auth/token", data=form)

    assert response.status_code == 422
    assert "access_token" not in response.text


def test_login_does_not_accept_json_body(client):
    response = client.post(
        "/auth/token",
        json={"username": "user", "password": PASSWORDS["user"]},
    )

    assert response.status_code == 422
