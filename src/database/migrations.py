"""
Database migration module for automatic schema updates.
This module handles all database schema migrations automatically on startup.
"""

from config.db_config import with_db_cursor
import hashlib


def ensure_default_user():
    """Ensure default_user and test users exist in user_informations table."""
    try:
        with with_db_cursor() as cursor:
            # Create default_user
            cursor.execute('SELECT user_name FROM user_informations WHERE user_name = %s;', ('default_user',))
            if not cursor.fetchone():
                print('Creating default_user in user_informations table...')
                password_hash = hashlib.sha256('password'.encode('utf-8')).hexdigest()
                cursor.execute('''
                    INSERT INTO user_informations (user_name, password, create_time, is_login)
                    VALUES (%s, %s, NOW(), FALSE);
                ''', ('default_user', password_hash))
                print('✓ default_user created successfully')
            
            # Create test users for testing
            test_users = [('test_user', 'test_hash'), ('test_user_pytest', 'test_hash')]
            for test_user, test_hash in test_users:
                cursor.execute('SELECT user_name FROM user_informations WHERE user_name = %s;', (test_user,))
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO user_informations (user_name, password, create_time, is_login)
                        VALUES (%s, %s, NOW(), FALSE);
                    ''', (test_user, test_hash))
                    print(f'✓ {test_user} created for testing')
    except Exception as e:
        print(f'Note: {e}')


def migrate_user_consent_table():
    """Migrate user_consent table from user_id to user_name."""
    try:
        with with_db_cursor() as cursor:
            # Check if user_id column exists
            cursor.execute('''
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='user_consent' AND column_name='user_id';
            ''')
            
            if cursor.fetchone():
                print('Migrating user_consent table: user_id → user_name...')
                
                # Delete invalid records that don't exist in user_informations
                cursor.execute('''
                    DELETE FROM user_consent 
                    WHERE user_id NOT IN (SELECT user_name FROM user_informations);
                ''')
                
                # Drop old constraints and indexes
                cursor.execute('DROP INDEX IF EXISTS idx_user_consent_user_id;')
                
                # Rename column
                cursor.execute('ALTER TABLE user_consent RENAME COLUMN user_id TO user_name;')
                
                # Add new constraints
                cursor.execute('ALTER TABLE user_consent DROP CONSTRAINT IF EXISTS user_consent_user_name_key;')
                cursor.execute('ALTER TABLE user_consent ADD CONSTRAINT user_consent_user_name_key UNIQUE(user_name);')
                
                # Add foreign key
                cursor.execute('ALTER TABLE user_consent DROP CONSTRAINT IF EXISTS user_consent_user_name_fkey;')
                cursor.execute('''
                    ALTER TABLE user_consent 
                    ADD CONSTRAINT user_consent_user_name_fkey 
                    FOREIGN KEY (user_name) REFERENCES user_informations(user_name) ON DELETE CASCADE;
                ''')
                
                # Create new index
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_consent_user_name ON user_consent(user_name);')
                
                print('✓ user_consent table migrated successfully')
                return True
    except Exception as e:
        print(f'Migration note (user_consent): {e}')
    return False


def migrate_external_service_permissions_table():
    """Migrate external_service_permissions table from user_id to user_name."""
    try:
        with with_db_cursor() as cursor:
            # Check if user_id column exists
            cursor.execute('''
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='external_service_permissions' AND column_name='user_id';
            ''')
            
            if cursor.fetchone():
                print('Migrating external_service_permissions table: user_id → user_name...')
                
                # Delete invalid records
                cursor.execute('''
                    DELETE FROM external_service_permissions 
                    WHERE user_id NOT IN (SELECT user_name FROM user_informations);
                ''')
                
                # Drop old constraints and indexes
                cursor.execute('DROP INDEX IF EXISTS idx_service_permissions_user_service;')
                cursor.execute('''
                    ALTER TABLE external_service_permissions 
                    DROP CONSTRAINT IF EXISTS external_service_permissions_user_id_service_name_key;
                ''')
                
                # Rename column
                cursor.execute('ALTER TABLE external_service_permissions RENAME COLUMN user_id TO user_name;')
                
                # Add new constraints
                cursor.execute('''
                    ALTER TABLE external_service_permissions 
                    ADD CONSTRAINT external_service_permissions_user_name_service_name_key 
                    UNIQUE(user_name, service_name);
                ''')
                
                # Add foreign key
                cursor.execute('''
                    ALTER TABLE external_service_permissions 
                    DROP CONSTRAINT IF EXISTS external_service_permissions_user_name_fkey;
                ''')
                cursor.execute('''
                    ALTER TABLE external_service_permissions 
                    ADD CONSTRAINT external_service_permissions_user_name_fkey 
                    FOREIGN KEY (user_name) REFERENCES user_informations(user_name) ON DELETE CASCADE;
                ''')
                
                # Create new index
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_service_permissions_user_service 
                    ON external_service_permissions(user_name, service_name);
                ''')
                
                print('✓ external_service_permissions table migrated successfully')
                return True
    except Exception as e:
        print(f'Migration note (external_service_permissions): {e}')
    return False


