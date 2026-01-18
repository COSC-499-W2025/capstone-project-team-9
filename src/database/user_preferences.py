from config.db_config import get_connection


def get_current_user_name() -> str:
    """
    Get the current logged-in user's username.
    Falls back to 'default_user' if no user is logged in.
    
    Returns:
        str: Current username or 'default_user'
    """
    try:
        from account.user_manager import AuthManager
        username = AuthManager.get_current_username()
        return username if username else 'default_user'
    except Exception:
        return 'default_user'


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
        else:
            # Migration: Handle user_id to user_name migration
            try:
                # Check if user_id column exists (as PRIMARY KEY)
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='user_preferences' AND column_name='user_id';
                """)
                if cur.fetchone():
                    print("Migrating user_preferences table structure")
                    # Check if user_name column already exists
                    cur.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='user_preferences' AND column_name='user_name';
                    """)
                    if not cur.fetchone():
                        # Add user_name column
                        cur.execute("""
                            ALTER TABLE user_preferences 
                            ADD COLUMN user_name VARCHAR(255);
                        """)
                        # Set default values for existing rows
                        cur.execute("""
                            UPDATE user_preferences 
                            SET user_name = 'default_user' 
                            WHERE user_name IS NULL;
                        """)
                        # Make it NOT NULL and UNIQUE
                        cur.execute("""
                            ALTER TABLE user_preferences 
                            ALTER COLUMN user_name SET NOT NULL;
                        """)
                        cur.execute("""
                            ALTER TABLE user_preferences 
                            ADD CONSTRAINT user_preferences_user_name_key UNIQUE(user_name);
                        """)
                        # Add foreign key
                        cur.execute("""
                            ALTER TABLE user_preferences 
                            DROP CONSTRAINT IF EXISTS user_preferences_user_name_fkey;
                        """)
                        cur.execute("""
                            ALTER TABLE user_preferences 
                            ADD CONSTRAINT user_preferences_user_name_fkey 
                            FOREIGN KEY (user_name) REFERENCES user_informations(user_name) ON DELETE CASCADE;
                        """)
                        conn.commit()
                        print("Migration completed successfully")
            except Exception as e:
                print(f"Migration note: {e}")
                conn.rollback()


def update_user_preferences(consent: bool):
    """
    Update the user's consent preference in the database.
    If the record doesn't exist, insert it.
    """
    try:
        current_user = get_current_user_name()
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_preferences (user_name, consent, last_updated)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_name)
                DO UPDATE SET consent = EXCLUDED.consent, last_updated = NOW();
            """, (current_user, consent))
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
        current_user = get_current_user_name()
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT consent, last_updated FROM user_preferences WHERE user_name = %s;", (current_user,))
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
