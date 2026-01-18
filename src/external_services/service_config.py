from config.db_config import with_db_cursor


class ServiceConfig:

    @staticmethod
    def initialize_table():
        """Create the external_service_permissions table if it doesn't exist."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS external_service_permissions (
                        id SERIAL PRIMARY KEY,
                        user_name VARCHAR(255) NOT NULL,
                        service_name VARCHAR(100) NOT NULL,
                        permission_granted BOOLEAN NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_name, service_name),
                        FOREIGN KEY (user_name) REFERENCES user_informations(user_name) ON DELETE CASCADE
                    );
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_service_permissions_user_service 
                    ON external_service_permissions(user_name, service_name);
                """)
            
            print("✓ External service permissions table initialized")
            
        except ConnectionError:
            raise Exception("Failed to connect to database")
        except Exception as e:
            print(f"✗ Error initializing external service permissions table: {e}")
            raise
    
    @staticmethod
    def get_permission(user_name, service_name):
        """
        Get permission status for a service.
        
        Args:
            user_name (str): User name identifier
            service_name (str): Name of the service
        
        Returns:
            bool or None: True/False if permission exists, None if no record
        """
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT permission_granted
                    FROM external_service_permissions 
                    WHERE user_name = %s AND service_name = %s
                    ORDER BY updated_at DESC 
                    LIMIT 1
                """, (user_name, service_name))
                
                result = cursor.fetchone()
            
            if result:
                return result[0]
            
            return None
            
        except ConnectionError:
            return None
        except Exception:
            # Silently return None if table doesn't exist or other error occurs
            return None