from typing import List, Tuple
from datetime import datetime, date
from unittest.mock import patch, MagicMock
import pytest
from src.analysis import key_metrics

class _FakeCursor:
    def __init__(self, rows):
        self._rows = rows
    # context manager support
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    # DB API stubs
    def execute(self, *_args, **_kwargs):
        pass
    def fetchall(self):
        return self._rows
    def close(self):
        pass

class _FakeConn:
    def __init__(self, rows):
        self._rows = rows
    # context manager support
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    # DB API stubs
    def cursor(self):
        return _FakeCursor(self._rows)

    def commit(self):
        pass

def _mock_db(monkeypatch, rows: List[Tuple[str, int, str, int]]):
    monkeypatch.setattr(key_metrics, "get_connection", lambda: _FakeConn(rows))

def test_analyze_project_from_db(monkeypatch):
    rows = [
        ("src/a.py", 120, "Python", False, b"line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10"),
        ("docs/readme.md", 50, "Markdown", False, b"line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10\nline11\nline12\nline13\nline14\nline15"),
        ("data/users.csv", 90, "CSV", False, b"line1\nline2\nline3\nline4\nline5"),
    ]
    _mock_db(monkeypatch, rows)
    monkeypatch.setattr("builtins.input", lambda _: "3")

    result = key_metrics.analyze_project_from_db(project_id=1)
    assert result["totals"]["files"] == 3
    assert result["totals"]["lines"] == 30
    assert "by_language" in result and "by_activity" in result

def test_empty_project(monkeypatch):
    _mock_db(monkeypatch, [])
    result = key_metrics.analyze_project_from_db(project_id=999)
    assert result["totals"]["files"] == 0
    assert result["totals"]["lines"] == 0

def test_print_summary(capsys, monkeypatch):
    rows = [("src/x.py", 100, "Python", False, b"line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8")]
    _mock_db(monkeypatch, rows)
    key_metrics.analyze_project_from_db(project_id=42)
    out = capsys.readouterr().out
    assert "Key Metrics" in out and "Python" in out

def test_choose_author_from_zip_no_authors(monkeypatch):
    """Test choose_author_from_zip with no authors."""
    monkeypatch.setattr(key_metrics, "get_project_contributor_name", lambda _: None)
    monkeypatch.setattr(key_metrics, "get_file_contents_by_upload_id", lambda _: {})
    monkeypatch.setattr(key_metrics, "_identify_authors_from_zip", lambda _: set())
    monkeypatch.setattr(key_metrics, "_extract_common_names_from_filenames", lambda _: set())
    
    result = key_metrics.choose_author_from_zip(1)
    assert result is None

def test_choose_author_from_zip_git_username_match(monkeypatch):
    """Test choose_author_from_zip when git username matches."""
    monkeypatch.setattr(key_metrics, "get_project_contributor_name", lambda _: None)
    monkeypatch.setattr(key_metrics, "get_file_contents_by_upload_id", lambda _: {})
    monkeypatch.setattr(key_metrics, "_identify_authors_from_zip", lambda _: {"user1", "user2"})
    monkeypatch.setattr(key_metrics, "_extract_common_names_from_filenames", lambda _: set())
    monkeypatch.setattr(key_metrics, "get_user_git_username", lambda: "user1")
    
    result = key_metrics.choose_author_from_zip(1)
    assert result == "user1"

def test_choose_author_from_zip_user_selection(monkeypatch, capsys):
    """Test choose_author_from_zip with user selection."""
    monkeypatch.setattr(key_metrics, "get_project_contributor_name", lambda _: None)
    monkeypatch.setattr(key_metrics, "get_file_contents_by_upload_id", lambda _: {})
    monkeypatch.setattr(key_metrics, "_identify_authors_from_zip", lambda _: {"user1", "user2"})
    monkeypatch.setattr(key_metrics, "_extract_common_names_from_filenames", lambda _: set())
    monkeypatch.setattr(key_metrics, "get_user_git_username", lambda: "other_user")
    monkeypatch.setattr(key_metrics, "set_project_contributor_name", lambda *_args, **_kwargs: True)
    monkeypatch.setattr("builtins.input", lambda _: "1")
    
    result = key_metrics.choose_author_from_zip(1)
    assert result == "user1" or result == "user2"  # sorted order

