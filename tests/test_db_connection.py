from src.config.db_config import get_connection

def test_connection():
    conn = get_connection()
    assert conn is not None, "Database connection is BAD" # assert that the connection is not None
    print("Database connection is GOOD") # print a message to the console
    conn.close()

if __name__ == "__main__":
    test_connection()
