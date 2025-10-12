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

def test_list_files(temp_test_dir):
    """
    Verify that list_files() correctly recursively lists all files and folders
    """
    result = list_files(temp_test_dir)

    # check data type
    assert isinstance(result, list)

    # expect result
    expected = [
        "[DIR] folderA",
        "  A1.txt",
        "  [DIR] folderB",
        "    B1.txt",
        "[DIR] folderC",
        "  C1.txt",
        "root.txt",
    ]

    # normalize the expected and result
    norm_expected = [line.rstrip() for line in expected]
    norm_result = [line.rstrip() for line in result]

    # simplify test
    assert norm_expected == norm_result

    # # check content in result
    # for item in norm_expected:
    #     assert item in norm_result, "{} not in {}".format(item, norm_result)
    #
    # # check number of levels
    # lines = [line for line in result if line.startswith("[DIR]")]
    # assert len(lines)==2, "expected 2 folders (folderA, folderB)"