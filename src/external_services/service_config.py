from config.db_config import get_connection


class ServiceConfig:

    @staticmethod
    def initialize_table():
        """Create the external_service_permissions table if it doesn't exist."""
        conn = get_connection()
        if not conn:
            raise Exception("Failed to connect to database")
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS external_service_permissions (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    service_name VARCHAR(100) NOT NULL,
                    permission_granted BOOLEAN NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, service_name)
                );
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_service_permissions_user_service 
                ON external_service_permissions(user_id, service_name);
            """)
            
            conn.commit()
            cursor.close()
            print("✓ External service permissions table initialized")
            
        except Exception as e:
            conn.rollback()
            print(f"✗ Error initializing external service permissions table: {e}")
            raise
        finally:
            conn.close()
    
    @staticmethod
    def get_permission(user_id, service_name):
        """
        Get permission status for a service.
        
        Args:
            user_id (str): User identifier
            service_name (str): Name of the service
        
        Returns:
            bool or None: True/False if permission exists, None if no record
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT permission_granted
                FROM external_service_permissions 
                WHERE user_id = %s AND service_name = %s
                ORDER BY updated_at DESC 
                LIMIT 1
            """, (user_id, service_name))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return result[0]
            
            return None
            
        except Exception as e:
            print(f"✗ Error retrieving service permission: {e}")
            return None
        finally:
            conn.close()