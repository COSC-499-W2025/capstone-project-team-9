import os
import sys
import tempfile
import zipfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Make src importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import parsing.file_contents_manager as fcm  # noqa: E402


def _ctx_with_cursor(cursor):
    ctx = MagicMock()
    ctx.__enter__.return_value = cursor
    ctx.__exit__.return_value = False
    return ctx


@patch("parsing.file_contents_manager.with_db_cursor")
def test_init_file_contents_table_runs_migrations(mock_cursor_factory):
    """Ensure init_file_contents_table executes creation/migration statements."""
    cursors = [MagicMock(), MagicMock(), MagicMock()]
    mock_cursor_factory.side_effect = [_ctx_with_cursor(c) for c in cursors]

    fcm.init_file_contents_table()

    # First cursor: table creation
    assert cursors[0].execute.call_count == 1
    # Second cursor: migration columns (source_created_at, source_modified_at, line_count)
    assert cursors[1].execute.call_count == 3
    # Third cursor: index creation
    assert cursors[2].execute.call_count == 2


@patch("parsing.file_contents_manager._insert_batch")
@patch("parsing.file_contents_manager.with_db_connection")
@patch("parsing.file_contents_manager.Binary", lambda b: b)
def test_extract_and_store_file_contents_success(mock_conn_factory, mock_insert_batch):
    """Extract files from a zip and store via batches."""
    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, "files.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("code.py", "print('hi')")
        zf.writestr("image.png", b"\x89PNG")

    cursor = MagicMock()
    # No existing duplicates in file_contents for this happy-path test
    cursor.fetchone.return_value = None
    conn = MagicMock()
    mock_conn_factory.return_value = _ctx_with_cursor((conn, cursor))

    result = fcm.extract_and_store_file_contents(1, zip_path, batch_size=1)

    assert result["success"] is True
    assert result["total_files"] == 2
    assert mock_insert_batch.call_count == 2


@patch("parsing.file_contents_manager.with_db_connection")
def test_extract_and_store_file_contents_too_many_files(mock_conn_factory):
    """Respect max_files guard."""
    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, "files.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("a.txt", "a")
        zf.writestr("b.txt", "b")

    mock_conn_factory.return_value = _ctx_with_cursor((MagicMock(), MagicMock()))

    result = fcm.extract_and_store_file_contents(1, zip_path, max_files=1)
    assert result["success"] is False
    assert "Too many files" in result["error"]


def test_extract_and_store_file_contents_missing_or_invalid():
    """Handle missing or invalid zip files."""
    missing = fcm.extract_and_store_file_contents(1, "/nope.zip")
    assert missing["success"] is False and "File not found" in missing["error"]

    tmp_dir = tempfile.mkdtemp()
    bad_zip = os.path.join(tmp_dir, "not_zip.txt")
    with open(bad_zip, "w", encoding="utf-8") as f:
        f.write("not a zip")
    invalid = fcm.extract_and_store_file_contents(1, bad_zip)
    assert invalid["success"] is False and "Invalid zip file" in invalid["error"]


def test_insert_batch_calls_executemany():
    cursor = MagicMock()
    batch = [(1, "p", "n", ".py", 1, b"", "text/plain", False, None, None)]
    fcm._insert_batch(cursor, batch)
    cursor.executemany.assert_called_once()


@patch("parsing.file_contents_manager.with_db_cursor")
def test_get_zip_file_found_and_missing(mock_cursor_factory):
    cursor = MagicMock()
    cursor.fetchone.side_effect = [(b"zipdata",), None]
    mock_cursor_factory.return_value = _ctx_with_cursor(cursor)

    found = fcm.get_zip_file(1)
    missing = fcm.get_zip_file(1)

    assert found == b"zipdata"
    assert missing is None


@patch("parsing.file_contents_manager.with_db_cursor")
def test_get_file_contents_by_folder(mock_cursor_factory):
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        ("folder/file.txt", "file.txt", ".txt", 10, b"data", "text/plain", False, datetime(2024, 1, 1))
    ]
    mock_cursor_factory.return_value = _ctx_with_cursor(cursor)

    result = fcm.get_file_contents_by_folder(1)
    assert "folder" in result
    assert result["folder"][0]["file_name"] == "file.txt"


@patch("parsing.file_contents_manager.with_db_cursor")
def test_get_file_statistics_defaults_when_empty(mock_cursor_factory):
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    mock_cursor_factory.return_value = _ctx_with_cursor(cursor)

    stats = fcm.get_file_statistics(1)
    assert stats["total_files"] == 0
    assert stats["file_extensions"] == []


@patch("parsing.file_contents_manager.with_db_cursor")
def test_get_file_statistics_normal(mock_cursor_factory):
    cursor = MagicMock()
    cursor.fetchone.return_value = (3, 123, 2, 1)
    cursor.fetchall.side_effect = [[(".py", 2)], [("root", 3)]]
    mock_cursor_factory.return_value = _ctx_with_cursor(cursor)

    stats = fcm.get_file_statistics(1)
    assert stats["total_files"] == 3
    assert stats["file_extensions"][0]["extension"] == ".py"
    assert stats["folders"][0]["folder"] == "root"


@patch("parsing.file_contents_manager.with_db_cursor")
def test_get_file_contents_by_upload_id(mock_cursor_factory):
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        (1, "p", "n", ".py", 10, b"", "text/plain", False, datetime(2024, 1, 1))
    ]
    mock_cursor_factory.return_value = _ctx_with_cursor(cursor)

    files = fcm.get_file_contents_by_upload_id(1)
    assert files[0]["file_extension"] == ".py"
    assert files[0]["id"] == 1


def test_is_binary_file_and_content_type():
    assert fcm._is_binary_file(".png") is True
    assert fcm._is_binary_file(".py") is False
    assert fcm._get_content_type(".py") == "text/x-python"
    assert fcm._get_content_type(".unknown") == "application/octet-stream"

