import os
import tempfile
import shutil
import pytest
from src.parsing.file_lister import list_files

@pytest.fixture
def temp_test_dir():
    # create folders
    test_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(test_dir, "folderA/folderB"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "folderC"), exist_ok=True)
    # creat file in folders
    with open(os.path.join(test_dir, "root.txt"), "w") as f:
        f.write("root")
    with open(os.path.join(test_dir,"folderA","A1.txt"), "w") as f:
        f.write("A1")
    with open(os.path.join(test_dir,"folderA","folderB","B1.txt"), "w") as f:
        f.write("B1")
    with open(os.path.join(test_dir,"folderC","C1.txt"), "w") as f:
        f.write("C1")

    yield test_dir
    # delete dir after test
    shutil.rmtree(test_dir)