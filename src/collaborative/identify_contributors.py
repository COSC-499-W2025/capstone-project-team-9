# identify_contributors.py
import os
import zipfile
import subprocess
import tempfile
import subprocess
from collections import defaultdict
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
    
    def get_line_changes(self) -> dict[str, dict[str, int]]:
        """
        Returns a dictionary of each author and the total lines they added and deleted.
        Example:
            {
                "Alice": {"added": 120, "deleted": 10, "cumulative": 110},
                "Bob": {"added": 50, "deleted": 5, "cumulative": 45}
            }
        Must call extract_repo() first.
        """
        if not self.repo_dir:
            raise ValueError("Repository not extracted. Call extract_repo() first.")
        # Use git log with numstat to get added/deleted lines per commit
        result = subprocess.run(
            ["git", "-C", self.repo_dir, "log", "--pretty=format:%an", "--numstat"],
            capture_output=True,
            text=True,
            check=True
        )
        lines_by_author = defaultdict(lambda: {"added": 0, "deleted": 0, "cumulative": 0})
        current_author = None
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            # If the line is not a number tab number tab filename, it's the author line
            if line.isalpha() or " " in line and not line[0].isdigit():
                current_author = line
                continue
            # Parse added/deleted numbers
            try:
                added_str, deleted_str, _ = line.split("\t")
                added = int(added_str) if added_str != "-" else 0
                deleted = int(deleted_str) if deleted_str != "-" else 0
                if current_author:
                    lines_by_author[current_author]["added"] += added
                    lines_by_author[current_author]["deleted"] += deleted
                    lines_by_author[current_author]["cumulative"] += (added-deleted)
            except ValueError:
                # Skip lines that don't match expected format
                continue
        return dict(lines_by_author)

    def get_file_contributions(self) -> dict[str, dict[str, dict]]:
        """
        Returns a dictionary mapping each author to their file contributions.
        Each author has 'created', 'modified', and 'deleted' entries, each containing:
            - 'count': number of unique files touched
            - 'files': set of unique file names
        Example output:
            {
                "Alice": {
                    "created": {"count": 2, "files": {"file1.py", "file2.txt"}},
                    "modified": {"count": 1, "files": {"file3.py"}},
                    "deleted": {"count": 1, "files": {"old_file.txt"}}
                },
                "Bob": {
                    "created": {"count": 0, "files": set()},
                    "modified": {"count": 1, "files": {"file4.py"}},
                    "deleted": {"count": 0, "files": set()}
                }
            }
        Must call extract_repo() first.
        """
        if not self.repo_dir:
            raise ValueError("Repository not extracted. Call extract_repo() first.")
        # Dictionary per author: each value is a dict with sets for created/modified/deleted
        file_sets = defaultdict(lambda: {"created": set(), "modified": set(), "deleted": set()})
        # Git log with name-status
        result = subprocess.run(
            ["git", "-C", self.repo_dir, "log", "--name-status", "--pretty=format:%an"],
            capture_output=True,
            text=True,
            check=True
        )
        current_author = None
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if "\t" not in line:
                current_author = line
                continue
            if current_author is None:
                continue
            status, file_path = line.split("\t", 1)
            status = status.upper()
            if status == "A":
                file_sets[current_author]["created"].add(file_path)
            elif status == "M":
                file_sets[current_author]["modified"].add(file_path)
            elif status == "D":
                file_sets[current_author]["deleted"].add(file_path)
        # Build final dictionary with counts
        file_contribs = {}
        for author, changes in file_sets.items():
            file_contribs[author] = {
                "created": {"count": len(changes["created"]), "files": changes["created"]},
                "modified": {"count": len(changes["modified"]), "files": changes["modified"]},
                "deleted": {"count": len(changes["deleted"]), "files": changes["deleted"]},
            }
        return file_contribs

    def cleanup(self):
        """
        Clean up the temporary extracted files.
        """
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()
