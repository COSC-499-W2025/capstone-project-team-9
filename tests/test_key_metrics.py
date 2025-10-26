from typing import List, Tuple
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

def _mock_db(monkeypatch, rows: List[Tuple[str, int, str, int]]):
    monkeypatch.setattr(key_metrics, "get_connection", lambda: _FakeConn(rows))

def test_analyze_project_from_db(monkeypatch):
    rows = [
        ("src/a.py", 120, "Python", 10),
        ("docs/readme.md", 50, "Markdown", 15),
        ("data/users.csv", 90, "CSV", 5),
    ]
    _mock_db(monkeypatch, rows)
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
    rows = [("src/x.py", 100, "Python", 8)]
    _mock_db(monkeypatch, rows)
    key_metrics.analyze_project_from_db(project_id=42)
    out = capsys.readouterr().out
    assert "Key Metrics" in out and "Python" in out
