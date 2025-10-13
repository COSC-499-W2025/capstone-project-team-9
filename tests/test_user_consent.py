import os
import sqlite3
import pytest
from src.database.user_consent import init_db, has_user_consented

def test_init_db_creates_table(tmp_path, monkeypatch):
    db_path = tmp_path / "test_users.db"
    monkeypatch.setattr("src.database.user_consent.DB_PATH", str(db_path))
    init_db()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_consent'")
    assert cursor.fetchone() is not None
    conn.close()

def test_has_user_consented_false_initially(tmp_path, monkeypatch):
    db_path = tmp_path / "test_users.db"
    monkeypatch.setattr("src.database.user_consent.DB_PATH", str(db_path))
    init_db()
    assert has_user_consented() is False
