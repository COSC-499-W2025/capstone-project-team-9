from config.db_config import get_connection


def init_user_preferences_table():
    """
    Create the user_preferences table if it does not exist.
    This table stores user consent and future preferences.
    """
    with get_connection() as conn, conn.cursor() as cur:
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'user_preferences'
            );
        """)
        exists = cur.fetchone()[0]

        if not exists:
            cur.execute("""
                CREATE TABLE user_preferences (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL UNIQUE,
                    consent BOOLEAN NOT NULL,
                    collaborative BOOLEAN NOT NULL,
                    git_username VARCHAR(255),
                    last_updated TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (user_name) REFERENCES user_informations(user_name) ON DELETE CASCADE
                );
            """)
            conn.commit()


def update_user_preferences(consent: bool):
    """
    Update the user's consent preference in the database.
    If the record doesn't exist, insert it.
    """
    try:
        with get_connection() as conn, conn.cursor() as cur:
            # Get default user name or use 'default_user'
            cur.execute("""
                INSERT INTO user_preferences (user_name, consent, last_updated)
                VALUES ('default_user', %s, NOW())
                ON CONFLICT (user_name)
                DO UPDATE SET consent = EXCLUDED.consent, last_updated = NOW();
            """, (consent,))
            conn.commit()
    except Exception as e:
        raise Exception(f"Error updating user preferences: {e}")


def get_user_preferences():
    """
    Retrieve user preferences from the database.
    Returns:
        tuple: (consent: bool, last_updated: datetime) or None
    """
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT consent, last_updated FROM user_preferences WHERE user_name = 'default_user';")
            return cur.fetchone()
    except Exception:
        return None


def update_user_collaboration(collaborative: bool):
    """
    Update the user's collaboration preference in the database.
    If the record doesn't exist, insert it.
    """
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_preferences (user_id, collaborative, last_updated)
                VALUES (1, %s, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET collaborative = EXCLUDED.collaborative, last_updated = NOW();
            """, (collaborative,))
            conn.commit()
    except Exception as e:
        raise Exception(f"Error updating user collaboration: {e}")


def get_user_collaboration():
    """
    Retrieve the user's collaboration setting.
    Returns:
        tuple: (collaborative: bool, last_updated: datetime) or None
    """
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT collaborative, last_updated FROM user_preferences WHERE user_id = 1;")
            return cur.fetchone()
    except Exception:
        return None


def update_user_git_username(git_username: str):
    """
    Update or insert the user's GitHub username.
    """
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_preferences (user_id, git_username, last_updated)
                VALUES (1, %s, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET git_username = EXCLUDED.git_username, last_updated = NOW();
            """, (git_username,))
            conn.commit()
    except Exception as e:
        raise Exception(f"Error updating GitHub username: {e}")


def get_user_git_username():
    """
    Retrieve the user's GitHub username.
    Returns:
        str or None
    """
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT git_username FROM user_preferences WHERE user_id = 1;")
            result = cur.fetchone()
            return result[0] if result else None
    except Exception:
        return None