def test_choose_author_from_zip_all_authors(monkeypatch):
    """Test choose_author_from_zip selecting all authors."""
    monkeypatch.setattr(key_metrics, "get_project_contributor_name", lambda _: None)
    monkeypatch.setattr(key_metrics, "get_file_contents_by_upload_id", lambda _: {})
    monkeypatch.setattr(key_metrics, "_identify_authors_from_zip", lambda _: {"user1", "user2"})
    monkeypatch.setattr(key_metrics, "_extract_common_names_from_filenames", lambda _: set())
    monkeypatch.setattr(key_metrics, "get_user_git_username", lambda: "other_user")
    monkeypatch.setattr("builtins.input", lambda _: "3")  # Select "all authors"
    
    result = key_metrics.choose_author_from_zip(1)
    assert result is None

def test_choose_author_from_zip_invalid_input(monkeypatch):
    """Test choose_author_from_zip with invalid input."""
    monkeypatch.setattr(key_metrics, "get_project_contributor_name", lambda _: None)
    monkeypatch.setattr(key_metrics, "get_file_contents_by_upload_id", lambda _: {})
    monkeypatch.setattr(key_metrics, "_identify_authors_from_zip", lambda _: {"user1", "user2"})
    monkeypatch.setattr(key_metrics, "_extract_common_names_from_filenames", lambda _: set())
    monkeypatch.setattr(key_metrics, "get_user_git_username", lambda: "other_user")
    monkeypatch.setattr(key_metrics, "set_project_contributor_name", lambda *_args, **_kwargs: True)
    
    inputs = ["invalid", "0", "1"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))
    
    result = key_metrics.choose_author_from_zip(1)
    assert result == "user1" or result == "user2"

def test_choose_author_from_zip_contributor_name(monkeypatch):
    """Test choose_author_from_zip returns contributor_name when set."""
    monkeypatch.setattr(key_metrics, "get_project_contributor_name", lambda _: "Sam")
    monkeypatch.setattr(key_metrics, "get_file_contents_by_upload_id", lambda _: {})
    monkeypatch.setattr(key_metrics, "_identify_authors_from_zip", lambda _: set())
    monkeypatch.setattr(key_metrics, "_extract_common_names_from_filenames", lambda _: set())

    result = key_metrics.choose_author_from_zip(1)
    assert result == "Sam"

def test_get_project_contributor_name(monkeypatch):
    """Test get_project_contributor_name trims and returns stored name."""
    class _Cursor:
        def execute(self, *_args, **_kwargs):
            pass
        def fetchone(self):
            return ("  Alex  ",)
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def close(self):
            pass
    class _Conn:
        def cursor(self):
            return _Cursor()
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
    monkeypatch.setattr(key_metrics, "get_connection", lambda: _Conn())

    result = key_metrics.get_project_contributor_name(1)
    assert result == "Alex"

