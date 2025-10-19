import os

class WrongFormatError(Exception):
    """Raised when a file is not a valid ZIP."""
    pass

MAX_BYTES = 200 * 1024 * 1024  # 200 MB default limit

def _assert_zip(path: str, content: bytes) -> None:
    """
    Validate that the file is a ZIP:
      - has .zip extension
      - has ZIP magic header "PK\x03\x04"
    """
    if not path.lower().endswith(".zip"):
        raise WrongFormatError("Only .zip files are accepted.")
    if not content.startswith(b"PK\x03\x04"):
        raise WrongFormatError("File is not a valid ZIP (bad magic header).")

def load_zip_bytes(path: str) -> bytes:
    """
    Read a ZIP file from disk with size and signature validation.
    Raises:
        FileNotFoundError, WrongFormatError
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise WrongFormatError(
            f"ZIP too large ({size} bytes). Limit is {MAX_BYTES} bytes."
        )

    with open(path, "rb") as f:
        data = f.read()

    _assert_zip(path, data)
    return data
