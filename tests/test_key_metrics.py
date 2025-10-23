from unittest.mock import patch
from src.analysis.key_metrics import read_zip, print_summary

def test_read_zip(tmp_path):
    # create a dummy zip file
    import zipfile, os
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("src/test.py", "print('hi')")
        z.writestr("docs/readme.md", "info")
    files, sizes = read_zip(zip_path)
    assert "src/test.py" in files
    assert "docs/readme.md" in files
    assert sizes["src/test.py"] > 0

def test_print_summary(capsys):
    agg = {
        "code": {"count": 1, "bytes": 120, "score": 5.2},
        "doc": {"count": 2, "bytes": 300, "score": 3.5}
    }
    print_summary("demo.zip", agg)
    out = capsys.readouterr().out
    assert "demo.zip" in out
    assert "code" in out
