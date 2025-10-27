# src/database/user_preferences.py

from config.db_config import get_connection

def init_user_preferences_table():
    """
    Create the user_preferences table if it does not exist.
    This table stores user consent and future preferences.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id SERIAL PRIMARY KEY,
            consent BOOLEAN NOT NULL,
            collaborative BOOLEAN NOT NULL,
            git_username VARCHAR(255),
            last_updated TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    conn.close()


def update_user_preferences(consent: bool):
    """
    Update the user's consent preference in the database.
    If the record doesn't exist, insert it.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_preferences (user_id, consent, last_updated)
        VALUES (1, %s, NOW())
        ON CONFLICT (user_id)
        DO UPDATE SET consent = EXCLUDED.consent, last_updated = NOW();
    """, (consent,))
    conn.commit()
    conn.close()


def get_user_preferences():
    """
    Retrieve user preferences from the database.
    Returns:
        tuple: (consent: bool, last_updated: datetime) or None
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT consent, last_updated FROM user_preferences WHERE user_id = 1;")
    result = cursor.fetchone()
    conn.close()
    return result

def update_user_collaboration(collaborative: bool):
    """
    Update the user's consent preference in the database.
    If the record doesn't exist, insert it.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_preferences (user_id, collaborative, last_updated)
        VALUES (1, %s, NOW())
        ON CONFLICT (user_id)
        DO UPDATE SET consent = EXCLUDED.consent, last_updated = NOW();
    """, (collaborative,))
    conn.commit()
    conn.close()


def get_user_callaboration():
    """
    Retrieve user preferences from the database.
    Returns:
        tuple: (consent: bool, last_updated: datetime) or None
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT collaborative, last_updated FROM user_preferences WHERE user_id = 1;")
    result = cursor.fetchone()
    conn.close()
    return result

def update_user_git_username(git_username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_preferences (user_id, git_username, last_updated)
        VALUES (1, %s, NOW())
        ON CONFLICT (user_id)
        DO UPDATE SET git_username = EXCLUDED.git_username, last_updated = NOW();
    """, (git_username,))
    conn.commit()
    conn.close()

def get_user_git_username():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT git_username FROM user_preferences WHERE user_id = 1;")
    result = cursor.fetchone()
    conn.close()
    return result