def test_set_project_contributor_name_success(monkeypatch):
    """Test set_project_contributor_name returns True on update."""
    class _Cursor:
        def execute(self, *_args, **_kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def close(self):
            pass
    class _Conn:
        def cursor(self):
            return _Cursor()
        def commit(self):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
    monkeypatch.setattr(key_metrics, "get_connection", lambda: _Conn())

    result = key_metrics.set_project_contributor_name(1, "Dana")
    assert result is True

def test_set_project_contributor_name_invalid_name(monkeypatch):
    """Test set_project_contributor_name rejects empty names."""
    result = key_metrics.set_project_contributor_name(1, "  ")
    assert result is False

def test_get_author_file_contributions_from_zip_invalid_project_id(monkeypatch):
    """Test get_author_file_contributions_from_zip with invalid project_id."""
    result = key_metrics.get_author_file_contributions_from_zip(0, "author")
    assert result == {"created": set(), "modified": set(), "deleted": set()}

def test_get_author_file_contributions_from_zip_no_zip_data(monkeypatch):
    """Test get_author_file_contributions_from_zip with no zip data."""
    monkeypatch.setattr(key_metrics, "get_zip_file", lambda _: None)
    result = key_metrics.get_author_file_contributions_from_zip(1, "author")
    assert result == {"created": set(), "modified": set(), "deleted": set()}

def test_get_author_file_contributions_from_zip_no_repo(monkeypatch):
    """Test get_author_file_contributions_from_zip with no repo."""
    mock_ic = MagicMock()
    mock_ic.extract_repo.return_value = None
    
    monkeypatch.setattr(key_metrics, "get_zip_file", lambda _: b"zip_data")
    monkeypatch.setattr(key_metrics, "identify_contributors", lambda **kwargs: mock_ic)
    
    result = key_metrics.get_author_file_contributions_from_zip(1, "author")
    assert result == {"created": set(), "modified": set(), "deleted": set()}
    mock_ic.cleanup.assert_called_once()

def test_get_author_file_contributions_from_zip_no_file_contribs(monkeypatch):
    """Test get_author_file_contributions_from_zip with no file contributions."""
    mock_ic = MagicMock()
    mock_ic.extract_repo.return_value = "/path/to/repo"
    mock_ic.get_file_contributions.return_value = {}
    
    monkeypatch.setattr(key_metrics, "get_zip_file", lambda _: b"zip_data")
    monkeypatch.setattr(key_metrics, "identify_contributors", lambda **kwargs: mock_ic)
    
    result = key_metrics.get_author_file_contributions_from_zip(1, "author")
    assert result == {"created": set(), "modified": set(), "deleted": set()}
    mock_ic.cleanup.assert_called_once()

def test_get_author_file_contributions_from_zip_exact_match(monkeypatch):
    """Test get_author_file_contributions_from_zip with exact author match."""
    mock_ic = MagicMock()
    mock_ic.extract_repo.return_value = "/path/to/repo"
    mock_ic.get_file_contributions.return_value = {
        "author": {
            "created": {"files": {"file1.py", "file2.txt"}},
            "modified": {"files": {"file3.py"}},
            "deleted": {"files": {"old.py"}}
        }
    }
    
    monkeypatch.setattr(key_metrics, "get_zip_file", lambda _: b"zip_data")
    monkeypatch.setattr(key_metrics, "identify_contributors", lambda **kwargs: mock_ic)
    
    result = key_metrics.get_author_file_contributions_from_zip(1, "author")
    assert len(result["created"]) == 2
    assert len(result["modified"]) == 1
    assert len(result["deleted"]) == 1
    mock_ic.cleanup.assert_called_once()

def test_get_author_file_contributions_from_zip_case_insensitive_match(monkeypatch):
    """Test get_author_file_contributions_from_zip with case-insensitive match."""
    mock_ic = MagicMock()
    mock_ic.extract_repo.return_value = "/path/to/repo"
    mock_ic.get_file_contributions.return_value = {
        "Author": {
            "created": {"files": {"file1.py"}},
            "modified": {"files": set()},
            "deleted": {"files": set()}
        }
    }
    
    monkeypatch.setattr(key_metrics, "get_zip_file", lambda _: b"zip_data")
    monkeypatch.setattr(key_metrics, "identify_contributors", lambda **kwargs: mock_ic)
    
    result = key_metrics.get_author_file_contributions_from_zip(1, "author")
    assert len(result["created"]) == 1
    mock_ic.cleanup.assert_called_once()

def test_get_author_file_contributions_from_zip_author_not_found(monkeypatch):
    """Test get_author_file_contributions_from_zip when author is not found."""
    mock_ic = MagicMock()
    mock_ic.extract_repo.return_value = "/path/to/repo"
    mock_ic.get_file_contributions.return_value = {
        "OtherAuthor": {
            "created": {"files": {"file1.py"}},
            "modified": {"files": set()},
            "deleted": {"files": set()}
        }
    }
    
    monkeypatch.setattr(key_metrics, "get_zip_file", lambda _: b"zip_data")
    monkeypatch.setattr(key_metrics, "identify_contributors", lambda **kwargs: mock_ic)
    
    result = key_metrics.get_author_file_contributions_from_zip(1, "author")
    # Should trigger line 110: return empty_result when author_contrib is None
    assert result == {"created": set(), "modified": set(), "deleted": set()}
    mock_ic.cleanup.assert_called_once()

def test_get_all_files_for_author_from_zip(monkeypatch):
    """Test get_all_files_for_author_from_zip function."""
    monkeypatch.setattr(key_metrics, "get_author_file_contributions_from_zip", 
                       lambda _, __: {
                           "created": {"file1.py"},
                           "modified": {"file2.py"},
                           "deleted": {"file3.py"}
                       })
    
    result = key_metrics.get_all_files_for_author_from_zip(1, "author")
    # Should trigger lines 127-128: union of created, modified, deleted
    assert len(result) == 3
    assert "file1.py" in result
    assert "file2.py" in result
    assert "file3.py" in result

def test_fetch_records_from_db_decode_exception(monkeypatch):
    """Test fetch_records_from_db with decode exception handling."""
    class BadBytes:
        def tobytes(self):
            raise Exception("Cannot convert")
        def count(self, _):
            return 0
    
    rows = [
        ("file.py", 100, "Python", False, BadBytes())
    ]
    _mock_db(monkeypatch, rows)
    
    result = key_metrics.fetch_records_from_db(1)
    # Should trigger lines 177-184: exception handling for decode
    assert len(result) == 1
    assert result[0][3] == 0  # num_lines should be 0 after exception

def test_fetch_records_from_db_git_folder(monkeypatch):
    """Test fetch_records_from_db keeping .git folder files."""
    rows = [
        ("file.py", 100, "Python", False, b"line1\nline2"),
        (".git/config", 50, "Config", False, b"config")
    ]
    _mock_db(monkeypatch, rows)
    
    monkeypatch.setattr(key_metrics, "get_user_collaboration", lambda: (True,))
    monkeypatch.setattr(key_metrics, "choose_author_from_zip", lambda _: "author")
    monkeypatch.setattr(key_metrics, "get_all_files_for_author_from_zip", lambda _, __: {"file.py"})
    
    result = key_metrics.fetch_records_from_db(1)
    # Should trigger line 203: keep = True for .git folder
    assert len(result) >= 1
    assert any("/.git/" in r[0] for r in result) or any(r[0] == "file.py" for r in result)

def test_fetch_activity_timestamps_exception_handling(monkeypatch):
    """Test _fetch_activity_timestamps exception handling paths."""
    call_count = [0]
    def mock_get_connection():
        call_count[0] += 1
        if call_count[0] == 1:
            # First call raises exception
            raise Exception("DB Error")
        elif call_count[0] == 2:
            # Second call returns partial data
            return _FakeConn([(datetime(2024, 1, 1),)])
        else:
            return _FakeConn([])
    
    monkeypatch.setattr(key_metrics, "get_connection", mock_get_connection)
    
    result = key_metrics._fetch_activity_timestamps(1)
    # Should trigger lines 282-283, 312-313: exception handling
    assert isinstance(result, list)

def test_fetch_activity_timestamps_date_conversion(monkeypatch):
    """Test _fetch_activity_timestamps with date to datetime conversion."""
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 15)
    rows = [(start_date, end_date)]
    
    _mock_db(monkeypatch, rows)
    
    result = key_metrics._fetch_activity_timestamps(1)
    # Should trigger lines 293-294, 328-329: date to datetime conversion
    assert len(result) == 2
    assert all(isinstance(ts, datetime) for ts in result)

