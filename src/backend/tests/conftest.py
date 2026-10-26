from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from app.core.database import get_db
from app.main import app

@pytest.fixture
def unit_client():
    db = MagicMock()
    previus_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = lambda: db
    try:
        with TestClient(app) as client:
            yield client, db
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previus_overrides)