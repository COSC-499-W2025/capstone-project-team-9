# tests/test_user_preferences.py

import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the project root to sys.path so `config` can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Import your module
from database import user_preferences

@pytest.fixture
def mock_conn_cursor():
    """
    Fixture to mock get_connection() and provide a cursor.
    """
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    with patch('database.user_preferences.get_connection', return_value=mock_conn):
        yield mock_cursor, mock_conn

# ----------------------------
# Tests for init_user_preferences_table
# ----------------------------
def test_init_user_preferences_table_calls_execute_and_commit(mock_conn_cursor):
    mock_cursor, mock_conn = mock_conn_cursor
    user_preferences.init_user_preferences_table()
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called()

# ----------------------------
# Tests for update_user_preferences
# ----------------------------
@pytest.mark.parametrize("consent_val", [True, False])
def test_update_user_preferences(mock_conn_cursor, consent_val):
    mock_cursor, mock_conn = mock_conn_cursor
    user_preferences.update_user_preferences(consent_val)
    mock_cursor.execute.assert_called()
    args, _ = mock_cursor.execute.call_args
    assert str(consent_val) in str(args)

# ----------------------------
# Tests for get_user_preferences
# ----------------------------
def test_get_user_preferences_returns_tuple(mock_conn_cursor):
    mock_cursor, mock_conn = mock_conn_cursor
    expected = (True, datetime.now())
    mock_cursor.fetchone.return_value = expected
    result = user_preferences.get_user_preferences()
    assert result == expected
    mock_conn.close.assert_called()

# ----------------------------
# Tests for update_user_collaboration
# ----------------------------
@pytest.mark.parametrize("collab_val", [True, False])
def test_update_user_collaboration(mock_conn_cursor, collab_val):
    mock_cursor, mock_conn = mock_conn_cursor
    user_preferences.update_user_collaboration(collab_val)
    mock_cursor.execute.assert_called()
    args, _ = mock_cursor.execute.call_args
    assert str(collab_val) in str(args)
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called()

# ----------------------------
# Tests for get_user_callaboration
# ----------------------------
def test_get_user_callaboration_returns_tuple(mock_conn_cursor):
    mock_cursor, mock_conn = mock_conn_cursor
    expected = (False, datetime.now())
    mock_cursor.fetchone.return_value = expected
    result = user_preferences.get_user_callaboration()
    assert result == expected
    mock_conn.close.assert_called()

# ----------------------------
# Tests for update_user_git_username
# ----------------------------
def test_update_user_git_username(mock_conn_cursor):
    mock_cursor, mock_conn = mock_conn_cursor
    username = "testuser"
    user_preferences.update_user_git_username(username)
    args, _ = mock_cursor.execute.call_args
    assert username in str(args)
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called()

# ----------------------------
# Tests for get_user_git_username
# ----------------------------
def test_get_user_git_username_returns_tuple(mock_conn_cursor):
    mock_cursor, mock_conn = mock_conn_cursor
    expected = ("testuser",)
    mock_cursor.fetchone.return_value = expected
    result = user_preferences.get_user_git_username()
    assert result == expected
    mock_conn.close.assert_called()
