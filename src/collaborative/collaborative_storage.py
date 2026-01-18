from config.db_config import with_db_cursor
from datetime import datetime

class CollaborativeStorage:
    """
    Handles storage and retrieval of user consent and collaborative preferences.
    """

    @staticmethod
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

    @staticmethod
    def init_table():
        """Create user_preferences table if it does not exist."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id SERIAL PRIMARY KEY,
                        user_name VARCHAR(255) NOT NULL UNIQUE,
                        consent BOOLEAN DEFAULT FALSE,
                        collaborative BOOLEAN DEFAULT FALSE,
                        last_updated TIMESTAMP DEFAULT NOW(),
                        FOREIGN KEY (user_name) REFERENCES user_informations(user_name) ON DELETE CASCADE
                    );
                """)
            
            # Migration: Handle user_id to user_name migration
            try:
                with with_db_cursor() as cursor:
                    # Check if user_id column exists (as PRIMARY KEY)
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='user_preferences' AND column_name='user_id';
                    """)
                    if cursor.fetchone():
                        print("Migrating user_preferences table structure")
                        # Check if user_name column already exists
                        cursor.execute("""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name='user_preferences' AND column_name='user_name';
                        """)
                        if not cursor.fetchone():
                            # Add user_name column
                            cursor.execute("""
                                ALTER TABLE user_preferences 
                                ADD COLUMN user_name VARCHAR(255);
                            """)
                            # Set default values for existing rows
                            cursor.execute("""
                                UPDATE user_preferences 
                                SET user_name = 'default_user' 
                                WHERE user_name IS NULL;
                            """)
                            # Make it NOT NULL and UNIQUE
                            cursor.execute("""
                                ALTER TABLE user_preferences 
                                ALTER COLUMN user_name SET NOT NULL;
                            """)
                            cursor.execute("""
                                ALTER TABLE user_preferences 
                                ADD CONSTRAINT user_preferences_user_name_key UNIQUE(user_name);
                            """)
                            # Add foreign key
                            cursor.execute("""
                                ALTER TABLE user_preferences 
                                ADD CONSTRAINT user_preferences_user_name_fkey 
                                FOREIGN KEY (user_name) REFERENCES user_informations(user_name) ON DELETE CASCADE;
                            """)
                            print("Migration completed successfully")
            except Exception as e:
                print(f"Migration note: {e}")
        except ConnectionError:
            raise Exception("Failed to connect to database")
        except Exception as e:
            raise Exception(f"Error initializing user_preferences table: {e}")

    @staticmethod
    def update_consent(consent: bool):
        """Update user consent preference."""
        try:
            current_user = CollaborativeStorage.get_current_user_name()
            with with_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_preferences (user_name, consent, last_updated)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (user_name)
                    DO UPDATE SET consent = EXCLUDED.consent, last_updated = NOW();
                """, (current_user, consent))
        except ConnectionError:
            raise Exception("Failed to connect to database")
        except Exception as e:
            raise Exception(f"Error updating consent: {e}")

    @staticmethod
    def update_collaborative(collaborative: bool):
        """Update user collaborative preference."""
        try:
            current_user = CollaborativeStorage.get_current_user_name()
            with with_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_preferences (user_name, collaborative, last_updated)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (user_name)
                    DO UPDATE SET collaborative = EXCLUDED.collaborative, last_updated = NOW();
                """, (current_user, collaborative))
        except ConnectionError:
            raise Exception("Failed to connect to database")
        except Exception as e:
            raise Exception(f"Error updating collaborative preference: {e}")

    @staticmethod
    def get_preferences():
        """Return tuple (consent: bool, collaborative: bool, last_updated: datetime)"""
        try:
            current_user = CollaborativeStorage.get_current_user_name()
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT consent, collaborative, last_updated 
                    FROM user_preferences 
                    WHERE user_name = %s;
                """, (current_user,))
                result = cursor.fetchone()
            return result
        except ConnectionError:
            return None
        except Exception:
            return None