def migrate_user_preferences_table():
    """Migrate user_preferences table to use user_name with proper structure."""
    try:
        with with_db_cursor() as cursor:
            # Check current table structure
            cursor.execute('''
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='user_preferences' ORDER BY ordinal_position;
            ''')
            columns = [row[0] for row in cursor.fetchall()]
            
            # Check if we need to rebuild the table
            if 'user_id' in columns and columns[0] == 'user_id':
                print('Migrating user_preferences table: rebuilding structure...')
                
                # Create new table with correct structure
                cursor.execute('''
                    CREATE TABLE user_preferences_new (
                        id SERIAL PRIMARY KEY,
                        user_name VARCHAR(255) NOT NULL UNIQUE,
                        consent BOOLEAN DEFAULT FALSE,
                        collaborative BOOLEAN DEFAULT FALSE,
                        git_username VARCHAR(255),
                        last_updated TIMESTAMP DEFAULT NOW(),
                        FOREIGN KEY (user_name) REFERENCES user_informations(user_name) ON DELETE CASCADE
                    );
                ''')
                
                # Migrate existing data
                cursor.execute('''
                    INSERT INTO user_preferences_new (user_name, consent, collaborative, git_username, last_updated)
                    SELECT 'default_user', 
                           COALESCE(consent, FALSE), 
                           COALESCE(collaborative, FALSE),
                           git_username,
                           COALESCE(last_updated, NOW())
                    FROM user_preferences
                    WHERE user_id = 1
                    ON CONFLICT (user_name) DO NOTHING;
                ''')
                
                # Drop old table and rename new one
                cursor.execute('DROP TABLE user_preferences CASCADE;')
                cursor.execute('ALTER TABLE user_preferences_new RENAME TO user_preferences;')
                
                print('✓ user_preferences table migrated successfully')
                return True
            elif 'user_id' in columns and 'user_name' not in columns:
                print('Migrating user_preferences table: adding user_name column...')
                
                # Add user_name column
                cursor.execute('ALTER TABLE user_preferences ADD COLUMN user_name VARCHAR(255);')
                cursor.execute("UPDATE user_preferences SET user_name = 'default_user' WHERE user_name IS NULL;")
                cursor.execute('ALTER TABLE user_preferences ALTER COLUMN user_name SET NOT NULL;')
                cursor.execute('ALTER TABLE user_preferences ADD CONSTRAINT user_preferences_user_name_key UNIQUE(user_name);')
                
                # Add foreign key
                cursor.execute('ALTER TABLE user_preferences DROP CONSTRAINT IF EXISTS user_preferences_user_name_fkey;')
                cursor.execute('''
                    ALTER TABLE user_preferences 
                    ADD CONSTRAINT user_preferences_user_name_fkey 
                    FOREIGN KEY (user_name) REFERENCES user_informations(user_name) ON DELETE CASCADE;
                ''')
                
                print('✓ user_preferences table migrated successfully')
                return True
    except Exception as e:
        print(f'Migration note (user_preferences): {e}')
    return False


def run_all_migrations():
    """
    Run all database migrations automatically.
    This function is idempotent and can be safely called multiple times.
    """
    print("\n" + "="*70)
    print("Running database migrations...")
    print("="*70)
    
    # Ensure default user exists first
    ensure_default_user()
    
    # Run all table migrations
    migrations_run = []
    
    if migrate_user_consent_table():
        migrations_run.append('user_consent')
    
    if migrate_external_service_permissions_table():
        migrations_run.append('external_service_permissions')
    
    if migrate_user_preferences_table():
        migrations_run.append('user_preferences')
    
    # Summary
    if migrations_run:
        print(f"\n✓ Migrations completed for: {', '.join(migrations_run)}")
    else:
        print("\n✓ All tables are up to date")
    
    print("="*70 + "\n")
