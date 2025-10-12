# tests/test_file_validator.py
import sys
import os
import pytest

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.parsing.file_validator import validate_uploaded_file, WrongFormatError

def test_invalid_extension(tmp_path):
    # Test that a non-zip extension raises WrongFormatError
    fake_txt = tmp_path / "test.txt"
    fake_txt.write_text("not a zip")
    with pytest.raises(WrongFormatError):
        validate_uploaded_file(str(fake_txt))

def test_invalid_zip_structure(tmp_path):
    # Test that a .zip file with invalid structure raises WrongFormatError
    fake_zip = tmp_path / "test.zip"
    fake_zip.write_text("this is not actually a zip")
    with pytest.raises(WrongFormatError):
        validate_uploaded_file(str(fake_zip))

def test_valid_zip(tmp_path):
    # Test that a proper zip archive passes validation
    import zipfile
    valid_zip = tmp_path / "valid.zip"
    with zipfile.ZipFile(valid_zip, 'w') as zf:
        zf.writestr("file.txt", "hello")

    # Should not raise any exception
    validate_uploaded_file(str(valid_zip))