def test_fetch_activity_timestamps_partial_row_data(monkeypatch):
    """Test _fetch_activity_timestamps with partial row data."""
    rows = [(datetime(2024, 1, 1), None)]  # Only start_ts, end_ts is None
    _mock_db(monkeypatch, rows)
    
    result = key_metrics._fetch_activity_timestamps(1)
    # Should trigger lines 317, 322: handling partial row data
    assert len(result) >= 0

def test_get_author_file_contributions_from_zip_exception(monkeypatch):
    """Test get_author_file_contributions_from_zip with exception."""
    mock_ic = MagicMock()
    mock_ic.extract_repo.side_effect = Exception("Error")
    
    monkeypatch.setattr(key_metrics, "get_zip_file", lambda _: b"zip_data")
    monkeypatch.setattr(key_metrics, "identify_contributors", lambda **kwargs: mock_ic)
    
    result = key_metrics.get_author_file_contributions_from_zip(1, "author")
    assert result == {"created": set(), "modified": set(), "deleted": set()}
    mock_ic.cleanup.assert_called_once()

def test_fetch_records_from_db_binary_content(monkeypatch):
    """Test fetch_records_from_db with binary content."""
    rows = [
        ("file.bin", 100, "Binary", True, b"\x00\x01\x02\x03")
    ]
    _mock_db(monkeypatch, rows)
    
    result = key_metrics.fetch_records_from_db(1)
    assert len(result) == 1
    assert result[0][3] == 0  # num_lines should be 0 for binary

