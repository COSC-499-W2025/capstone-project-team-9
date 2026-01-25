"""
Tests for deleting projects and related cleanup.
"""
import os
import sys
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from project_manager import delete_project
from account.user_manager import AuthManager


@contextmanager
def _mock_db_cursor(cursor):
    yield (MagicMock(), cursor)


def _build_cursor_for_delete():
    cursor = MagicMock()

    def execute_side_effect(query, params=None):
        query_text = " ".join(query.split()).lower()
        if "select id, filename, filepath" in query_text:
            cursor.rowcount = 1
        elif "delete from project_metrics" in query_text:
            cursor.rowcount = 2
        elif "delete from analysis_results" in query_text:
            cursor.rowcount = 3
        elif "delete from project_rankings" in query_text:
            cursor.rowcount = 4
        elif "delete from file_contents" in query_text:
            cursor.rowcount = 5
        elif "delete from uploaded_files" in query_text:
            cursor.rowcount = 1
        else:
            cursor.rowcount = 0

    cursor.execute.side_effect = execute_side_effect
    cursor.fetchone.return_value = (123, "demo.zip", "uploads/demo.zip")
    return cursor


def test_delete_project_removes_records_and_file():
    AuthManager._current_user = {"user_name": "testuser", "user_id": 1}

    cursor = _build_cursor_for_delete()
    with patch("project_manager.with_db_connection", return_value=_mock_db_cursor(cursor)), \
        patch("project_manager._table_exists", return_value=True), \
        patch("os.path.exists", return_value=True), \
        patch("os.remove") as mock_remove:
        result = delete_project(123)

    assert result["success"] is True
    assert result["deleted"]["project_metrics"] == 2
    assert result["deleted"]["analysis_results"] == 3
    assert result["deleted"]["project_rankings"] == 4
    assert result["deleted"]["file_contents"] == 5
    assert result["deleted"]["uploaded_files"] == 1
    assert result["file_deleted"] is True
    mock_remove.assert_called_once_with("uploads/demo.zip")


def test_delete_project_requires_login():
    AuthManager.clear_session()
    result = delete_project(123)
    assert result["success"] is False
    assert result["error"] == "Not logged in"
