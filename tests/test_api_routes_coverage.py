"""Route-level tests with mocks to raise coverage on api.routes.* modules."""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from api.main import app
from api.dependencies import get_authenticated_user


@pytest.fixture
def client():
    return TestClient(app)


# --- public.py ---
@patch("api.routes.public.get_all_users")
def test_api_users_list_success(mock_get, client):
    mock_get.return_value = [
        {
            "user_id": 1,
            "user_name": "a",
            "create_time": datetime(2024, 1, 2, tzinfo=timezone.utc),
            "last_login_time": None,
            "is_login": True,
        }
    ]
    r = client.get("/api/users")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["count"] == 1
    assert data["users"][0]["user_name"] == "a"
    assert "T" in data["users"][0]["create_time"]


@patch("api.routes.public.get_all_users", side_effect=RuntimeError("db"))
def test_api_users_list_error(mock_get, client):
    r = client.get("/api/users")
    assert r.status_code == 500


# --- health.py ---
@patch("api.routes.health.check_db_connection", return_value=True)
def test_health_db_connected(mock_chk, client):
    r = client.get("/api/health/db")
    assert r.status_code == 200
    assert r.json()["database"] == "connected"


@patch("api.routes.health.check_db_connection", return_value=False)
def test_health_db_unavailable(mock_chk, client):
    r = client.get("/api/health/db")
    assert r.status_code == 503
    # Normalized by api.exception_handlers.http_exception_handler
    assert r.json()["details"]["error_type"] == "DB_UNAVAILABLE"


@patch("api.routes.health.check_db_connection", side_effect=RuntimeError("x"))
def test_health_db_exception_branch(mock_chk, client):
    r = client.get("/api/health/db")
    assert r.status_code == 503
    assert r.json()["details"]["error_type"] == "DB_HEALTH_CHECK_FAILED"


# --- consent.py ---
@patch("api.routes.consent.ConsentStorage.store_consent", return_value=True)
@patch("api.routes.consent.ConsentStorage.get_consent_status", return_value={"ok": True})
def test_privacy_consent_with_username(mock_gs, mock_ss, client):
    r = client.post("/api/privacy-consent", json={"consent_given": True, "user_name": "u1"})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["user_name"] == "u1"


@patch("account.user_manager.AuthManager.get_current_username", return_value=None)
@patch("api.routes.consent.ConsentStorage.store_consent", return_value=True)
def test_privacy_consent_missing_user(mock_ss, mock_user, client):
    r = client.post("/api/privacy-consent", json={"consent_given": True})
    assert r.status_code == 400


@patch("api.routes.consent.ConsentStorage.store_consent", return_value=False)
@patch("api.routes.consent.ConsentStorage.get_consent_status", return_value={})
def test_privacy_consent_store_failed(mock_gs, mock_ss, client):
    r = client.post("/api/privacy-consent", json={"consent_given": False, "user_name": "u"})
    assert r.status_code == 500


@patch("api.routes.consent.ConsentStorage.store_consent", return_value=True)
@patch("api.routes.consent.ConsentStorage.get_consent_status", side_effect=RuntimeError("x"))
def test_privacy_consent_unexpected_error(mock_gs, mock_ss, client):
    r = client.post("/api/privacy-consent", json={"consent_given": True, "user_name": "u"})
    assert r.status_code == 500


# --- auth.py ---
@patch("api.routes.auth.login_user", return_value=False)
def test_auth_login_invalid(mock_login, client):
    r = client.post("/api/auth/login", json={"username": "u", "password": "pw"})
    assert r.status_code == 401


def test_auth_login_validation_empty_user(client):
    # LoginRequest enforces min_length=1 — rejected by Pydantic before the route runs
    r = client.post("/api/auth/login", json={"username": "", "password": "x"})
    assert r.status_code == 422


def test_auth_login_validation_empty_password(client):
    r = client.post("/api/auth/login", json={"username": "u", "password": ""})
    assert r.status_code == 422


@patch("api.routes.auth.login_user", return_value=True)
@patch("api.routes.auth.get_user_by_username", return_value=None)
def test_auth_login_user_missing_after_ok(mock_gu, mock_login, client):
    r = client.post("/api/auth/login", json={"username": "u", "password": "pw"})
    assert r.status_code == 500


@patch("api.routes.auth.AuthManager.register", return_value={"success": False, "message": "taken"})
def test_auth_register_failure(mock_reg, client):
    r = client.post("/api/auth/register", json={"username": "u", "password": "secret1"})
    assert r.status_code == 200
    assert r.json()["success"] is False


