from config.db_config import get_connection
from upload_file import add_file_to_db
from project_manager import list_projects
from consent.consent_manager import ConsentManager
from collaborative.collaborative_manager import CollaborativeManager

def display_error(result):
    """Format and display error information"""
    print("\n" + "="*60)
    print("❌ ERROR")
    print("="*60)
    print(f"Error Type: {result.error_type}")
    print(f"Message: {result.message}")
    if result.data:
        print("\nDetails:")
        for key, value in result.data.items():
            print(f"  • {key}: {value}")
    print("="*60 + "\n")

def display_success(result):
    """Format and display success information"""
    print("\n" + "="*60)
    print("✅ SUCCESS")
    print("="*60)
    print(f"Message: {result.message}")
    if result.data:
        print("\nDetails:")
        for key, value in result.data.items():
            if key != "files":  # files list is too long, handle separately
                print(f"  • {key}: {value}")
        if "files" in result.data and result.data["files"]:
            print(f"\nContains {len(result.data['files'])} files:")
            for i, file in enumerate(result.data['files'][:5], 1):
                print(f"  {i}. {file}")
            if len(result.data['files']) > 5:
                print(f"  ... and {len(result.data['files']) - 5} more files")
    print("="*60 + "\n")

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
        print("Consent not granted. Exiting...")
        return
    else:
        print("User consent granted. Proceeding with backend setup.")

    # Test database connection
    conn = get_connection()
    if conn:
        print("WE ARE GOOOOOOOD!")
        conn.close()
    else:
        print("WE ARE NOT GOOOOOOOD!")
        return
    
    # Main menu interface
    while True:
        print("\n" + "-"*50)
        print("Upload and Analyze files main page")
        print("-"*50)
        print("1. Upload a ZIP file")
        print("2. List stored projects")
        print("3. Exit")
        print("-"*50)
        
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == '1':
            filepath = input("Enter the path to your zip file: ")
            result = add_file_to_db(filepath)
            
            if result.success:
                display_success(result)
            else:
                display_error(result)
                
        elif choice == '2':
            list_projects()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    # Initialize CollabrativeManager
    manager = CollaborativeManager()
    # Check/request user consent
    if not manager.request_collaborative_if_needed():
        print("Collaborative not granted. Doing individual.")
        return
    else:
        print("Collaborative granted. Doing colabrative and individual.")

if __name__ == "__main__":
    main()