"""
Module for storing and retrieving consent data from the database.
Sub-issue #14 & #18: Store and check consent, allow withdrawal
"""

from datetime import datetime
from config.db_config import get_connection


class ConsentStorage:
    """Handles database operations for consent management."""
    
    @staticmethod
    def initialize_consent_table():
        """Create the consent table if it doesn't exist."""
        conn = get_connection()
        if not conn:
            raise Exception("Failed to connect to database")
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_consent (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) DEFAULT 'default_user',
                    consent_given BOOLEAN NOT NULL,
                    consent_date TIMESTAMP NOT NULL,
                    withdrawn_date TIMESTAMP NULL,
                    consent_version VARCHAR(50) DEFAULT '1.0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_consent_user_id 
                ON user_consent(user_id);
            """)
            
            conn.commit()
            cursor.close()
            print("✓ Consent table initialized")
            
        except Exception as e:
            conn.rollback()
            print(f"✗ Error initializing consent table: {e}")
            raise
        finally:
            conn.close()
    
    @staticmethod
    def store_consent(consent_given, user_id='default_user'):
        """Store user consent in database."""
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM user_consent 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (user_id,))
            
            existing_record = cursor.fetchone()
            
            if existing_record:
                cursor.execute("""
                    UPDATE user_consent 
                    SET consent_given = %s,
                        consent_date = %s,
                        withdrawn_date = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (consent_given, datetime.now(), user_id))
            else:
                cursor.execute("""
                    INSERT INTO user_consent (user_id, consent_given, consent_date)
                    VALUES (%s, %s, %s)
                """, (user_id, consent_given, datetime.now()))
            
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"✗ Error storing consent: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_consent_status(user_id='default_user'):
        """
        Get current consent status.
        Sub-issue #14: Check consent before access
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT consent_given, consent_date, withdrawn_date, consent_version
                FROM user_consent 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'consent_given': result[0],
                    'consent_date': result[1],
                    'withdrawn_date': result[2],
                    'consent_version': result[3]
                }
            return None
            
        except Exception as e:
            print(f"✗ Error retrieving consent: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def withdraw_consent(user_id='default_user'):
        """
        Withdraw consent.
        Sub-issue #18: Allow withdrawal
        """
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_consent 
                SET consent_given = FALSE,
                    withdrawn_date = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (datetime.now(), user_id))
            
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"✗ Error withdrawing consent: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def has_valid_consent(user_id='default_user'):
        """
        Check if user has valid consent.
        Sub-issue #14: Main access control check
        """
        consent_data = ConsentStorage.get_consent_status(user_id)
        
        if not consent_data:
            return False
        
        return consent_data['consent_given'] and consent_data['withdrawn_date'] is None