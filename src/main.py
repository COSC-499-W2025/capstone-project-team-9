from config.db_config import get_connection
from upload_file import add_file_to_db
from consent.consent_manager import ConsentManager

def main():
    print("STARTING BACKEND SETUP...")
    
    # Initialize database tables
    try:
        from upload_file import init_uploaded_files_table
        init_uploaded_files_table()
    except Exception as e:
        print(f"Failed to initialize database tables: {e}")
        return

    # Initialize ConsentManager
    manager = ConsentManager(user_id="default_user")
    manager.initialize()
    
    # Check/request user consent
    if not manager.request_consent_if_needed():
        print("✗ Consent not granted. Exiting...")
        return
    else:
        print("✅ User consent granted. Proceeding with backend setup.")

    # Test database connection
    conn = get_connection()
    if conn:
        print("WE ARE GOOOOOOOD!")
        conn.close()
    else:
        print("WE ARE NOT GOOOOOOOD!")
        return
    
    # File upload interface
    while True:
        choice = input("\nDo you want to upload a ZIP file? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            filepath = input("Enter the path to your zip file: ")
            add_file_to_db(filepath)
        elif choice in ['n', 'no']:
            print("Goodbye!")
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    main()