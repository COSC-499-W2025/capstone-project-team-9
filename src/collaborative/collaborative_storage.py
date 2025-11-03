from config.db_config import get_connection
from datetime import datetime

class CollaborativeStorage:
    """
    Handles storage and retrieval of user consent and collaborative preferences.
    """

    USER_ID = 1  # Default user

    @staticmethod
    def init_table():
        """Create user_preferences table if it does not exist."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id SERIAL PRIMARY KEY,
                consent BOOLEAN DEFAULT FALSE,
                collaborative BOOLEAN DEFAULT FALSE,
                last_updated TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def update_consent(consent: bool):
        """Update user consent preference."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_preferences (user_id, consent, last_updated)
            VALUES (%s, %s, NOW())
            ON CONFLICT (user_id)
            DO UPDATE SET consent = EXCLUDED.consent, last_updated = NOW();
        """, (CollaborativeStorage.USER_ID, consent))
        conn.commit()
        conn.close()

    @staticmethod
    def update_collaborative(collaborative: bool):
        """Update user collaborative preference."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_preferences (user_id, collaborative, last_updated)
            VALUES (%s, %s, NOW())
            ON CONFLICT (user_id)
            DO UPDATE SET collaborative = EXCLUDED.collaborative, last_updated = NOW();
        """, (CollaborativeStorage.USER_ID, collaborative))
        conn.commit()
        conn.close()

    @staticmethod
    def get_preferences():
        """Return tuple (consent: bool, collaborative: bool, last_updated: datetime)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT consent, collaborative, last_updated 
            FROM user_preferences 
            WHERE user_id = %s;
        """, (CollaborativeStorage.USER_ID,))
        result = cursor.fetchone()
        conn.close()
        return result
