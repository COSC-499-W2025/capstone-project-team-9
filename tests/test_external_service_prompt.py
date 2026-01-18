"""
Pytest tests for ExternalServicePrompt and request_external_service_permission.

Covers:
- Storing permissions successfully and on DB error
- Short-circuit behavior when permission already exists (True / False)
- Full workflow when permission is not set (info + prompt + store)
- Force re-prompting when permission exists but force=True

Run with: $env:PYTHONPATH="."; pytest tests/test_external_service_prompt.py -vv
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

from external_services import external_service_prompt as esp


class DummyCursor:
    """Simple fake DB cursor that records executed SQL for assertions."""

    def __init__(self):
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))


class DummyCursorContext:
    """Context manager that returns a DummyCursor."""

    def __init__(self):
        self.cursor = DummyCursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        # No special handling; just allow context to exit normally
        return False


# Tests for ExternalServicePrompt.store_permission

def test_store_permission_success(monkeypatch, capfd):
    """store_permission should return True when DB operation succeeds."""

    def fake_with_db_cursor():
        # Simulate a working DB cursor context manager
        return DummyCursorContext()

    # Patch the with_db_cursor used inside store_permission
    monkeypatch.setattr("config.db_config.with_db_cursor", fake_with_db_cursor)

    result = esp.ExternalServicePrompt.store_permission(
        user_name="user1", service_name="LLM", permission_granted=True
    )

    out, _ = capfd.readouterr()
    # We don't expect an error message in the normal case
    assert "Error storing permission" not in out
    assert result is True


def test_store_permission_db_error(monkeypatch, capfd):
    """store_permission should catch DB errors and return False."""

    def broken_with_db_cursor():
        # Simulate an exception when trying to get a DB cursor
        raise RuntimeError("DB connection failed")

    monkeypatch.setattr("config.db_config.with_db_cursor", broken_with_db_cursor)

    result = esp.ExternalServicePrompt.store_permission(
        user_name="user2", service_name="LLM", permission_granted=False
    )

    out, _ = capfd.readouterr()
    assert "Error storing permission" in out
    assert result is False


# Tests for request_external_service_permission

class FakePermissionBase:
    """Base fake for ExternalServicePermission; just records calls."""

    def __init__(self, user_name):
        self.user_name = user_name
        self.called_with_service = []

    def has_permission(self, service_name):
        self.called_with_service.append(service_name)
        return None


class FakePermissionTrue(FakePermissionBase):
    def has_permission(self, service_name):
        self.called_with_service.append(service_name)
        return True


class FakePermissionFalse(FakePermissionBase):
    def has_permission(self, service_name):
        self.called_with_service.append(service_name)
        return False


class FakePermissionNone(FakePermissionBase):
    def has_permission(self, service_name):
        self.called_with_service.append(service_name)
        return None



class FakeServiceConfig:
    """Fake ServiceConfig that just records initialize_table calls."""

    def __init__(self):
        self.initialized = False

    def initialize_table(self):
        self.initialized = True


def test_request_permission_existing_true_not_forced(monkeypatch, capfd):
    """
    If an existing permission is True and force=False,
    request_external_service_permission should:
    - NOT call info / prompt / store
    - Return True directly
    """

    # Patch ServiceConfig so it doesn't touch the real DB
    monkeypatch.setattr(esp, "ServiceConfig", FakeServiceConfig)

    # Patch ExternalServicePermission to always return True
    monkeypatch.setattr(esp, "ExternalServicePermission", FakePermissionTrue)

    flags = {"info": False, "prompt": False, "store": False}

    def fake_show_info():
        flags["info"] = True

    def fake_prompt(service_name="LLM"):
        flags["prompt"] = True
        return True

    def fake_store(user_name, service_name, permission_granted):
        flags["store"] = True
        return True

    monkeypatch.setattr(esp.ExternalServicePrompt, "show_external_service_info", staticmethod(fake_show_info))
    monkeypatch.setattr(esp.ExternalServicePrompt, "prompt_for_permission", staticmethod(fake_prompt))
    monkeypatch.setattr(esp.ExternalServicePrompt, "store_permission", staticmethod(fake_store))

    result = esp.request_external_service_permission(
        user_name="u_existing_true", service_name="LLM", force=False
    )

    out, _ = capfd.readouterr()
    assert "Using enhanced analysis" in out
    assert result is True

    # Ensure we short-circuited (no extra interactions)
    assert flags["info"] is False
    assert flags["prompt"] is False
    assert flags["store"] is False


def test_request_permission_existing_false_not_forced(monkeypatch, capfd):
    """
    If an existing permission is False and force=False,
    request_external_service_permission should:
    - NOT call info / prompt / store
    - Return False directly
    """

    monkeypatch.setattr(esp, "ServiceConfig", FakeServiceConfig)
    monkeypatch.setattr(esp, "ExternalServicePermission", FakePermissionFalse)

    flags = {"info": False, "prompt": False, "store": False}

    def fake_show_info():
        flags["info"] = True

    def fake_prompt(service_name="LLM"):
        flags["prompt"] = True
        return False

    def fake_store(user_name, service_name, permission_granted):
        flags["store"] = True
        return True

    monkeypatch.setattr(esp.ExternalServicePrompt, "show_external_service_info", staticmethod(fake_show_info))
    monkeypatch.setattr(esp.ExternalServicePrompt, "prompt_for_permission", staticmethod(fake_prompt))
    monkeypatch.setattr(esp.ExternalServicePrompt, "store_permission", staticmethod(fake_store))

    result = esp.request_external_service_permission(
        user_name="u_existing_false", service_name="LLM", force=False
    )

    out, _ = capfd.readouterr()
    assert "Using local analysis only" in out
    assert result is False

    assert flags["info"] is False
    assert flags["prompt"] is False
    assert flags["store"] is False


def test_request_permission_no_existing_runs_full_flow(monkeypatch):
    """
    If no existing permission (has_permission returns None),
    the function should:
    - call show_external_service_info
    - call prompt_for_permission
    - call store_permission with the chosen value
    - return the same value as prompt_for_permission
    """

    monkeypatch.setattr(esp, "ServiceConfig", FakeServiceConfig)
    monkeypatch.setattr(esp, "ExternalServicePermission", FakePermissionNone)

    flags = {"info": False, "prompt": False, "store": False}
    stored_calls = []

    def fake_show_info():
        flags["info"] = True

    def fake_prompt(service_name="LLM"):
        flags["prompt"] = True
        return True  # Simulate user granting permission

    def fake_store(user_name, service_name, permission_granted):
        flags["store"] = True
        stored_calls.append((user_name, service_name, permission_granted))
        return True

    monkeypatch.setattr(esp.ExternalServicePrompt, "show_external_service_info", staticmethod(fake_show_info))
    monkeypatch.setattr(esp.ExternalServicePrompt, "prompt_for_permission", staticmethod(fake_prompt))
    monkeypatch.setattr(esp.ExternalServicePrompt, "store_permission", staticmethod(fake_store))

    result = esp.request_external_service_permission(
        user_name="u_none", service_name="LLM", force=False
    )

    assert result is True
    assert flags["info"] is True
    assert flags["prompt"] is True
    assert flags["store"] is True

    # Check that store_permission was called with the expected values
    assert stored_calls == [("u_none", "LLM", True)]


def test_request_permission_existing_true_force_reprompts(monkeypatch):
    """
    When force=True, even if permission exists,
    the function should re-run the info + prompt + store flow.
    """

    monkeypatch.setattr(esp, "ServiceConfig", FakeServiceConfig)
    monkeypatch.setattr(esp, "ExternalServicePermission", FakePermissionTrue)

    flags = {"info": False, "prompt": False, "store": False}
    stored_calls = []

    def fake_show_info():
        flags["info"] = True

    def fake_prompt(service_name="LLM"):
        flags["prompt"] = True
        return False  # User now declines

    def fake_store(user_name, service_name, permission_granted):
        flags["store"] = True
        stored_calls.append((user_name, service_name, permission_granted))
        return True

    monkeypatch.setattr(esp.ExternalServicePrompt, "show_external_service_info", staticmethod(fake_show_info))
    monkeypatch.setattr(esp.ExternalServicePrompt, "prompt_for_permission", staticmethod(fake_prompt))
    monkeypatch.setattr(esp.ExternalServicePrompt, "store_permission", staticmethod(fake_store))

    result = esp.request_external_service_permission(
        user_name="u_force", service_name="LLM", force=True
    )

    # Even though existing permission was True, we forced a new choice (False)
    assert result is False
    assert flags["info"] is True
    assert flags["prompt"] is True
    assert flags["store"] is True
    assert stored_calls == [("u_force", "LLM", False)]
