from config.db_config import get_connection
from upload_file import add_file_to_db
from project_manager import list_projects
from consent.consent_manager import ConsentManager
from collaborative.collaborative_manager import CollaborativeManager
from analysis.key_metrics import analyze_project_from_db
from project_summarizer import summarize_project, get_available_projects
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/collaborative")))
from identify_contributors import identify_contributors
from tools.cleanup_insights import delete_insights

consent_manager = ConsentManager(user_id="default_user")
collab_manager = CollaborativeManager()

def ensure_user_preferences_schema():
    """Ensure user_preferences table has all required columns and defaults."""
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                ALTER TABLE user_preferences
                ADD COLUMN IF NOT EXISTS collaborative BOOLEAN DEFAULT FALSE;
            """)
            cur.execute("""
                ALTER TABLE user_preferences
                ALTER COLUMN consent SET DEFAULT TRUE;
            """)
            conn.commit()
        print("user_preferences schema verified/updated")
    except Exception as e:
        print(f"[WARN] Failed to update user_preferences schema: {e}")


def summarize_project_menu():
    """Handle the project summarization menu."""
    print("\n" + "-"*50)
    print("Project Summarization")
    print("-"*50)
    
    # Get available projects
    projects = get_available_projects()
    
    if not projects:
        print("No projects found in database.")
        print("Please upload a project first using option 1.")
        return
    
    # Display available projects
    print("Available projects:")
    for i, project in enumerate(projects, 1):
        created_date = project['created_at'].strftime("%Y-%m-%d") if project['created_at'] else "Unknown"
        print(f"{i}. {project['filename']} (ID: {project['id']}, Created: {created_date})")
    
    print("-"*50)
    
    # Get user selection
    while True:
        try:
            choice = input(f"Select a project to summarize (1-{len(projects)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                return
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(projects):
                selected_project = projects[choice_num - 1]
                print(f"\nGenerating summary for: {selected_project['filename']}")
                print("Please wait...")
                
                # Generate and display summary
                summary = summarize_project(selected_project['id'])
                print(summary)
                
                # Ask if user wants to continue
                continue_choice = input("\nPress Enter to continue or 'q' to quit: ").strip()
                if continue_choice.lower() == 'q':
                    return
                break
            else:
                print(f"Please enter a number between 1 and {len(projects)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")

def ensure_user_preferences_schema():
    """Ensure user_preferences table has all required columns and defaults."""
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                ALTER TABLE user_preferences
                ADD COLUMN IF NOT EXISTS collaborative BOOLEAN DEFAULT FALSE;
            """)
            cur.execute("""
                ALTER TABLE user_preferences
                ALTER COLUMN consent SET DEFAULT TRUE;
            """)
            conn.commit()
        print("user_preferences schema verified/updated")
    except Exception as e:
        print(f"[WARN] Failed to update user_preferences schema: {e}")

def ask_user_preferences(is_start):
    if consent_manager.has_access() and not is_start:
        while True:
            response = input("\nWould you like to withdraw consent? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                consent_manager.withdraw()
                print("\nConsent withdrawn. Thank you!")
                break
            elif response in ['no', 'n']:
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
    else:
        """Asks the user what their prefereces(consent, collaborative) are"""
        # Check/request user consent
        if not consent_manager.request_consent_if_needed():
            print("Consent not granted.")
        else:
            print("User consent granted.\n")

    prefs = collab_manager.get_preferences()
    if prefs and prefs[1] and not is_start: 
        while True:
            response = input("\nWould you like to not include collaborative work? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                collab_manager.update_collaborative(False)
                print("\nCollaborative not granted. Thank you!")
                break
            elif response in ['no', 'n']:
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
    else:
        # Check/request user consent
        if not collab_manager.request_collaborative_if_needed():
            print("Collaborative not granted. Doing individual.")
        else:
            print("Collaborative granted. Doing colabrative and individual.")
            # Path to the ZIP file
            zip_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../test.zip"))
            ic = identify_contributors(zip_path)
            try:
                # Extract the repo
                repo_path = ic.extract_repo()
                if repo_path is None:
                    print("No git repository found in the ZIP.")
                    return
                # Get commit counts per author
                commit_counts = ic.get_commit_counts()
                print("Commit counts per user:")
                for user, count in commit_counts.items():
                    print(f"{user}: {count} commits")
            finally:
                # Cleanup temporary extracted files
                ic.cleanup()

def main():
    print("STARTING BACKEND SETUP...")

    # Ensure user_preferences schema is up to date
    ensure_user_preferences_schema()
    
    # Initialize database tables
    try:
        from upload_file import init_uploaded_files_table
        init_uploaded_files_table()
    except Exception as e:
        print(f"Failed to initialize database tables: {e}")
        return
    
    # Test database connection
    conn = get_connection()
    if conn:
        print("Database is connected!")
        conn.close()
    else:
        print("Database is not connected.")
        return

    # Initialize ConsentManager
    consent_manager.initialize()
    ask_user_preferences(True)
    
    # Main menu interface
    while True:
        print("\n" + "-"*50)
        print("Upload and Analyze files main page")
        print("-"*50)
        print("1. Upload a ZIP file")
        print("2. List stored projects")
        print("3. Analyze project metrics")
        print("4. Summarize a project")
        print("5. Change preferences")
        print("6. Cleanup insights for a project")
        print("7. Exit")
        print("-"*50)
        
        choice = input("Choose an option (1-7): ").strip()
        
        if choice == '1':
            filepath = input("Enter the path to your zip file (full or relative): ")
            add_file_to_db(filepath)
            
        elif choice == '2':
            list_projects()
        elif choice == '3':
            project_id = input("Enter the project ID to analyze: ").strip()
            if project_id.isdigit():
                analyze_project_from_db(int(project_id))
            else:
                print("Invalid project ID.")
        elif choice == '4':
            summarize_project_menu()
        elif choice == '5':
            ask_user_preferences(False)
        elif choice == '6':
            pid = input("Enter project ID to clean: ").strip()
            if pid.isdigit():
                confirm = input(f"Delete insights for project {pid}? This cannot be undone. (y/n): ").strip().lower()
                if confirm in ('y', 'yes'):
                    m, f = delete_insights(int(pid))
                    print(f"Deleted: project_metrics={m}, file_contents={f}")
                else:
                    print("Cancelled.")
            else:
                print("Invalid project ID.")
        elif choice == '7':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()
