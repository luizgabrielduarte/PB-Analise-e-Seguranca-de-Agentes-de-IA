import base64
import json
import time
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from security.jwt import ALGORITHM, SECRET_KEY

PROTECTED_ROUTES = [
    pytest.param("POST", "/predict", {"json": {"text": "Quero cancelar meu pedido"}},
                 id="POST /predict"),
    pytest.param("GET", "/predict/2", {}, id="GET /predict/{id}"),
]


def _b64(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _make_token(*, sub="user", role="user", secret=SECRET_KEY,
                expires_in=timedelta(minutes=5), include_sub=True) -> str:
    claims = {"role": role, "exp": datetime.now(timezone.utc) + expires_in}
    if include_sub:
        claims["sub"] = sub
    return jwt.encode(claims, secret, algorithm=ALGORITHM)


@pytest.mark.parametrize("method, path, kwargs", PROTECTED_ROUTES)
def test_protected_route_without_token_returns_401(client, method, path, kwargs):
    response = client.request(method, path, **kwargs)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_protected_route_checks_auth_before_validating_body(client):
    response = client.post("/predict", json={"campo_invalido": 1})

    assert response.status_code == 401


def test_public_routes_do_not_require_token(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_valid_token_grants_access(client, login):
    response = client.get("/predict/2", headers=login("user"))

    assert response.status_code == 200


def _invalid_tokens():
    now = int(time.time())
    valid_payload = {"sub": "admin", "role": "admin", "exp": now + 300}
    return {
        "garbage": "isto-nao-e-um-jwt",
        "expired": _make_token(expires_in=timedelta(minutes=-1)),
        "signed-with-wrong-key": _make_token(secret="chave-do-atacante"),
        "alg-none": f"{_b64({'alg': 'none', 'typ': 'JWT'})}.{_b64(valid_payload)}.",
        "missing-sub-claim": _make_token(include_sub=False),
        "user-does-not-exist": _make_token(sub="fantasma"),
    }


@pytest.mark.parametrize("name", list(_invalid_tokens()))
def test_protected_route_rejects_invalid_token(client, name):
    token = _invalid_tokens()[name]

    response = client.get("/predict/2", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Token inválido ou expirado"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_protected_route_rejects_token_with_tampered_payload(client, login):
    token = login("user")["Authorization"].removeprefix("Bearer ")
    header, _payload, signature = token.split(".")
    forged_payload = _b64({"sub": "admin", "role": "admin", "exp": int(time.time()) + 300})

    response = client.get(
        "/predict/1",
        headers={"Authorization": f"Bearer {header}.{forged_payload}.{signature}"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Token inválido ou expirado"}


@pytest.mark.parametrize("authorization", ["Basic dXNlcjp1c2VyMTIz", "Bearer", "Token abc"])
def test_protected_route_rejects_wrong_authorization_scheme(client, authorization):
    response = client.get("/predict/2", headers={"Authorization": authorization})

    assert response.status_code == 401
