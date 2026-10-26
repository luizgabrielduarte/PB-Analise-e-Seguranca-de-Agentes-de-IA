from conftest import PASSWORDS

LIMIT = 10


def _login(client, password, **kwargs):
    return client.post(
        "/auth/token", data={"username": "user", "password": password}, **kwargs
    )


def test_login_is_blocked_after_the_limit_is_exceeded(client):
    ok = PASSWORDS["user"]

    for attempt in range(1, LIMIT + 1):
        response = _login(client, ok)
        assert response.status_code == 200, f"tentativa {attempt} deveria passar"

    blocked = _login(client, ok)
    assert blocked.status_code == 429
    assert blocked.headers["content-type"].startswith("application/json")
    detail = blocked.json()["detail"]
    assert "10" in detail and "minute" in detail
    assert "access_token" not in blocked.text


def test_brute_force_is_blocked_even_when_the_correct_password_arrives(client):
    for attempt in range(1, LIMIT + 1):
        response = _login(client, f"palpite-{attempt}")
        assert response.status_code == 401

    assert _login(client, "palpite-11").status_code == 429
    assert _login(client, PASSWORDS["user"]).status_code == 429


def test_rate_limit_cannot_be_bypassed_by_spoofing_x_forwarded_for(client):
    for _ in range(LIMIT):
        _login(client, "errada")

    response = _login(client, PASSWORDS["user"], headers={"X-Forwarded-For": "203.0.113.77"})

    assert response.status_code == 429


def test_rate_limit_only_applies_to_the_login_route(client):
    for _ in range(LIMIT + 1):
        _login(client, "errada")
    assert _login(client, "errada").status_code == 429

    assert client.get("/health").status_code == 200