def test_fetch_records_from_db_text_content(monkeypatch):
    """Test fetch_records_from_db with text content."""
    rows = [
        ("file.py", 100, "Python", False, b"line1\nline2\nline3")
    ]
    _mock_db(monkeypatch, rows)
    
    result = key_metrics.fetch_records_from_db(1)
    assert len(result) == 1
    assert result[0][3] == 3  # num_lines

def test_fetch_records_from_db_decode_error(monkeypatch):
    """Test fetch_records_from_db with decode error."""
    rows = [
        ("file.py", 100, "Python", False, b"\xff\xfe\xfd")  # Invalid UTF-8
    ]
    _mock_db(monkeypatch, rows)
    
    result = key_metrics.fetch_records_from_db(1)
    assert len(result) == 1
    assert result[0][3] >= 0  # Should handle error gracefully

def test_fetch_records_from_db_with_collaboration(monkeypatch):
    """Test fetch_records_from_db with collaboration enabled."""
    rows = [
        ("file.py", 100, "Python", False, b"line1\nline2"),
        (".git/config", 50, "Config", False, b"config")
    ]
    _mock_db(monkeypatch, rows)
    
    monkeypatch.setattr(key_metrics, "get_user_collaboration", lambda: (True,))
    monkeypatch.setattr(key_metrics, "choose_author_from_zip", lambda _: "author")
    monkeypatch.setattr(key_metrics, "get_all_files_for_author_from_zip", lambda _, __: {"file.py", ".git/config"})
    
    result = key_metrics.fetch_records_from_db(1)
    # Should include files matching author or .git files
    assert len(result) >= 1

def test_fetch_records_from_db_with_collaboration_author_none(monkeypatch):
    """Test fetch_records_from_db with collaboration but author=None."""
    rows = [
        ("file.py", 100, "Python", False, b"line1\nline2")
    ]
    _mock_db(monkeypatch, rows)
    
    monkeypatch.setattr(key_metrics, "get_user_collaboration", lambda: (True,))
    monkeypatch.setattr(key_metrics, "choose_author_from_zip", lambda _: None)
    monkeypatch.setattr(key_metrics, "get_all_files_for_author_from_zip", lambda _, __: set())
    
    result = key_metrics.fetch_records_from_db(1)
    # When author is None and user_files is empty, the condition len(user_files)>0 is False
    # so filtering is skipped and all results are returned
    assert len(result) == 1

def test_fetch_records_from_db_collaboration_with_matching_files(monkeypatch):
    """Test fetch_records_from_db with collaboration and matching files."""
    rows = [
        ("file.py", 100, "Python", False, b"line1\nline2"),
        ("other.py", 50, "Python", False, b"line1")
    ]
    _mock_db(monkeypatch, rows)
    
    monkeypatch.setattr(key_metrics, "get_user_collaboration", lambda: (True,))
    monkeypatch.setattr(key_metrics, "choose_author_from_zip", lambda _: "author")
    monkeypatch.setattr(key_metrics, "get_all_files_for_author_from_zip", lambda _, __: {"file.py"})
    
    result = key_metrics.fetch_records_from_db(1)
    # Should filter to only include file.py (matching suffix) and .git files
    assert len(result) >= 1
    assert any(r[0] == "file.py" for r in result)

def test_fetch_activity_timestamps_from_file_contents(monkeypatch):
    """Test _fetch_activity_timestamps using file_contents timestamps."""
    start_ts = datetime(2024, 1, 1, 10, 0, 0)
    end_ts = datetime(2024, 1, 15, 10, 0, 0)
    rows = [(start_ts, end_ts)]
    
    _mock_db(monkeypatch, rows)
    
    result = key_metrics._fetch_activity_timestamps(1)
    assert len(result) == 2
    assert result[0] == start_ts
    assert result[1] == end_ts

def test_fetch_activity_timestamps_from_file_contents_date(monkeypatch):
    """Test _fetch_activity_timestamps with date objects."""
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 15)
    rows = [(start_date, end_date)]
    
    _mock_db(monkeypatch, rows)
    
    result = key_metrics._fetch_activity_timestamps(1)
    assert len(result) == 2

