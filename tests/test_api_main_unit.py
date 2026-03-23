"""Tests for api.main helpers and document routes (mock filesystem where needed)."""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


def test_initialize_database_tables_failure():
    from api.main import initialize_database_tables

    with patch(
        "database.user_informations.init_user_informations_table",
        side_effect=RuntimeError("init failed"),
    ):
        assert initialize_database_tables() is False


def test_initialize_database_tables_success():
    from api.main import initialize_database_tables

    m = MagicMock()
    with patch("database.user_informations.init_user_informations_table", m), patch(
        "upload_file.init_uploaded_files_table", m
    ), patch("analysis.ranking_storage.init_ranking_storage_table", m), patch(
        "resume.resume_manager.ResumeManager.init_resume_table", m
    ), patch("resume.resume_builder_db.init_resume_builder_tables", m), patch(
        "database.user_profile.init_user_profile_table", m
    ), patch(
        "resume.resume_manager.ResumeManager.init_portfolio_customizations_table", m
    ), patch(
        "resume.resume_manager.ResumeManager.init_portfolio_settings_table", m
    ), patch(
        "resume.resume_manager.ResumeManager.init_portfolio_timeline_overrides_table", m
    ), patch(
        "consent.consent_storage.ConsentStorage.initialize_consent_table", m
    ), patch(
        "collaborative.collaborative_storage.CollaborativeStorage.init_table", m
    ), patch(
        "external_services.service_config.ServiceConfig.initialize_table", m
    ):
        assert initialize_database_tables() is True


def test_find_frontend_static_dir_prefers_first_existing(tmp_path, monkeypatch):
    from api import main as main_mod

    monkeypatch.chdir(tmp_path)
    fe = tmp_path / "frontend"
    fe.mkdir()
    (fe / "css").mkdir()
    assert main_mod.find_frontend_static_dir() == "frontend"


def test_find_frontend_file_returns_path(tmp_path, monkeypatch):
    from api import main as main_mod

    monkeypatch.chdir(tmp_path)
    fe = tmp_path / "frontend"
    fe.mkdir()
    idx = fe / "index.html"
    idx.write_text("<html/>", encoding="utf-8")
    found = main_mod.find_frontend_file("index.html")
    assert found and os.path.isfile(found)


def test_find_frontend_file_missing():
    from api import main as main_mod

    with patch("api.main.os.path.exists", return_value=False):
        assert main_mod.find_frontend_file("nope.html") is None


def test_root_json_for_api_clients():
    from api.main import app

    client = TestClient(app)
    r = client.get("/", headers={"accept": "application/json"})
    assert r.status_code == 200
    body = r.json()
    assert body["message"] == "Artifact API is running"
    assert body["version"] == "1.0.0"


def test_root_serves_index_when_html_accepted(tmp_path, monkeypatch):
    from api import main as main_mod
    from api.main import app

    idx = tmp_path / "index.html"
    idx.write_text("<!DOCTYPE html><html></html>", encoding="utf-8")
    with patch.object(main_mod, "find_frontend_file", return_value=str(idx)):
        client = TestClient(app)
        r = client.get("/", headers={"accept": "text/html"})
        assert r.status_code == 200
        assert b"DOCTYPE html" in r.content


def test_static_html_routes_and_favicon():
    from api import main as main_mod
    from api.main import app

    p = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    )
    if not os.path.isfile(p):
        pytest.skip("frontend/index.html not in workspace")
    with patch.object(main_mod, "find_frontend_file", return_value=p):
        c = TestClient(app)
        assert c.get("/index.html").status_code == 200
        assert c.get("/dashboard.html").status_code == 200
        assert c.get("/public-dashboard.html").status_code == 200
        assert c.get("/api-test.html").status_code == 200


def test_static_routes_404_when_missing():
    from api import main as main_mod
    from api.main import app

    with patch.object(main_mod, "find_frontend_file", return_value=None):
        c = TestClient(app)
        assert c.get("/index.html").status_code == 404


def test_favicon_no_content():
    from api.main import app

    r = TestClient(app).get("/favicon.ico")
    assert r.status_code == 204
