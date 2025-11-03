import os # for getting environment variables
import psycopg # for connecting to the database
from dotenv import load_dotenv # for loading environment variables from the .env file
from contextlib import contextmanager
from typing import Optional, Generator

load_dotenv()  # loads the .env file

def get_connection():
    try: # try to connect to the database
        conn = psycopg.connect( # connect to the database
            dbname=os.getenv("POSTGRES_DB"), # database name
            user=os.getenv("POSTGRES_USER"), # username
            password=os.getenv("POSTGRES_PASSWORD"), # password
            host=os.getenv("POSTGRES_HOST"), # host
            port=os.getenv("POSTGRES_PORT") # port
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None


@contextmanager
def with_db_connection():
    """
    Context manager for database connections that handles cleanup automatically.
    
    Usage:
        with with_db_connection() as (conn, cursor):
            cursor.execute("SELECT * FROM table")
            results = cursor.fetchall()
            conn.commit()
        # Connection and cursor are automatically closed
    
    Raises:
        ConnectionError: If database connection fails
    """
    conn = get_connection()
    if not conn:
        raise ConnectionError("Could not connect to database")
    
    cursor = None
    try:
        cursor = conn.cursor()
        yield (conn, cursor)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        conn.close()


@contextmanager
def with_db_cursor():
    """
    Simplified context manager that returns just the cursor.
    Connection is handled internally and committed on success.
    
    Usage:
        with with_db_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            results = cursor.fetchall()
        # Auto-commits on success, auto-rolls back on error
    
    Raises:
        ConnectionError: If database connection fails
    """
    conn = get_connection()
    if not conn:
        raise ConnectionError("Could not connect to database")
    
    cursor = None
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        conn.close()
