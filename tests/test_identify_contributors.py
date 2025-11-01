# test_identify_contributors.py
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/collaborative")))
import zipfile
import subprocess
import tempfile
import pytest
from collections import Counter
from pathlib import Path
from collections import defaultdict
from identify_contributors import identify_contributors

@pytest.fixture
def temp_git_zip(tmp_path):
    """
    Creates a temporary Git repository with multiple commits/authors, 
    zips it, and returns the path to the ZIP file.
    """
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    
    # Set default git user for initial commits
    subprocess.run(["git", "config", "user.name", "Alice"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "alice@example.com"], cwd=repo_dir, check=True)

    # Create initial file and commit
    (repo_dir / "file1.txt").write_text("Hello")
    subprocess.run(["git", "add", "file1.txt"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True)

    # Second commit by another author
    subprocess.run(["git", "config", "user.name", "Bob"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "bob@example.com"], cwd=repo_dir, check=True)
    (repo_dir / "file2.txt").write_text("World")
    subprocess.run(["git", "add", "file2.txt"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Second commit"], cwd=repo_dir, check=True)

    # Zip the repo
    zip_path = tmp_path / "repo.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for root, dirs, files in os.walk(repo_dir):
            for file in files:
                file_path = Path(root) / file
                zf.write(file_path, file_path.relative_to(repo_dir.parent))

    return zip_path

def test_extract_repo(temp_git_zip):
    ic = identify_contributors(str(temp_git_zip))
    repo_path = ic.extract_repo()
    assert repo_path is not None
    assert (Path(repo_path) / ".git").exists()
    ic.cleanup()

def test_get_commit_counts(temp_git_zip):
    ic = identify_contributors(str(temp_git_zip))
    ic.extract_repo()
    counts = ic.get_commit_counts()
    assert isinstance(counts, Counter)
    assert counts["Alice"] == 1
    assert counts["Bob"] == 1
    ic.cleanup()

def test_get_line_changes(temp_git_zip):
    ic = identify_contributors(str(temp_git_zip))
    ic.extract_repo()
    changes = ic.get_line_changes()
    # Check the type of the returned value
    assert isinstance(changes, dict)
    # Check that both authors are present
    assert "Alice" in changes
    assert "Bob" in changes
    # Check that added/deleted/cumulative keys exist
    for author, data in changes.items():
        assert set(data.keys()) == {"added", "deleted", "cumulative"}
    # Check actual numbers (based on our test repo setup)
    # Alice added "Hello" to file1.txt (5 characters -> counted as 1 line)
    # Bob added "World" to file2.txt (1 line)
    # Since no deletions, cumulative should equal added
    assert changes["Alice"]["added"] > 0
    assert changes["Alice"]["deleted"] == 0
    assert changes["Alice"]["cumulative"] == changes["Alice"]["added"]
    assert changes["Bob"]["added"] > 0
    assert changes["Bob"]["deleted"] == 0
    assert changes["Bob"]["cumulative"] == changes["Bob"]["added"]
    ic.cleanup()

def test_get_file_contributions(temp_git_zip):
    ic = identify_contributors(str(temp_git_zip))
    ic.extract_repo()
    contribs = ic.get_file_contributions()
    # Check type and that both authors exist
    assert isinstance(contribs, dict)
    assert "Alice" in contribs
    assert "Bob" in contribs
    # Check structure for each author
    for author, data in contribs.items():
        assert set(data.keys()) == {"created", "modified", "deleted"}
        for change_type, details in data.items():
            assert "count" in details
            assert "files" in details
            assert isinstance(details["files"], set)
            assert isinstance(details["count"], int)
            # Count matches the number of files
            assert details["count"] == len(details["files"])
    # Verify specific contributions for our test repo
    assert contribs["Alice"]["created"]["files"] == {"file1.txt"}
    assert contribs["Alice"]["modified"]["count"] == 0
    assert contribs["Alice"]["deleted"]["count"] == 0
    assert contribs["Bob"]["created"]["files"] == {"file2.txt"}
    assert contribs["Bob"]["modified"]["count"] == 0
    assert contribs["Bob"]["deleted"]["count"] == 0
    ic.cleanup()

def test_get_full_contribution_profile(temp_git_zip):
    ic = identify_contributors(str(temp_git_zip))
    ic.extract_repo()
    
    profile = ic.get_full_contribution_profile()
    
    # Basic structure checks
    assert isinstance(profile, dict)
    assert "Alice" in profile
    assert "Bob" in profile
    
    for author, data in profile.items():
        # Check top-level keys
        assert set(data.keys()) == {"commits", "lines", "files"}
        
        # Commits
        assert isinstance(data["commits"], int)
        assert data["commits"] > 0
        
        # Lines
        lines = data["lines"]
        assert set(lines.keys()) == {"added", "deleted", "cumulative"}
        assert lines["added"] >= 0
        assert lines["deleted"] >= 0
        assert lines["cumulative"] == lines["added"] - lines["deleted"]
        
        # Files
        files = data["files"]
        assert set(files.keys()) == {"created", "modified", "deleted"}
        for change_type, details in files.items():
            assert "count" in details and "files" in details
            assert isinstance(details["files"], set)
            assert details["count"] == len(details["files"])
    
    # Specific checks for our test repo
    assert profile["Alice"]["commits"] == 1
    assert profile["Bob"]["commits"] == 1
    
    assert profile["Alice"]["files"]["created"]["files"] == {"file1.txt"}
    assert profile["Bob"]["files"]["created"]["files"] == {"file2.txt"}
    
    # No modifications or deletions in the simple test repo
    for author in ["Alice", "Bob"]:
        assert profile[author]["files"]["modified"]["count"] == 0
        assert profile[author]["files"]["deleted"]["count"] == 0
    
    ic.cleanup()


def test_get_commit_counts_without_extract(temp_git_zip):
    ic = identify_contributors(str(temp_git_zip))
    with pytest.raises(ValueError, match="Repository not extracted"):
        ic.get_commit_counts()
