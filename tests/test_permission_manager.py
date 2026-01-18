"""
Pytest tests for ServiceConfig and ExternalServicePermission.

Covers:
- ServiceConfig.initialize_table success and exception branches
- ServiceConfig.get_permission for True / False / None and error cases
- ExternalServicePermission.initialize success/failure
- ExternalServicePermission.has_permission behavior

Run with: $env:PYTHONPATH="."; pytest tests/test_permission_manager.py -vv
"""

import os
import sys
import pytest

# Add src directory to Python path (same pattern as other tests)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from external_services.service_config import ServiceConfig
from external_services.permission_manager import ExternalServicePermission


# Fakes for DB cursor / context

class DummyCursor:
    """Fake DB cursor that can be configured with a fetchone result."""

    def __init__(self, fetchone_result=None):
        self.fetchone_result = fetchone_result
        self.executed = []

    def execute(self, sql, params=None):
        # Just record the calls, no real DB
        self.executed.append((sql, params))

    def fetchone(self):
        return self.fetchone_result


class DummyCursorContext:
    """Context manager returning a DummyCursor."""

    def __init__(self, fetchone_result=None):
        self.cursor = DummyCursor(fetchone_result=fetchone_result)

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


# Tests for ServiceConfig.initialize_table

def test_initialize_table_success(monkeypatch, capfd):
    """initialize_table prints success message when DB operations succeed."""

    def fake_with_db_cursor():
        # Return a context manager with a dummy cursor
        return DummyCursorContext()

    monkeypatch.setattr("external_services.service_config.with_db_cursor", fake_with_db_cursor)

    ServiceConfig.initialize_table()

    out, _ = capfd.readouterr()
    assert "External service permissions table initialized" in out


def test_initialize_table_connection_error(monkeypatch):
    """initialize_table wraps ConnectionError as a generic Exception."""

    def raise_conn_error():
        raise ConnectionError("DB down")

    monkeypatch.setattr("external_services.service_config.with_db_cursor", raise_conn_error)

    with pytest.raises(Exception) as excinfo:
        ServiceConfig.initialize_table()

    assert "Failed to connect to database" in str(excinfo.value)


def test_initialize_table_other_error(monkeypatch, capfd):
    """initialize_table prints error and re-raises for generic exceptions."""

    def raise_other_error():
        raise RuntimeError("Some DB error")

    monkeypatch.setattr("external_services.service_config.with_db_cursor", raise_other_error)

    with pytest.raises(Exception):
        ServiceConfig.initialize_table()

    out, _ = capfd.readouterr()
    assert "Error initializing external service permissions table" in out


# Tests for ServiceConfig.get_permission

def test_get_permission_returns_true(monkeypatch):
    """get_permission should return True when DB row has permission_granted=True."""

    def fake_with_db_cursor():
        return DummyCursorContext(fetchone_result=(True,))

    monkeypatch.setattr("external_services.service_config.with_db_cursor", fake_with_db_cursor)

    result = ServiceConfig.get_permission("user1", "LLM")
    assert result is True


def test_get_permission_returns_false(monkeypatch):
    """get_permission should return False when DB row has permission_granted=False."""

    def fake_with_db_cursor():
        return DummyCursorContext(fetchone_result=(False,))

    monkeypatch.setattr("external_services.service_config.with_db_cursor", fake_with_db_cursor)

    result = ServiceConfig.get_permission("user2", "LLM")
    assert result is False


def test_get_permission_returns_none_when_no_record(monkeypatch):
    """get_permission returns None when no record is found."""

    def fake_with_db_cursor():
        # fetchone() will return None
        return DummyCursorContext(fetchone_result=None)

    monkeypatch.setattr("external_services.service_config.with_db_cursor", fake_with_db_cursor)

    result = ServiceConfig.get_permission("user3", "LLM")
    assert result is None


def test_get_permission_connection_error(monkeypatch):
    """get_permission returns None on ConnectionError."""

    def raise_conn_error():
        raise ConnectionError("DB down")

    monkeypatch.setattr("external_services.service_config.with_db_cursor", raise_conn_error)

    result = ServiceConfig.get_permission("user4", "LLM")
    assert result is None


def test_get_permission_other_error(monkeypatch):
    """get_permission returns None on generic exception."""

    def raise_other_error():
        raise RuntimeError("Some DB error")

    monkeypatch.setattr("external_services.service_config.with_db_cursor", raise_other_error)

    result = ServiceConfig.get_permission("user5", "LLM")
    assert result is None


# Tests for ExternalServicePermission

class FakeServiceConfigOK:
    """Fake ServiceConfig with successful initialize_table and configurable get_permission."""

    def __init__(self, permission=None):
        self.permission = permission
        self.initialized = False

    def initialize_table(self):
        self.initialized = True

    def get_permission(self, user_name, service_name):
        return self.permission


class FakeServiceConfigFail:
    """Fake ServiceConfig whose initialize_table always fails."""

    def initialize_table(self):
        raise RuntimeError("init failed")

    def get_permission(self, user_name, service_name):
        return None


def test_external_permission_initialize_success(monkeypatch):
    """ExternalServicePermission.initialize returns True when initialize_table succeeds."""

    fake_config = FakeServiceConfigOK()
    # Patch the ServiceConfig used inside permission_manager
    monkeypatch.setattr(
        "external_services.permission_manager.ServiceConfig",
        lambda: fake_config
    )

    mgr = ExternalServicePermission(user_name="u_init_ok")
    result = mgr.initialize()

    assert result is True
    assert fake_config.initialized is True


def test_external_permission_initialize_failure(monkeypatch, capfd):
    """ExternalServicePermission.initialize returns False and prints error on failure."""

    fake_config = FakeServiceConfigFail()
    monkeypatch.setattr(
        "external_services.permission_manager.ServiceConfig",
        lambda: fake_config
    )

    mgr = ExternalServicePermission(user_name="u_init_fail")
    result = mgr.initialize()

    out, _ = capfd.readouterr()
    assert result is False
    assert "Failed to initialize external service permissions" in out


@pytest.mark.parametrize(
    "permission_value, expected",
    [
        (True, True),
        (False, False),
        (None, False),  # fallback when no record => False
    ],
)
def test_external_permission_has_permission(monkeypatch, permission_value, expected):
    """has_permission should delegate to ServiceConfig.get_permission and fallback None->False."""

    fake_config = FakeServiceConfigOK(permission=permission_value)

    monkeypatch.setattr(
        "external_services.permission_manager.ServiceConfig",
        lambda: fake_config
    )

    mgr = ExternalServicePermission(user_name="u_perm")
    result = mgr.has_permission(service_name="LLM")

    assert result is expected
