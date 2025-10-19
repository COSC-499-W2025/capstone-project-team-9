from database.file_storage import init_file_table, store_file_in_db

def test_reject_duplicate_names():
    init_file_table()
    name = "dup_test.zip"
    blob = b"PK\x03\x04" + b"\x00" * 8  # minimal valid header
    assert store_file_in_db(name, blob) is True   # first insert
    assert store_file_in_db(name, blob) is False  # duplicate rejected