def test_auth_register_short_password(client):
    # RegisterRequest requires min_length=6 — schema validation returns 422 before AuthManager.register
    r = client.post("/api/auth/register", json={"username": "u", "password": "12345"})
    assert r.status_code == 422


def test_auth_logout_validation(client):
    # LogoutRequest enforces min_length=1 on username
    r = client.post("/api/auth/logout", json={"username": ""})
    assert r.status_code == 422


@patch("api.routes.auth.get_user_by_username", return_value=None)
def test_auth_logout_user_not_found(mock_gu, client):
    r = client.post("/api/auth/logout", json={"username": "ghost"})
    assert r.status_code == 404


@patch(
    "api.routes.auth.get_user_by_username",
    return_value={"user_id": 1, "user_name": "u", "is_login": False},
)
def test_auth_logout_not_logged_in(mock_gu, client):
    r = client.post("/api/auth/logout", json={"username": "u"})
    assert r.status_code == 409


@patch(
    "api.routes.auth.get_user_by_username",
    return_value={"user_id": 1, "user_name": "u", "is_login": True},
)
@patch("api.routes.auth.logout_user", return_value=False)
def test_auth_logout_failed(mock_lo, mock_gu, client):
    r = client.post("/api/auth/logout", json={"username": "u"})
    assert r.status_code == 500


def test_auth_me_validation(client):
    r = client.get("/api/auth/me", params={"username": "  "})
    assert r.status_code == 400


@patch("api.routes.auth.get_user_by_username", return_value=None)
def test_auth_me_not_found(mock_gu, client):
    r = client.get("/api/auth/me", params={"username": "nope"})
    assert r.status_code == 404


@patch(
    "api.routes.auth.get_user_by_username",
    return_value={"user_id": 1, "user_name": "u", "is_login": False},
)
def test_auth_me_not_logged_in(mock_gu, client):
    r = client.get("/api/auth/me", params={"username": "u"})
    assert r.status_code == 401


# --- resume_builder (prefix /api/resume-builder) ---
@patch("api.routes.resume_builder.build_resume_model", return_value={"resume": True})
def test_resume_builder_get_preview(mock_bm, client):
    r = client.get("/api/resume-builder/resume", params={"user_name": "alice"})
    assert r.status_code == 200
    assert r.json()["resume"] is True


@patch("api.routes.resume_builder.build_resume_model", side_effect=RuntimeError("e"))
def test_resume_builder_get_500(mock_bm, client):
    r = client.get("/api/resume-builder/resume", params={"user_name": "alice"})
    assert r.status_code == 500


@patch("api.routes.resume_builder.load_saved_resume", return_value={"id": 2})
def test_resume_builder_get_saved(mock_lr, client):
    r = client.get("/api/resume-builder/resume/3", params={"user_name": "alice"})
    assert r.status_code == 200


@patch("api.routes.resume_builder.list_resumes", return_value=[])
def test_resume_builder_list_names(mock_lr, client):
    r = client.get("/api/resume-builder/resume_names", params={"user_name": "alice"})
    assert r.status_code == 200
    assert r.json()["resumes"] == []


@patch("api.routes.resume_builder.create_resume", return_value=9)
@patch("api.routes.resume_builder.attach_projects_to_resume")
def test_resume_builder_create(mock_att, mock_cr, client):
    r = client.post(
        "/api/resume-builder/resume?user_name=alice",
        json={"name": "Tailored", "project_ids": [1, 2]},
    )
    assert r.status_code == 200
    assert r.json()["resume_id"] == 9


@patch("api.routes.resume_builder.resume_exists", return_value=True)
@patch("api.routes.resume_builder.save_resume_edits")
def test_resume_builder_save_edits(mock_se, mock_ex, client):
    r = client.post(
        "/api/resume-builder/resume/1/edit?user_name=alice",
        json={"skills": []},
    )
    assert r.status_code == 200


