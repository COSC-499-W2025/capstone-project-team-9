"""Unit tests for api.dependencies (DB + auth helpers)."""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from api.dependencies import get_db_cursor, check_db_connection, get_authenticated_user


def test_get_db_cursor_no_connection():
    with patch("api.dependencies.get_connection", return_value=None):
        gen = get_db_cursor()
        with pytest.raises(HTTPException) as ei:
            next(gen)
        assert ei.value.status_code == 503
        assert ei.value.detail["error_type"] == "DB_UNAVAILABLE"


def test_get_db_cursor_success_commits_and_closes():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    with patch("api.dependencies.get_connection", return_value=mock_conn):
        gen = get_db_cursor()
        cur = next(gen)
        assert cur is mock_cursor
        try:
            next(gen)
        except StopIteration:
            pass
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_get_db_cursor_exception_triggers_rollback():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    with patch("api.dependencies.get_connection", return_value=mock_conn):
        gen = get_db_cursor()
        next(gen)
        with pytest.raises(HTTPException) as ei:
            gen.throw(RuntimeError("db failure"))
        assert ei.value.status_code == 500
        assert ei.value.detail["error_type"] == "DB_ERROR"
    mock_conn.rollback.assert_called_once()


def test_check_db_connection():
    mock_conn = MagicMock()
    with patch("api.dependencies.get_connection", return_value=mock_conn):
        assert check_db_connection() is True
    mock_conn.close.assert_called_once()
    with patch("api.dependencies.get_connection", return_value=None):
        assert check_db_connection() is False


def test_get_authenticated_user_blank_username():
    with pytest.raises(HTTPException) as ei:
        get_authenticated_user(username="   ")
    assert ei.value.status_code == 401
    assert ei.value.detail["error_type"] == "AUTH_REQUIRED"


def test_get_authenticated_user_not_found():
    with patch("api.dependencies.get_user_by_username", return_value=None):
        with pytest.raises(HTTPException) as ei:
            get_authenticated_user(username="nobody")
    assert ei.value.status_code == 401
    assert ei.value.detail["error_type"] == "USER_NOT_FOUND"


def test_get_authenticated_user_not_logged_in():
    with patch(
        "api.dependencies.get_user_by_username",
        return_value={"user_id": 1, "user_name": "u", "is_login": False},
    ):
        with pytest.raises(HTTPException) as ei:
            get_authenticated_user(username="u")
    assert ei.value.status_code == 401
    assert ei.value.detail["error_type"] == "NOT_LOGGED_IN"


def test_get_authenticated_user_success():
    row = {"user_id": 9, "user_name": "alice", "is_login": True}
    with patch("api.dependencies.get_user_by_username", return_value=row):
        assert get_authenticated_user(username="alice") == row