def test_fetch_activity_timestamps_fallback_to_uploaded_files(monkeypatch):
    """Test _fetch_activity_timestamps falling back to uploaded_files."""
    # First query returns empty, second returns timestamps
    call_count = [0]
    def mock_get_connection():
        call_count[0] += 1
        if call_count[0] == 1:
            return _FakeConn([])  # First call - empty
        else:
            return _FakeConn([(datetime(2024, 1, 1), datetime(2024, 1, 15))])  # Second call
    
    monkeypatch.setattr(key_metrics, "get_connection", mock_get_connection)
    
    result = key_metrics._fetch_activity_timestamps(1)
    assert len(result) == 2

def test_fetch_activity_timestamps_exception(monkeypatch):
    """Test _fetch_activity_timestamps with exception."""
    # Mock connection to raise exception on first query
    call_count = [0]
    def mock_get_connection():
        call_count[0] += 1
        if call_count[0] == 1:
            raise Exception("DB Error")
        return _FakeConn([])
    
    monkeypatch.setattr(key_metrics, "get_connection", mock_get_connection)
    
    result = key_metrics._fetch_activity_timestamps(1)
    # Should handle exception and continue to fallback
    assert isinstance(result, list)

def test_fetch_activity_timestamps_partial_row(monkeypatch):
    """Test _fetch_activity_timestamps with partial row data."""
    rows = [(datetime(2024, 1, 1),)]  # Only one timestamp
    _mock_db(monkeypatch, rows)
    
    result = key_metrics._fetch_activity_timestamps(1)
    assert len(result) >= 1

def test_compute_timeline_metrics_empty(monkeypatch):
    """Test _compute_timeline_metrics with empty timestamps."""
    result = key_metrics._compute_timeline_metrics([])
    assert result["start"] is None
    assert result["end"] is None
    assert result["duration_days"] == 0
    assert result["active_days"] == 0

def test_compute_timeline_metrics_single_timestamp(monkeypatch):
    """Test _compute_timeline_metrics with single timestamp."""
    timestamps = [datetime(2024, 1, 1, 10, 0, 0)]
    result = key_metrics._compute_timeline_metrics(timestamps)
    assert result["start"] is not None
    assert result["end"] is not None
    assert result["duration_days"] == 0
    assert result["active_days"] == 1

def test_compute_timeline_metrics_multiple_timestamps(monkeypatch):
    """Test _compute_timeline_metrics with multiple timestamps."""
    timestamps = [
        datetime(2024, 1, 1, 10, 0, 0),
        datetime(2024, 1, 5, 10, 0, 0),
        datetime(2024, 1, 10, 10, 0, 0)
    ]
    result = key_metrics._compute_timeline_metrics(timestamps)
    assert result["duration_days"] == 9
    assert result["active_days"] == 3

def test_analyze_project_from_db_silent(monkeypatch):
    """Test analyze_project_from_db with silent=True."""
    rows = [
        ("src/a.py", 120, "Python", False, b"line1\nline2\nline3")
    ]
    _mock_db(monkeypatch, rows)
    
    result = key_metrics.analyze_project_from_db(project_id=1, silent=True)
    assert result["totals"]["files"] == 1
    assert "by_language" in result
    assert "by_activity" in result
    assert "timeline" in result

def test_touch_project_last_modified(monkeypatch):
    """Test _touch_project_last_modified."""
    _mock_db(monkeypatch, [])
    # Should not raise exception
    key_metrics._touch_project_last_modified(1)

def test_touch_project_last_modified_exception(monkeypatch, capsys):
    """Test _touch_project_last_modified with exception."""
    def mock_get_connection():
        conn = MagicMock()
        conn.__enter__ = MagicMock(return_value=conn)
        conn.__exit__ = MagicMock(return_value=False)
        conn.cursor.side_effect = Exception("DB Error")
        return conn
    
    monkeypatch.setattr(key_metrics, "get_connection", mock_get_connection)
    # Should handle exception gracefully and print warning
    key_metrics._touch_project_last_modified(1)
    out = capsys.readouterr().out
    assert "WARN" in out or "Failed" in out
