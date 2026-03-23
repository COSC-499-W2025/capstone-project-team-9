"""Unit tests for api.client.APIClient (httpx mocked)."""
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import httpx
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from api.client import APIClient, get_api_client, set_api_client


def _http_error_response(status: int, json_body=None, text_body=""):
    req = httpx.Request("GET", "http://localhost:8000/api/x")
    if json_body is not None:
        resp = httpx.Response(status, json=json_body, request=req)
    else:
        resp = httpx.Response(status, text=text_body, request=req)
    return httpx.HTTPStatusError("err", request=req, response=resp)


class TestFormatApiError:
    def test_invalid_json_returns_fallback(self):
        req = httpx.Request("GET", "http://x")
        resp = httpx.Response(500, text="not json", request=req)
        assert APIClient._format_api_error(resp, "fb") == "fb"

    def test_unified_error_shape(self):
        req = httpx.Request("GET", "http://x")
        resp = httpx.Response(
            400,
            json={"error_type": "X", "message": "m"},
            request=req,
        )
        assert APIClient._format_api_error(resp, "fb") == "X: m"

    def test_detail_string(self):
        req = httpx.Request("GET", "http://x")
        resp = httpx.Response(400, json={"detail": "oops"}, request=req)
        assert APIClient._format_api_error(resp, "fb") == "API_ERROR: oops"

    def test_detail_dict(self):
        req = httpx.Request("GET", "http://x")
        resp = httpx.Response(
            400,
            json={"detail": {"error_type": "E", "message": "msg"}},
            request=req,
        )
        assert APIClient._format_api_error(resp, "fb") == "E: msg"

    def test_detail_non_str_non_dict(self):
        req = httpx.Request("GET", "http://x")
        resp = httpx.Response(400, json={"detail": [1, 2]}, request=req)
        out = APIClient._format_api_error(resp, "fb")
        assert out.startswith("API_ERROR:")

    def test_unknown_body_returns_fallback(self):
        req = httpx.Request("GET", "http://x")
        resp = httpx.Response(400, json={"other": True}, request=req)
        assert APIClient._format_api_error(resp, "fb") == "fb"


class TestMakeRequest:
    def test_success_returns_json(self):
        c = APIClient(base_url="http://example.com")
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"ok": True}

        mock_client = MagicMock()
        mock_client.request.return_value = mock_resp
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_client
        mock_cm.__exit__.return_value = False

        with patch("api.client.httpx.Client", return_value=mock_cm):
            out = c._make_request("GET", "/projects")

        assert out == {"ok": True}
        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert args[0] == "GET"
        assert args[1] == "http://example.com/api/projects"

    def test_http_status_error_wraps_message(self):
        c = APIClient(base_url="http://example.com")
        err = _http_error_response(400, json_body={"error_type": "BAD", "message": "nope"})

        mock_client = MagicMock()
        mock_client.request.side_effect = err
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_client
        mock_cm.__exit__.return_value = False

        with patch("api.client.httpx.Client", return_value=mock_cm):
            with pytest.raises(Exception, match="API Error: BAD: nope"):
                c._make_request("GET", "/x")


class TestUploadAndHelpers:
    def test_upload_missing_file(self):
        c = APIClient()
        with pytest.raises(FileNotFoundError):
            c.upload_project("/nonexistent/path.zip")

    def test_upload_passes_user_name_param(self):
        fd, path = tempfile.mkstemp(suffix=".zip")
        os.close(fd)
        try:
            c = APIClient(base_url="http://x")
            with patch.object(c, "_make_request", return_value={"success": True}) as m:
                c.upload_project(path, user_name="u1")
            kwargs = m.call_args[1]
            assert kwargs["params"] == {"user_name": "u1"}
        finally:
            os.unlink(path)

    def test_post_privacy_and_get_projects_delegate(self):
        c = APIClient(base_url="http://x")
        with patch.object(c, "_make_request", return_value={}) as m:
            c.post_privacy_consent(True, "alice")
            m.assert_called_with("POST", "/privacy-consent", json={"consent_given": True, "user_name": "alice"})
        with patch.object(c, "_make_request", return_value={}) as m:
            c.get_projects("bob")
            m.assert_called_with("GET", "/projects", params={"user_name": "bob"})
        with patch.object(c, "_make_request", return_value={}) as m:
            c.get_project_by_id(5, user_name="bob")
            m.assert_called_with("GET", "/projects/5", params={"user_name": "bob"})

    def test_resume_portfolio_methods(self):
        c = APIClient(base_url="http://x")
        with patch.object(c, "_make_request", return_value={}) as m:
            c.list_resume_custom_wording("u")
            m.assert_called_with("GET", "/resume/u/custom-wording")
            c.save_resume_custom_wording("u", 3, "w")
            m.assert_called_with(
                "POST", "/resume/u/custom-wording", json={"project_id": 3, "wording": "w"}
            )
            c.clear_resume_custom_wording("u", 3)
            m.assert_called_with("DELETE", "/resume/u/custom-wording/3")
            c.list_portfolio_customizations("u")
            m.assert_called_with("GET", "/portfolio/u/custom-data")
            c.save_portfolio_customization("u", 1, "t", "d", "r")
            m.assert_called_with(
                "POST",
                "/portfolio/u/custom-data",
                json={
                    "project_id": 1,
                    "custom_title": "t",
                    "custom_description": "d",
                    "custom_role": "r",
                },
            )
            c.get_portfolio_customization("u", 2)
            m.assert_called_with("GET", "/portfolio/u/custom-data/2")
            c.clear_portfolio_customization("u", 2)
            m.assert_called_with("DELETE", "/portfolio/u/custom-data/2")


def test_get_and_set_api_client():
    import api.client as mod

    mod._default_client = None
    a = get_api_client()
    b = get_api_client()
    assert a is b
    custom = APIClient(base_url="http://custom")
    set_api_client(custom)
    assert get_api_client() is custom
    mod._default_client = None
