# identify_contributors.py
import os
import zipfile
import subprocess
import tempfile
from collections import Counter

class identify_contributors:
    """
    Class to analyze a Git repository stored in a ZIP file.
    """

    def __init__(self, zip_path: str):
        """
        Initialize with the path to the ZIP file.
        """
        self.zip_path = zip_path
        self.repo_dir = None  # Will hold the path to the extracted repo

    def extract_repo(self) -> str | None:
        """
        Extract the ZIP and find the repository containing a .git folder.
        Returns the path to the repo or None if not found.
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(self.zip_path, "r") as z:
            z.extractall(self.temp_dir.name)

        # Look for a subdirectory containing .git
        subdirs = [os.path.join(self.temp_dir.name, d) for d in os.listdir(self.temp_dir.name)]
        self.repo_dir = next((d for d in subdirs if os.path.isdir(os.path.join(d, ".git"))), None)

        return self.repo_dir

    def get_commit_counts(self) -> Counter | None:
        """
        Returns a Counter of commits per author.
        Must call extract_repo() first.
        """
        if not self.repo_dir:
            raise ValueError("Repository not extracted. Call extract_repo() first.")

        result = subprocess.run(
            ["git", "-C", self.repo_dir, "log", "--pretty=format:%an"],
            capture_output=True,
            text=True,
            check=True
        )
        authors = result.stdout.splitlines()
        return Counter(authors)

    def cleanup(self):
        """
        Clean up the temporary extracted files.
        """
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()
