# tests/test_contributor_helpers.py
import builtins
from typing import Dict, Set

import pytest

import analysis.key_metrics as key_metrics


# --- Tests for choose_author_from_zip ----------------------------------------


def test_choose_author_from_zip_no_authors(monkeypatch):
    """If _identify_authors_from_zip returns empty, we should get None and no input is requested."""

    # _identify_authors_from_zip -> empty set
    monkeypatch.setattr(
        "analysis.key_metrics.get_project_contributor_name",
        lambda uploaded_file_id: None,
    )
    monkeypatch.setattr(
        "analysis.key_metrics._identify_authors_from_zip",
        lambda uploaded_file_id: set(),
    )
    monkeypatch.setattr(
        "analysis.key_metrics.get_file_contents_by_upload_id",
        lambda uploaded_file_id: {},
    )
    monkeypatch.setattr(
        "analysis.key_metrics._extract_common_names_from_filenames",
        lambda file_contents: set(),
    )

    # Don't need to patch input; function should never call it
    result = key_metrics.choose_author_from_zip(uploaded_file_id=1)
    assert result is None


def test_choose_author_from_zip_select_specific_author(monkeypatch):
    """User selects a specific author (e.g., option 2)."""

    # Return 2 authors; after sorting: ["Alice", "Bob"]
    monkeypatch.setattr(
        "analysis.key_metrics.get_project_contributor_name",
        lambda uploaded_file_id: None,
    )
    monkeypatch.setattr(
        "analysis.key_metrics._identify_authors_from_zip",
        lambda uploaded_file_id: {"Bob", "Alice"},
    )
    monkeypatch.setattr(
        "analysis.key_metrics.get_file_contents_by_upload_id",
        lambda uploaded_file_id: {},
    )
    monkeypatch.setattr(
        "analysis.key_metrics._extract_common_names_from_filenames",
        lambda file_contents: set(),
    )
    monkeypatch.setattr(
        "analysis.key_metrics.get_user_git_username",
        lambda: None,
    )
    monkeypatch.setattr(
        "analysis.key_metrics.set_project_contributor_name",
        lambda *_args, **_kwargs: True,
    )

    # Simulate user typing "2" (select "Bob")
    monkeypatch.setattr("builtins.input", lambda prompt: "2")

    result = key_metrics.choose_author_from_zip(uploaded_file_id=1)
    assert result == "Bob"


def test_choose_author_from_zip_not_collaborative(monkeypatch):
    """User selects the 'Not a collaborative project' option."""

    # Return 2 authors; menu will show 3rd option as 'Not a collaborative project'
    monkeypatch.setattr(
        "analysis.key_metrics.get_project_contributor_name",
        lambda uploaded_file_id: None,
    )
    monkeypatch.setattr(
        "analysis.key_metrics._identify_authors_from_zip",
        lambda uploaded_file_id: {"Bob", "Alice"},
    )
    monkeypatch.setattr(
        "analysis.key_metrics.get_file_contents_by_upload_id",
        lambda uploaded_file_id: {},
    )
    monkeypatch.setattr(
        "analysis.key_metrics._extract_common_names_from_filenames",
        lambda file_contents: set(),
    )
    monkeypatch.setattr(
        "analysis.key_metrics.get_user_git_username",
        lambda: None,
    )

    # Simulate user typing "3" (len(authors) + 1)
    monkeypatch.setattr("builtins.input", lambda prompt: "3")

    result = key_metrics.choose_author_from_zip(uploaded_file_id=1)
    # Our implementation returns None for non-collaborative
    assert result is None


# --- Helpers for get_author_file_contributions_from_zip tests ----------------


