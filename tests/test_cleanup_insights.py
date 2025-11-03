from src.tools.cleanup_insights import delete_insights

class _FakeCursor:
    def __init__(self):
        self._calls = []
        self.rowcount = 0
        self._last_sql = ""
    # support with ... as ...
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

    def execute(self, sql, params=None):
        sql_strip = sql.strip()
        self._last_sql = sql_strip
        self._calls.append((sql_strip, tuple(params or ())))

        # simulate rowcount for delete statements
        if "FROM project_metrics" in sql_strip:
            self.rowcount = 3
        elif "FROM file_contents" in sql_strip:
            self.rowcount = 5
        elif "FROM uploaded_files" in sql_strip:
            self.rowcount = 1
        else:
            self.rowcount = 0

    def fetchone(self):
        # Called by _table_exists: returns non-None whenever information_schema is queried.
        if "information_schema.tables" in self._last_sql:
            return (1,)
        return None

    def close(self):
        pass


class _FakeConn:
    def __init__(self):
        self.cur = _FakeCursor()
    # with get_connection() as conn need to return a context-supporting connection
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass
    # with conn.cursor() as cur need to return a context-supporting cursor
    def cursor(self):
        return self.cur
    def commit(self):
        pass
    def close(self):
        pass


def test_delete_insights(monkeypatch):
    from src.tools import cleanup_insights as ci
    monkeypatch.setattr(ci, "get_connection", lambda: _FakeConn())

    metrics, files, projects = delete_insights(42)

    assert metrics == 3
    assert files == 5
    assert projects == 1
