#identify_contributors.py
import os
import zipfile
import subprocess
import tempfile
from collections import Counter

def extract_repo(zip_path):
    """Extract ZIP and return path to repo containing .git folder"""
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(temp_dir)
        
        subdirs = [os.path.join(temp_dir, d) for d in os.listdir(temp_dir)]
        repo_dir = next((d for d in subdirs if os.path.isdir(os.path.join(d, ".git"))), None)
        if repo_dir is None:
            return None
        return repo_dir  # Note: temp_dir will be deleted after context ends

def get_commit_counts(repo_dir):
    """Return a Counter of commit authors"""
    result = subprocess.run(
        ["git", "-C", repo_dir, "log", "--pretty=format:%an"],
        capture_output=True,
        text=True,
        check=True
    )
    authors = result.stdout.splitlines()
    return Counter(authors)

