# src/parsing/file_validator.py
import os
import zipfile

class WrongFormatError(Exception):
    """Raised when uploaded file is not a valid ZIP file."""
    pass

ALLOWED_EXTENSIONS = [".zip"]

def validate_uploaded_file(file_path: str) -> None:
    """
    Validate uploaded file format.
    - Check if extension is .zip
    - Check if file is a valid ZIP archive
    Raises WrongFormatError if invalid.
    """
    # Check file extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise WrongFormatError(f"Invalid extension: {ext}. Must be one of {ALLOWED_EXTENSIONS}")

    # Check if file is a valid ZIP archive
    if not zipfile.is_zipfile(file_path):
        raise WrongFormatError("The uploaded file is not a valid ZIP archive.")
