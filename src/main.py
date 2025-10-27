from config.db_config import get_connection
from upload_file import add_file_to_db
from project_manager import list_projects
from consent.consent_manager import ConsentManager
from collaborative.collaborative_manager import CollaborativeManager
from project_summarizer import summarize_project, get_available_projects
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/collaborative")))
from identify_contributors import identify_contributors


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
        print("Database is connected!")
        conn.close()
    else:
        print("Database is not connected.")
        return
    
    # Main menu interface
    while True:
        print("\n" + "-"*50)
        print("Upload and Analyze files main page")
        print("-"*50)
        print("1. Upload a ZIP file")
        print("2. List stored projects")
        print("3. Summarize a project")
        print("4. Exit")
        print("-"*50)
        
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == '1':
            filepath = input("Enter the path to your zip file: ")
            add_file_to_db(filepath)
        elif choice == '2':
            list_projects()
        elif choice == '3':
            summarize_project_menu()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

    # Initialize CollabrativeManager
    manager = CollaborativeManager()
    # Check/request user consent
    if not manager.request_collaborative_if_needed():
        print("Collaborative not granted. Doing individual.")
        return
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

if __name__ == "__main__":
    main()