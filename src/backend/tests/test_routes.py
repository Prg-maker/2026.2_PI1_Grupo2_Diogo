from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app

client = TestClient(app)


class FakeResult:
    def __init__(self, row):
        self.row = row

    def mappings(self):
        return self

    def first(self):
        return self.row


class FakeDB:
    def __init__(self, row):
        self.row = row

    def execute(self, _query):
        return FakeResult(self.row)


def active_session():
    return {
        "id": 847,
        "labirinto_id": 4,
        "iniciada_em": "2026-10-20T12:00:00",
        "finalizada_em": None,
        "tempo_total_ms": None,
        "status": "em_execucao",
        "resultado": None,
        "velocidade_media_cm_s": None,
        "criado_em": "2026-10-20T12:00:00",
        "algoritmo": "Flood Fill",
    }


def get_active_session_with_db(row):
    app.dependency_overrides[get_db] = lambda: FakeDB(row)
    try:
        return client.get("/api/sessions/active")
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_active_session_returns_200_and_session():
    response = get_active_session_with_db(active_session())

    assert response.status_code == 200
    data = response.json()
    assert data is not None
    assert data["id"] == "847"
    assert data["algorithm"] == "Flood Fill"
    assert data["status"] == "em_execucao"


def test_active_session_returns_null_when_no_session():
    response = get_active_session_with_db(None)

    assert response.status_code == 200
    assert response.json() is None


def test_active_session_shape_matches_model():
    """O JSON contém os campos públicos do modelo Session."""
    response = get_active_session_with_db(active_session())

    assert set(response.json()) == {
        "id",
        "labirinto_id",
        "iniciada_em",
        "finalizada_em",
        "tempo_total_ms",
        "status",
        "resultado",
        "velocidade_media_cm_s",
        "criado_em",
        "algorithm",
    }
