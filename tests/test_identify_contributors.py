#test_identify_contributor.py
import os
import sys
import pytest
import zipfile
import subprocess
import shutil
from collections import Counter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/collaborative")))
from identify_contributors import extract_repo, get_commit_counts

@pytest.fixture
def temp_repo(tmp_path):
    """
    Create a real git repository, commit a file, zip it, and provide a folder for extraction.
    """
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    # Initialize a real git repo
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)

    # Add a dummy file and commit
    file_path = repo_dir / "file.txt"
    file_path.write_text("hello")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=repo_dir, check=True)

    # Create a ZIP of the repo
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for root, dirs, files in os.walk(repo_dir):
            for f in files:
                file_full = os.path.join(root, f)
                # Store relative paths in the ZIP
                z.write(file_full, arcname=os.path.relpath(file_full, tmp_path))

    # Provide a folder for extraction
    extract_dir = tmp_path / "extracted"
    extract_dir.mkdir()
    return zip_path, extract_dir

def test_extract_repo(temp_repo):
    zip_path, extract_dir = temp_repo

    # Extract the ZIP into the pytest-managed folder
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)

    # Find the extracted repo directory (it should contain a .git folder)
    repo_dir = next(
        (d for d in extract_dir.iterdir() if (d / ".git").is_dir()),
        None
    )

    assert repo_dir is not None
    assert (repo_dir / ".git").is_dir()

@pytest.mark.skipif(
    not shutil.which("git"),
    reason="Git not available, skipping git tests"
)
def test_get_commit_counts(temp_repo):
    zip_path, extract_dir = temp_repo

    # Extract ZIP
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)

    # Find the extracted repo directory
    repo_dir = next(
        (d for d in extract_dir.iterdir() if (d / ".git").is_dir()),
        None
    )
    assert repo_dir is not None

    # Make a second commit to test multiple commits
    file_path = repo_dir / "file.txt"
    file_path.write_text("change")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "second commit"], cwd=repo_dir, check=True)

    # Get commit counts
    counts = get_commit_counts(repo_dir)
    assert isinstance(counts, Counter)
    assert counts["Test User"] == 2