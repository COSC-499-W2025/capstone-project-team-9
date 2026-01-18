"""
Module for storing and retrieving consent data from the database.
Sub-issue #14 & #18: Store and check consent, allow withdrawal
"""

from datetime import datetime
from config.db_config import with_db_cursor


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


class ConsentStorage:
    """Handles database operations for consent management."""
    
    @staticmethod
    def initialize_consent_table():
        """Create the consent table if it doesn't exist."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_consent (
                        id SERIAL PRIMARY KEY,
                        user_name VARCHAR(255) NOT NULL,
                        consent_given BOOLEAN NOT NULL,
                        consent_date TIMESTAMP NOT NULL,
                        withdrawn_date TIMESTAMP NULL,
                        consent_version VARCHAR(50) DEFAULT '1.0',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_name),
                        FOREIGN KEY (user_name) REFERENCES user_informations(user_name) ON DELETE CASCADE
                    );
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_consent_user_name 
                    ON user_consent(user_name);
                """)
            
            print("Consent table initialized")
            
        except ConnectionError:
            raise Exception("Failed to connect to database")
        except Exception as e:
            print(f"Error initializing consent table: {e}")
            raise
    
    @staticmethod
    def store_consent(consent_given, user_name=None):
        """Store user consent in database."""
        if user_name is None:
            user_name = get_current_user_name()
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM user_consent 
                    WHERE user_name = %s 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (user_name,))
                
                existing_record = cursor.fetchone()
                
                if existing_record:
                    cursor.execute("""
                        UPDATE user_consent 
                        SET consent_given = %s,
                            consent_date = %s,
                            withdrawn_date = NULL,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_name = %s
                    """, (consent_given, datetime.now(), user_name))
                else:
                    cursor.execute("""
                        INSERT INTO user_consent (user_name, consent_given, consent_date)
                        VALUES (%s, %s, %s)
                    """, (user_name, consent_given, datetime.now()))
            
            return True
            
        except ConnectionError:
            return False
        except Exception as e:
            print(f"Error storing consent: {e}")
            return False
    
    @staticmethod
    def get_consent_status(user_name=None):
        """
        Get current consent status.
        Sub-issue #14: Check consent before access
        """
        if user_name is None:
            user_name = get_current_user_name()
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT consent_given, consent_date, withdrawn_date, consent_version
                    FROM user_consent 
                    WHERE user_name = %s 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (user_name,))
                
                result = cursor.fetchone()
            
            if result:
                return {
                    'consent_given': result[0],
                    'consent_date': result[1],
                    'withdrawn_date': result[2],
                    'consent_version': result[3]
                }
            return None
            
        except ConnectionError:
            return None
        except Exception as e:
            print(f"✗ Error retrieving consent: {e}")
            return None
    
    @staticmethod
    def withdraw_consent(user_name=None):
        """
        Withdraw consent.
        Sub-issue #18: Allow withdrawal
        """
        if user_name is None:
            user_name = get_current_user_name()
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    UPDATE user_consent 
                    SET consent_given = FALSE,
                        withdrawn_date = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_name = %s
                """, (datetime.now(), user_name))
            
            return True
            
        except ConnectionError:
            return False
        except Exception as e:
            print(f"Error withdrawing consent: {e}")
            return False
    
    @staticmethod
    def has_valid_consent(user_name=None):
        """
        Check if user has valid consent.
        Sub-issue #14: Main access control check
        """
        if user_name is None:
            user_name = get_current_user_name()
        consent_data = ConsentStorage.get_consent_status(user_name)
        
        if not consent_data:
            return False
        
        return consent_data['consent_given'] and consent_data['withdrawn_date'] is None