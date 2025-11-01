# src/database/user_preferences.py

from config.db_config import with_db_cursor

def init_user_preferences_table():
    """
    Create the user_preferences table if it does not exist.
    This table stores user consent and future preferences.
    """
    try:
        with with_db_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id SERIAL PRIMARY KEY,
                    consent BOOLEAN NOT NULL,
                    collaborative BOOLEAN NOT NULL,
                    last_updated TIMESTAMP DEFAULT NOW()
                );
            """)
    except ConnectionError:
        raise Exception("Failed to connect to database")
    except Exception as e:
        raise Exception(f"Error initializing user_preferences table: {e}")


def update_user_preferences(consent: bool):
    """
    Update the user's consent preference in the database.
    If the record doesn't exist, insert it.
    """
    try:
        with with_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_preferences (user_id, consent, last_updated)
                VALUES (1, %s, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET consent = EXCLUDED.consent, last_updated = NOW();
            """, (consent,))
    except ConnectionError:
        raise Exception("Failed to connect to database")
    except Exception as e:
        raise Exception(f"Error updating user preferences: {e}")


def get_user_preferences():
    """
    Retrieve user preferences from the database.
    Returns:
        tuple: (consent: bool, last_updated: datetime) or None
    """
    try:
        with with_db_cursor() as cursor:
            cursor.execute("SELECT consent, last_updated FROM user_preferences WHERE user_id = 1;")
            result = cursor.fetchone()
        return result
    except ConnectionError:
        return None
    except Exception:
        return None

def update_user_collaboration(collaborative: bool):
    """
    Update the user's consent preference in the database.
    If the record doesn't exist, insert it.
    """
    try:
        with with_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_preferences (user_id, collaborative, last_updated)
                VALUES (1, %s, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET consent = EXCLUDED.consent, last_updated = NOW();
            """, (collaborative,))
    except ConnectionError:
        raise Exception("Failed to connect to database")
    except Exception as e:
        raise Exception(f"Error updating user collaboration: {e}")


def get_user_callaboration():
    """
    Retrieve user preferences from the database.
    Returns:
        tuple: (consent: bool, last_updated: datetime) or None
    """
    try:
        with with_db_cursor() as cursor:
            cursor.execute("SELECT collaborative, last_updated FROM user_preferences WHERE user_id = 1;")
            result = cursor.fetchone()
        return result
    except ConnectionError:
        return None
    except Exception:
        return None