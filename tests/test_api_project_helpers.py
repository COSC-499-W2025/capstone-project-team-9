"""Tests for api.routes.project helpers (pure logic + LLM gate)."""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from api.routes import project as project_routes
from api.main import app


def test_detect_image_type_png_jpeg_gif():
    assert project_routes._detect_image_type(b"\x89PNG\r\n\x1a\n") == "png"
    assert project_routes._detect_image_type(b"\xff\xd8\xff") == "jpeg"
    assert project_routes._detect_image_type(b"GIF89a") == "gif"
    assert project_routes._detect_image_type(b"BM") == "bmp"
    assert project_routes._detect_image_type(b"II*\x00") == "tiff"
    assert project_routes._detect_image_type(b"RIFF\x00\x00\x00\x00WEBP") == "webp"
    assert project_routes._detect_image_type(b"") is None
    assert project_routes._detect_image_type(b"unknown") is None


def test_ensure_llm_allowed_requires_user():
    with pytest.raises(HTTPException) as ei:
        project_routes._ensure_llm_allowed(None)
    assert ei.value.status_code == 400


@patch("api.routes.project.ExternalServicePermission")
@patch("api.routes.project.ConsentStorage.get_consent_status")
def test_ensure_llm_allowed_blocks_without_consent(mock_cs, mock_pm_cls):
    mock_cs.return_value = {"consent_given": False}
    inst = MagicMock()
    inst.has_permission.return_value = True
    mock_pm_cls.return_value = inst
    with pytest.raises(HTTPException) as ei:
        project_routes._ensure_llm_allowed("u")
    assert ei.value.status_code == 403


@patch("api.routes.project.ExternalServicePermission")
@patch("api.routes.project.ConsentStorage.get_consent_status")
def test_ensure_llm_allowed_ok(mock_cs, mock_pm_cls):
    mock_cs.return_value = {"consent_given": True}
    inst = MagicMock()
    inst.has_permission.return_value = True
    mock_pm_cls.return_value = inst
    assert project_routes._ensure_llm_allowed("alice") == "alice"


@patch("api.routes.project.list_projects", return_value=[])
def test_projects_list_for_user(mock_lp):
    r = TestClient(app).get("/api/projects", params={"user_name": "nobody"})
    assert r.status_code == 200
    assert r.json()["count"] == 0


@patch("api.routes.project.list_uploaded_files", return_value=[])
def test_projects_list_all_users(mock_luf):
    r = TestClient(app).get("/api/projects")
    assert r.status_code == 200