@patch("api.routes.resume_builder.export_pdf", return_value=b"%PDF-1.4")
def test_resume_builder_export_pdf_body(mock_pdf, client):
    r = client.post(
        "/api/resume-builder/resume/export?format=pdf&user_name=alice",
        json={"x": 1},
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"


@patch("api.routes.resume_builder.render_html", return_value="<html/>")
def test_resume_builder_export_html(mock_rh, client):
    r = client.post(
        "/api/resume-builder/resume/export?format=html&user_name=alice",
        json={"x": 1},
    )
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


@patch("api.routes.resume_builder.export_markdown", return_value="# hi")
def test_resume_builder_export_md(mock_em, client):
    r = client.post(
        "/api/resume-builder/resume/export?format=markdown&user_name=alice",
        json={"x": 1},
    )
    assert r.status_code == 200


def test_resume_builder_export_bad_format(client):
    r = client.post(
        "/api/resume-builder/resume/export?format=xml&user_name=alice",
        json={},
    )
    assert r.status_code == 400


@patch("api.routes.resume_builder._get_resume_model", return_value={"m": 1})
@patch("api.routes.resume_builder.export_pdf", return_value=b"%PDF")
def test_resume_builder_export_pdf_get(mock_pdf, mock_gm, client):
    r = client.get(
        "/api/resume-builder/resume/export/pdf",
        params={"user_name": "alice", "resume_id": 1},
    )
    assert r.status_code == 200


def test_resume_builder_export_pdf_get_conflict_params(client):
    r = client.get(
        "/api/resume-builder/resume/export/pdf",
        params={"user_name": "alice", "resume_id": 1, "project_ids": [1]},
    )
    assert r.status_code == 400


@patch("api.routes.resume_builder.add_projects_to_resume")
def test_resume_builder_add_projects(mock_add, client):
    r = client.post(
        "/api/resume-builder/resume/2/projects?user_name=alice",
        json={"project_ids": [1]},
    )
    assert r.status_code == 200


def test_resume_builder_add_projects_master_forbidden(client):
    r = client.post(
        "/api/resume-builder/resume/0/projects?user_name=alice",
        json={"project_ids": [1]},
    )
    assert r.status_code == 400


@patch("api.routes.resume_builder.remove_project_from_resume")
def test_resume_builder_remove_project(mock_rm, client):
    r = client.delete("/api/resume-builder/resume/2/project/9?user_name=alice")
    assert r.status_code == 200


@patch("api.routes.resume_builder.delete_resume")
def test_resume_builder_delete(mock_del, client):
    r = client.delete("/api/resume-builder/resume/5?user_name=alice")
    assert r.status_code == 200


def test_resume_builder_delete_master_forbidden(client):
    r = client.delete("/api/resume-builder/resume/0?user_name=alice")
    assert r.status_code == 400


# --- resume_portfolio.py ---
@patch("api.routes.resume_portfolio.get_project_with_analysis", return_value=None)
def test_resume_preview_not_found(mock_gp, client):
    r = client.get("/api/resume/preview/999")
    assert r.status_code == 404


@patch("api.routes.resume_portfolio.get_project_with_analysis", return_value={"id": 1})
@patch(
    "api.routes.resume_portfolio.ItemFormatter.format_resume_item",
    return_value={
        "project_title": "Demo",
        "role": "Developer",
        "description_bullets": ["Shipped features"],
        "technologies": ["Python"],
    },
)
def test_resume_preview_ok(mock_fmt, mock_gp, client):
    r = client.get("/api/resume/preview/1")
    assert r.status_code == 200
    body = r.json()
    assert body["project_title"] == "Demo"
    assert body["role"] == "Developer"


@patch("api.routes.resume_portfolio.ResumeManager.get_user_resume", return_value=None)
def test_skills_empty(mock_gr, client):
    r = client.get("/api/skills")
    assert r.status_code == 200
    assert r.json()["skills"] == []


@patch("api.routes.resume_portfolio.ResumeManager.get_user_resume")
def test_skills_with_data(mock_gr, client):
    mock_gr.return_value = {
        "resume_data": {
            "all_skills": ["Py"],
            "categorized_skills": {},
            "languages": [],
            "frameworks": [],
        }
    }
    r = client.get("/api/skills", params={"user_name": "u"})
    assert r.status_code == 200
    assert r.json()["skills"] == ["Py"]


@patch("database.user_informations.get_all_users", return_value=[])
@patch("api.routes.resume_portfolio.ResumeManager.get_portfolio_settings", return_value={})
def test_public_portfolio_users_empty(mock_gs, mock_ga, client):
    r = client.get("/api/portfolio/public-users")
    assert r.status_code == 200
    assert r.json()["users"] == []


@patch("api.routes.resume_portfolio.ResumeManager.get_portfolio_settings")
@patch("api.routes.resume_portfolio.PortfolioManager")
def test_public_portfolio_success(mock_pm_cls, mock_gs, client):
    mock_gs.return_value = {
        "is_public": True,
        "show_stats": True,
        "show_timeline": False,
        "show_heatmap": False,
        "show_top_projects": False,
    }
    inst = MagicMock()
    inst.generate_portfolio_report.return_value = {
        "summary": {},
        "skills": {},
        "projects": [{"name": "App", "summary": "", "primary_language": "", "skills": [], "frameworks": []}],
    }
    mock_pm_cls.return_value = inst
    r = client.get("/api/portfolio/public/alice")
    assert r.status_code == 200
    assert r.json()["success"] is True


@patch(
    "api.routes.resume_portfolio.ResumeManager.get_portfolio_settings",
    return_value={"is_public": False},
)
def test_public_portfolio_private(mock_gs, client):
    r = client.get("/api/portfolio/public/alice")
    assert r.status_code == 403


@patch(
    "api.routes.resume_portfolio._get_public_settings_or_403",
    return_value={"is_public": True, "show_timeline": True, "updated_at": "x"},
)
def test_public_portfolio_settings(mock_g, client):
    r = client.get("/api/portfolio/public/u1/settings")
    assert r.status_code == 200
    assert r.json()["success"] is True
    assert "updated_at" not in r.json()["settings"]


@pytest.fixture
def authed_client():
    app.dependency_overrides[get_authenticated_user] = lambda: {
        "user_id": 1,
        "user_name": "tester",
        "is_login": True,
        "create_time": None,
        "last_login_time": None,
    }
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_authenticated_user, None)


