from config.db_config import with_db_cursor
from datetime import datetime

class CollaborativeStorage:
    """
    Handles storage and retrieval of user consent and collaborative preferences.
    """

    USER_ID = 1  # Default user

    @staticmethod
    def init_table():
        """Create user_preferences table if it does not exist."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        user_id SERIAL PRIMARY KEY,
                        consent BOOLEAN DEFAULT FALSE,
                        collaborative BOOLEAN DEFAULT FALSE,
                        last_updated TIMESTAMP DEFAULT NOW()
                    );
                """)
        except ConnectionError:
            raise Exception("Failed to connect to database")
        except Exception as e:
            raise Exception(f"Error initializing user_preferences table: {e}")

    @staticmethod
    def update_consent(consent: bool):
        """Update user consent preference."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_preferences (user_id, consent, last_updated)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (user_id)
                    DO UPDATE SET consent = EXCLUDED.consent, last_updated = NOW();
                """, (CollaborativeStorage.USER_ID, consent))
        except ConnectionError:
            raise Exception("Failed to connect to database")
        except Exception as e:
            raise Exception(f"Error updating consent: {e}")

    @staticmethod
    def update_collaborative(collaborative: bool):
        """Update user collaborative preference."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_preferences (user_id, collaborative, last_updated)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (user_id)
                    DO UPDATE SET collaborative = EXCLUDED.collaborative, last_updated = NOW();
                """, (CollaborativeStorage.USER_ID, collaborative))
        except ConnectionError:
            raise Exception("Failed to connect to database")
        except Exception as e:
            raise Exception(f"Error updating collaborative preference: {e}")

    @staticmethod
    def get_preferences():
        """Return tuple (consent: bool, collaborative: bool, last_updated: datetime)"""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT consent, collaborative, last_updated 
                    FROM user_preferences 
                    WHERE user_id = %s;
                """, (CollaborativeStorage.USER_ID,))
                result = cursor.fetchone()
            return result
        except ConnectionError:
            return None
        except Exception:
            return None
