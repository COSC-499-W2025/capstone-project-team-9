from config.db_config import get_connection
from upload_file import add_file_to_db
from project_manager import list_projects
from consent.consent_manager import ConsentManager
from collaborative.collaborative_manager import CollaborativeManager
from src.analysis.key_metrics import analyze_project_from_db

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
        print("3. Analyze project metrics")
        print("4. Exit")
        print("-"*50)
        
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == '1':
            filepath = input("Enter the path to your zip file: ")
            add_file_to_db(filepath)
        elif choice == '2':
            list_projects()
        elif choice == "3":
            project_id = input("Enter the project ID to analyze: ").strip()
            if project_id.isdigit():
                analyze_project_from_db(int(project_id))
            else:
                print("Invalid project ID.")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1–4.")

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