@patch("api.routes.settings.ConsentStorage.get_consent_status", return_value={"c": 1})
@patch("api.routes.settings.get_user_git_username", return_value="gh")
def test_settings_get_all(mock_git, mock_cs, authed_client):
    r = authed_client.get("/api/settings", params={"username": "tester"})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["privacy"] == {"c": 1}
    assert body["general"]["git_username"] == "gh"


@patch("api.routes.settings._user_data_to_dict", side_effect=RuntimeError("x"))
def test_settings_get_all_500(mock_ud, authed_client):
    r = authed_client.get("/api/settings", params={"username": "tester"})
    assert r.status_code == 500


def test_settings_account_post_placeholder(authed_client):
    r = authed_client.post("/api/settings/account", params={"username": "tester"}, json={})
    assert r.status_code == 200
    assert "coming soon" in r.json()["message"].lower()


@patch("api.routes.settings.ConsentStorage.get_consent_status", return_value={})
@patch("api.routes.settings.ConsentStorage.store_consent", return_value=True)
def test_settings_privacy_post(mock_sc, mock_gcs, authed_client):
    r = authed_client.post(
        "/api/settings/privacy",
        params={"username": "tester"},
        json={"consent_given": True},
    )
    assert r.status_code == 200


@patch("api.routes.settings.get_user_git_username", return_value="g")
def test_settings_general_get(mock_g, authed_client):
    r = authed_client.get("/api/settings/general", params={"username": "tester"})
    assert r.status_code == 200


@patch("api.routes.settings.update_user_git_username")
@patch("api.routes.settings.get_user_git_username", return_value="newg")
def test_settings_general_post(mock_gu, mock_up, authed_client):
    r = authed_client.post(
        "/api/settings/general",
        params={"username": "tester"},
        json={"git_username": "newg"},
    )
    assert r.status_code == 200


@patch("external_services.permission_manager.ExternalServicePermission")
def test_settings_llm_get(mock_perm_cls, authed_client):
    inst = MagicMock()
    inst.has_permission.return_value = True
    mock_perm_cls.return_value = inst
    r = authed_client.get("/api/settings/llm", params={"username": "tester"})
    assert r.status_code == 200
    assert r.json()["llm_enabled"] is True


@patch("external_services.external_service_prompt.ExternalServicePrompt.store_permission", return_value=True)
@patch("api.routes.settings.ConsentStorage.store_consent", return_value=True)
def test_settings_llm_post(mock_cs, mock_sp, authed_client):
    r = authed_client.post(
        "/api/settings/llm",
        params={"username": "tester"},
        json={"llm_enabled": True},
    )
    assert r.status_code == 200


@patch("external_services.external_service_prompt.ExternalServicePrompt.store_permission", return_value=False)
@patch("api.routes.settings.ConsentStorage.store_consent", return_value=True)
def test_settings_llm_post_store_failed(mock_cs, mock_sp, authed_client):
    r = authed_client.post(
        "/api/settings/llm",
        params={"username": "tester"},
        json={"llm_enabled": True},
    )
    assert r.status_code == 500


@patch("api.routes.settings.init_user_profile_table")
@patch("api.routes.settings.get_user_profile", return_value=None)
def test_settings_profile_get_empty(mock_gp, mock_init, authed_client):
    r = authed_client.get("/api/settings/profile", params={"username": "tester"})
    assert r.status_code == 200
    assert r.json()["has_profile"] is False


@patch("api.routes.settings.init_user_profile_table")
@patch("api.routes.settings.save_user_profile")
def test_settings_profile_post(mock_save, mock_init, authed_client):
    r = authed_client.post(
        "/api/settings/profile",
        params={"username": "tester"},
        json={"display_name": "DN", "email": "e@e.com"},
    )
    assert r.status_code == 200
