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

def test_get_commit_counts_without_extract(temp_git_zip):
    ic = identify_contributors(str(temp_git_zip))
    with pytest.raises(ValueError, match="Repository not extracted"):
        ic.get_commit_counts()
