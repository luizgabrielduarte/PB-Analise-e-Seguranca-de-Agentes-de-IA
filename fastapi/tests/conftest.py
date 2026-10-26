import sys
from pathlib import Path

# Permite `from main import app`, `from security.jwt import ...` etc.
# independentemente do diretório de onde o pytest é executado.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from database import get_session  # noqa: E402
from main import app  # noqa: E402
from models.database import Prediction, User  # noqa: E402
from security.rate_limit import limiter  # noqa: E402

PASSWORDS = {
    "admin": "admin123",
    "user": "user123",
    "maria": "maria123",
}

ADMIN_ID, USER_ID, MARIA_ID = 1, 2, 3


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture()
def engine(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all([
            User(id=ADMIN_ID, username="admin", password=PASSWORDS["admin"], role="admin"),
            User(id=USER_ID, username="user", password=PASSWORDS["user"], role="user"),
            User(id=MARIA_ID, username="maria", password=PASSWORDS["maria"], role="user"),
        ])
        session.add_all([
            Prediction(id=1, text="Quero cancelar meu pedido",
                       intent="cancellation_request", owner_id=ADMIN_ID),
            Prediction(id=2, text="Preciso de ajuda com meu produto",
                       intent="technical_issue", owner_id=USER_ID),
            Prediction(id=3, text="Quero o reembolso da minha compra",
                       intent="refund_request", owner_id=MARIA_ID),
        ])
        session.commit()

    yield engine
    engine.dispose()


@pytest.fixture()
def session_factory(engine):
    return lambda: Session(engine)


@pytest.fixture()
def client(engine):
    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def login(client):
    def _login(username: str) -> dict:
        response = client.post(
            "/auth/token",
            data={"username": username, "password": PASSWORDS[username]},
        )
        assert response.status_code == 200, response.text
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _login
