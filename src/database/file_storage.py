from config.db_config import get_connection

DDL = """
CREATE TABLE IF NOT EXISTS uploaded_files (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL UNIQUE,
    upload_date TIMESTAMP DEFAULT NOW(),
    file_content BYTEA
);
"""

def init_file_table() -> None:
    """
    Ensure the uploaded_files table exists with a UNIQUE constraint on file_name.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(DDL)
    finally:
        conn.close()

def store_file_in_db(file_name: str, content: bytes) -> bool:
    """
    Insert a ZIP file into database.
    Returns:
        True  -> inserted successfully
        False -> rejected because a same-name file already exists
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO uploaded_files (file_name, file_content)
                    VALUES (%s, %s)
                    ON CONFLICT (file_name) DO NOTHING;
                    """,
                    (file_name, content),
                )
                # rowcount is 1 if inserted, 0 if conflict happened
                return cur.rowcount == 1
    finally:
        conn.close()

def count_files_by_name(file_name: str) -> int:
    """
    Utility for quick verification in CLI/logs and tests.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM uploaded_files WHERE file_name = %s;", (file_name,))
                (n,) = cur.fetchone()
                return int(n)
    finally:
        conn.close()
