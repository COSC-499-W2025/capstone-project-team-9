import tempfile
import os
from io import StringIO, BytesIO
from typing import Optional, Union


class tempDataStore:
    """
    Generic temporary data store:
      - Store data either in memory or on disk (temporary file)
      - Text or binary mode
      - In file mode, the file is deleted when the stream is closed (incl. leaving a `with` block)
    """

    def __init__(self, use_memory: bool = True, binary: bool = False, encoding: str = "utf-8"):
        """
        Args:
            use_memory: True -> in-memory buffer; False -> temporary file on disk.
            binary: True -> binary mode (bytes); False -> text mode (str).
            encoding: Text encoding when in text mode (ignored in binary mode).
        """
        self.use_memory = use_memory
        self.binary = binary
        self.encoding = encoding

        self.buffer: Union[StringIO, BytesIO, "tempfile._TemporaryFileWrapper", None] = None
        self.file_path: Optional[str] = None
        self.closed: bool = False
        self._deleted: bool = False  # track deletion of the temp file

        if self.use_memory:
            self.buffer = BytesIO() if self.binary else StringIO()
        else:
            # delete=False so we can control deletion timing; we delete on close()
            mode = "w+b" if self.binary else "w+"
            tmp = tempfile.NamedTemporaryFile(mode=mode, delete=False, encoding=None if self.binary else self.encoding)
            self.buffer = tmp
            self.file_path = tmp.name

    def write(self, data: Union[str, bytes]) -> None:
        """Write data to the underlying buffer."""
        self._ensure_open()
        if self.binary:
            if isinstance(data, str):
                data = data.encode(self.encoding)
            elif not isinstance(data, (bytes, bytearray)):
                raise TypeError("Binary mode expects bytes-like data or str (which will be encoded).")
        else:
            if isinstance(data, (bytes, bytearray)):
                data = data.decode(self.encoding)
            elif not isinstance(data, str):
                raise TypeError("Text mode expects str or bytes-like (which will be decoded).")
        self.buffer.write(data)  # type: ignore[arg-type]
        self.buffer.flush() # make suer the data write into tempfile.

    def read(self) -> Union[str, bytes]:
        """Read all data from the underlying buffer from the beginning."""
        self._ensure_open()
        self.buffer.seek(0) # return to the start of the buffer to avoid read empty
        return self.buffer.read()

    def get_path(self) -> str:
        """
        Return the file path (file mode only) while the stream is open and the file exists.
        Raises RuntimeError if in memory mode, or if the file is closed/deleted.
        """
        if self.use_memory:
            raise RuntimeError("Memory mode: no file path available.")
        if self.closed or self._deleted or not (self.file_path and os.path.exists(self.file_path)):
            raise RuntimeError("The temporary file is not available (already closed/deleted).")
        return self.file_path  # type: ignore[return-value]

    def delete(self) -> bool:
        """
        Manually delete the temporary file (file mode only).
        Returns True if deletion happened; False otherwise (e.g., memory mode or already deleted).
        """
        if self.use_memory:
            return False
        if self._deleted:
            return False
        if self.file_path and os.path.exists(self.file_path):
            # Ensure file handle is closed before deletion on Windows
            if hasattr(self.buffer, "close"):
                try:
                    self.buffer.flush()
                except Exception:
                    pass
            try:
                os.remove(self.file_path)
                self._deleted = True
                return True
            finally:
                # do not nullify file_path so error messages can still reference it if needed
                ...
        return False

    def close(self) -> None:
        """
        Close the stream. If in file mode, also delete the temporary file.
        Safe to call multiple times.
        """
        if self.closed:
            return

        # Close the buffer/handle first (important on Windows)
        try:
            if self.buffer is not None:
                self.buffer.close()
        finally:
            self.closed = True

        # In file mode: delete the file on close
        if not self.use_memory and not self._deleted and self.file_path:
            try:
                if os.path.exists(self.file_path):
                    os.remove(self.file_path)
                self._deleted = True
            except FileNotFoundError:
                self._deleted = True

    # ===== context manager protocol =====
    def __enter__(self) -> "TempDataStore":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        # Always close (and thus delete the temp file in file mode)
        self.close()

    # ===== helpers =====
    def _ensure_open(self) -> None:
        """Raise if the buffer has been closed."""
        if self.closed:
            raise RuntimeError("The stream is closed.")
