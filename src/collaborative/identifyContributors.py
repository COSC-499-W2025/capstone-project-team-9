import os
import zipfile
import subprocess
import tempfile
from collections import Counter

# Path to your repo ZIP file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_PATH = os.path.join(SCRIPT_DIR, "../../test.zip")

# Create a temporary directory to extract into
with tempfile.TemporaryDirectory() as temp_dir:
    print(f"Extracting to {temp_dir} ...")
    # Extract all contents
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall(temp_dir)
    # Find the extracted repository folder (assuming only one top-level dir)
    subdirs = [os.path.join(temp_dir, d) for d in os.listdir(temp_dir)]
    repo_dir = next((d for d in subdirs if os.path.isdir(os.path.join(d, ".git"))), None)
    if not repo_dir:
        print("No .git folder found. This ZIP doesn’t contain Git history.")
    else:
        print(f"Found .git folder in: {repo_dir}") 
        # Run git log to get author names
        try:
            result = subprocess.run(
                ["git", "-C", repo_dir, "log", "--pretty=format:%an"],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print("Error running git:", e)
            exit(1)
        # Count commits per author
        authors = result.stdout.splitlines()
        counts = Counter(authors)
        print("\n Commit count per contributor:")
        for author, count in counts.most_common():
            print(f"{author}: {count} commits")
