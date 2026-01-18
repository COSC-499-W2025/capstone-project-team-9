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
            
            # Migration: Rename user_id column to user_name if it exists
            try:
                with with_db_cursor() as cursor:
                    # Check if user_id column exists
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='external_service_permissions' AND column_name='user_id';
                    """)
                    if cursor.fetchone():
                        print("Migrating external_service_permissions table: user_id -> user_name")
                        # Drop old constraints and indexes
                        cursor.execute("DROP INDEX IF EXISTS idx_service_permissions_user_service;")
                        cursor.execute("""
                            ALTER TABLE external_service_permissions 
                            DROP CONSTRAINT IF EXISTS external_service_permissions_user_id_service_name_key;
                        """)
                        # Rename column
                        cursor.execute("""
                            ALTER TABLE external_service_permissions 
                            RENAME COLUMN user_id TO user_name;
                        """)
                        # Add new constraints and foreign key
                        cursor.execute("""
                            ALTER TABLE external_service_permissions 
                            ADD CONSTRAINT external_service_permissions_user_name_service_name_key 
                            UNIQUE(user_name, service_name);
                        """)
                        cursor.execute("""
                            ALTER TABLE external_service_permissions 
                            DROP CONSTRAINT IF EXISTS external_service_permissions_user_name_fkey;
                        """)
                        cursor.execute("""
                            ALTER TABLE external_service_permissions 
                            ADD CONSTRAINT external_service_permissions_user_name_fkey 
                            FOREIGN KEY (user_name) REFERENCES user_informations(user_name) ON DELETE CASCADE;
                        """)
                        # Create new index
                        cursor.execute("""
                            CREATE INDEX IF NOT EXISTS idx_service_permissions_user_service 
                            ON external_service_permissions(user_name, service_name);
                        """)
                        print("Migration completed successfully")
            except Exception as e:
                print(f"Migration note: {e}")
            
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