class FakeIdentifyContributors:
    """
    Minimal fake for identify_contributors used in tests.
    """

    def __init__(self, zip_bytes: bytes):
        self.zip_bytes = zip_bytes
        self.cleaned = False

    def extract_repo(self) -> str | None:
        # Simulate finding a valid repo directory
        return "/tmp/fakerepo"

    def get_file_contributions(self) -> Dict[str, Dict[str, Dict]]:
        # Simulated contributions for multiple authors
        return {
            "Alice": {
                "created": {"count": 1, "files": {"src/a.py"}},
                "modified": {"count": 1, "files": {"src/shared.py"}},
                "deleted": {"count": 0, "files": set()},
            },
            "bob": {  # note lowercase key (to test case-insensitive matching)
                "created": {"count": 1, "files": {"src/b.py"}},
                "modified": {"count": 0, "files": set()},
                "deleted": {"count": 1, "files": {"old/legacy.py"}},
            },
        }

    def cleanup(self):
        self.cleaned = True


# --- Tests for get_author_file_contributions_from_zip ------------------------


def test_get_author_file_contributions_bad_project_id():
    """Project ID <= 0 should immediately return empty sets."""
    result = key_metrics.get_author_file_contributions_from_zip(project_id=0, author_name="Alice")
    assert result == {"created": set(), "modified": set(), "deleted": set()}


def test_get_author_file_contributions_no_zip(monkeypatch):
    """If get_zip_file returns no data, we should get empty sets."""

    monkeypatch.setattr(
        "analysis.key_metrics.get_zip_file",
        lambda project_id: None,
    )

    result = key_metrics.get_author_file_contributions_from_zip(project_id=1, author_name="Alice")
    assert result == {"created": set(), "modified": set(), "deleted": set()}


def test_get_author_file_contributions_exact_match(monkeypatch):
    """Exact author name match should return that author's files."""

    # Simulate a valid zip blob
    monkeypatch.setattr(
        "analysis.key_metrics.get_zip_file",
        lambda project_id: b"fakezipbytes",
    )

    # Patch identify_contributors constructor to return our fake
    monkeypatch.setattr(
        "analysis.key_metrics.identify_contributors",
        FakeIdentifyContributors,
    )

    result = key_metrics.get_author_file_contributions_from_zip(project_id=1, author_name="Alice")

    assert result["created"] == {"src/a.py"}
    assert result["modified"] == {"src/shared.py"}
    assert result["deleted"] == set()


def test_get_author_file_contributions_case_insensitive(monkeypatch):
    """Author name lookup should be case-insensitive if exact key not found."""

    monkeypatch.setattr(
        "analysis.key_metrics.get_zip_file",
        lambda project_id: b"fakezipbytes",
    )
    monkeypatch.setattr(
        "analysis.key_metrics.identify_contributors",
        FakeIdentifyContributors,
    )

    # In FakeIdentifyContributors, we have "bob" as a key; here we ask for "Bob"
    result = key_metrics.get_author_file_contributions_from_zip(project_id=1, author_name="Bob")

    assert result["created"] == {"src/b.py"}
    assert result["modified"] == set()
    assert result["deleted"] == {"old/legacy.py"}


def test_get_author_file_contributions_author_not_found(monkeypatch):
    """Unknown author should yield empty sets."""

    monkeypatch.setattr(
        "analysis.key_metrics.get_zip_file",
        lambda project_id: b"fakezipbytes",
    )
    monkeypatch.setattr(
        "analysis.key_metrics.identify_contributors",
        FakeIdentifyContributors,
    )

    result = key_metrics.get_author_file_contributions_from_zip(project_id=1, author_name="Charlie")

    assert result == {"created": set(), "modified": set(), "deleted": set()}


# --- Tests for get_all_files_for_author_from_zip -----------------------------


def test_get_all_files_for_author_from_zip_union(monkeypatch):
    """get_all_files_for_author_from_zip should return the union of created, modified, deleted."""

    # Directly monkeypatch the helper to isolate this test
    def fake_get_author_file_contributions_from_zip(project_id: int, author_name: str) -> Dict[str, Set[str]]:
        return {
            "created": {"src/a.py"},
            "modified": {"src/b.py"},
            "deleted": {"old/c.py"},
        }

    monkeypatch.setattr(
        "analysis.key_metrics.get_author_file_contributions_from_zip",
        fake_get_author_file_contributions_from_zip,
    )

    all_files = key_metrics.get_all_files_for_author_from_zip(project_id=1, author_name="Alice")
    assert all_files == {"src/a.py", "src/b.py", "old/c.py"}
