import os
import sys

from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from api.main import app

client = TestClient(app)


def test_db_connection_handles_connection_error(monkeypatch):
    from api.routes import health

    def mock_fail(*args, **kwargs):
        raise Exception("DB down")

    monkeypatch.setattr(health, "check_db_connection", mock_fail, raising=False)

    response = client.get("/api/health/db")

    assert response.status_code == 503