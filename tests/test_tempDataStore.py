import os
import io
import pytest
from src.parsing.tempDataStore import tempDataStore


# ---------- Basic Functionality Tests ----------

def test_memory_text_mode_write_and_read():
    """Test text mode in-memory storage."""
    store = tempDataStore(use_memory=True, binary=False)
    data = "Hello, world!"
    store.write(data)
    result = store.read()
    assert result == data
    store.close()
    assert store.closed


def test_memory_binary_mode_write_and_read():
    """Test binary mode in-memory storage."""
    store = tempDataStore(use_memory=True, binary=True)
    data = b"binary-data"
    store.write(data)
    result = store.read()
    assert result == data
    store.close()
    assert store.closed


# ---------- File Mode Tests ----------

def test_file_text_mode_write_read_and_delete(tmp_path):
    """Test text mode when using a temporary file."""
    store = tempDataStore(use_memory=False, binary=False)
    path = store.get_path()
    assert os.path.exists(path)

    store.write("sample text")
    content = store.read()
    assert "sample" in content

    # Manual deletion
    deleted = store.delete()
    assert deleted
    assert not os.path.exists(path)
    store.close()


def test_file_binary_mode_write_and_auto_delete():
    """Test binary mode and file deletion on close()."""
    store = tempDataStore(use_memory=False, binary=True)
    path = store.get_path()
    store.write(b"abc123")
    assert os.path.exists(path)
    store.close()
    # The file should be deleted after closing
    assert not os.path.exists(path)


# ---------- Exception and Edge Case Tests ----------

def test_get_path_in_memory_mode_raises():
    store = tempDataStore(use_memory=True)
    with pytest.raises(RuntimeError):
        store.get_path()


def test_write_wrong_type_text_mode():
    store = tempDataStore(use_memory=True, binary=False)
    with pytest.raises(TypeError):
        store.write(1234)  # Invalid data type
    store.close()


def test_write_wrong_type_binary_mode():
    store = tempDataStore(use_memory=True, binary=True)
    with pytest.raises(TypeError):
        store.write(1234)  # Invalid data type
    store.close()


def test_read_after_close_raises():
    store = tempDataStore(use_memory=True)
    store.close()
    with pytest.raises(RuntimeError):
        store.read()


def test_context_manager_auto_close_and_delete():
    """Test that the with-context closes and deletes the file automatically."""
    with tempDataStore(use_memory=False, binary=False) as store:
        path = store.get_path()
        assert os.path.exists(path)
        store.write("context test")
    # After leaving the context, file should be deleted
    assert not os.path.exists(path)
    assert store.closed


def test_double_close_is_safe():
    """Closing twice should not raise an error."""
    store = tempDataStore()
    store.close()
    store.close()
    assert store.closed


def test_delete_on_already_deleted_file():
    """Deleting twice should return False."""
    store = tempDataStore(use_memory=False, binary=False)
    path = store.get_path()
    assert os.path.exists(path)
    store.delete()
    assert not os.path.exists(path)
    result = store.delete()
    assert result is False
    store.close()
