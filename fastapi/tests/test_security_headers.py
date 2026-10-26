import pytest


@pytest.mark.parametrize("path, expected_status", [("/health", 200), ("/predict/1", 401)])
def test_security_headers_are_present_on_every_response(client, path, expected_status):
    response = client.get(path)

    assert response.status_code == expected_status
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "max-age=" in response.headers["Strict-Transport-Security"]
    csp = response.headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in csp
    assert "object-src 'none'" in csp


def test_cors_does_not_allow_arbitrary_origins(client):
    response = client.options(
        "/predict",
        headers={
            "Origin": "https://site-malicioso.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert "access-control-allow-origin" not in response.headers
