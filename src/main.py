from config.db_config import get_connection
from upload_file import add_file_to_db
from project_manager import list_projects
from consent.consent_manager import ConsentManager
from collaborative.collaborative_manager import CollaborativeManager
from analysis.key_metrics import analyze_project_from_db
from analysis.project_ranking import rank_all_projects, display_rankings
from project_summarizer import summarize_project, get_available_projects
from external_services.external_service_prompt import request_external_service_permission
from project_analyzer import analyze_project_by_id
import os
import sys
from collaborative.identify_contributors import identify_contributors
from database.user_preferences import get_user_git_username, update_user_git_username

def display_error(result):
    """Display error information to user."""
    print("\n" + "="*70)
    print("ERROR")
    print("="*70)
    
    if hasattr(result, 'error_type') and result.error_type:
        print(f"Error Type: {result.error_type}")
    
    if hasattr(result, 'message') and result.message:
        print(f"Message: {result.message}")
    
    if hasattr(result, 'data') and result.data:
        print("\nDetails:")
        for key, value in result.data.items():
            print(f"  {key}: {value}")
    
    print("="*70 + "\n")

def ensure_user_preferences_schema():
    """Debug version to check why git_username is not being added."""
    try:
        with get_connection() as conn, conn.cursor() as cur:
            
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = 'user_preferences'
                );
            """)
            table_exists = cur.fetchone()[0]
            print("Table exists:", table_exists)
            
            # Add git_username column if missing
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns
                WHERE table_name = 'user_preferences' AND column_name = 'git_username';
            """)
            column_exists = cur.fetchone()
            print("git_username column exists before ALTER:", column_exists)
            cur.execute("""
                ALTER TABLE user_preferences
                ADD COLUMN IF NOT EXISTS git_username VARCHAR(255);
            """)
            # Check after
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns
                WHERE table_name = 'user_preferences' AND column_name = 'git_username';
            """)
            column_exists_after = cur.fetchone()
            print("git_username column exists after ALTER:", column_exists_after)
            conn.commit()
    except Exception as e:
        print(f"[WARN] Exception caught: {e}")

def display_success(result):
    """Display success information to user."""
    print("\n" + "="*70)
    print("SUCCESS")
    print("="*70)
    
    if hasattr(result, 'message') and result.message:
        print(f"Message: {result.message}")
    
    if hasattr(result, 'data') and result.data:
        data = result.data
        
        # Display file information
        if 'filename' in data:
            print(f"File: {data['filename']}")
        
        if 'file_id' in data:
            print(f"File ID: {data['file_id']}")
        
        # Display file list
        if 'files' in data and data['files']:
            files = data['files']
            file_count = len(files)
            
            print(f"\n{file_count} files:")
            
            # Show first 5 files
            for i, file in enumerate(files[:5], 1):
                print(f"  {i}. {file}")
            
            # If more than 5 files, indicate there are more
            if file_count > 5:
                print(f"  ... and {file_count - 5} more files")
        
        # Display file count if provided
        if 'file_count' in data and 'files' not in data:
            print(f"Total files: {data['file_count']}")
    
    print("="*70 + "\n")


def _select_project_interactive(title: str):
    """Unified project selection UI. Returns selected project dict or None."""
    print("\n" + "-"*50)
    print(title)
    print("-"*50)

    projects = get_available_projects()

    if not projects:
        print("No projects found in database.")
        print("Please upload a project first using option 1.")
        return None

    print("Available projects:")
    for i, project in enumerate(projects, 1):
        created_date = project['created_at'].strftime("%Y-%m-%d") if project['created_at'] else "Unknown"
        print(f"{i}. {project['filename']} (ID: {project['id']}, Created: {created_date})")

    print("-"*50)

    while True:
        try:
            choice = input(f"Select a project (1-{len(projects)}) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                return None
            choice_num = int(choice)
            if 1 <= choice_num <= len(projects):
                return projects[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(projects)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")

def summarize_project_menu():
    """Handle the project summarization menu."""
    print("\n" + "-"*50)
    print("Project Summarization")
    print("-"*50)
    
    selected_project = _select_project_interactive("Project Summarization")
    if not selected_project:
        return
    print(f"\nGenerating summary for: {selected_project['filename']}")
    print("Please wait...")
    summary = summarize_project(selected_project['id'])
    print(summary)
    input("\nPress Enter to continue...")

def display_error(result):
    """Format and display error information"""
    print("\n" + "="*60)
    print("ERROR")
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
    print("SUCCESS")
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

def analyze_project_menu():
    """
    Handle the project analysis menu.
    This is the main menu for Issue #10: Analysis if User Declines Outside Sources.
    """
    print("\n" + "-"*50)
    print("Project Analysis (with Local Fallback)")
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
            choice = input(f"Select a project to analyze (1-{len(projects)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                return
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(projects):
                selected_project = projects[choice_num - 1]
                print(f"\nAnalyzing: {selected_project['filename']}")
                print("Please wait...")
                
                # Perform analysis (respects user's external service permission)
                analyze_project_by_id(selected_project['id'])
                
                # Ask if user wants to continue
                continue_choice = input("\nPress Enter to continue or 'q' to quit: ").strip()
                if continue_choice.lower() == 'q':
                    return
                break
            else:
                print(f"Please enter a number between 1 and {len(projects)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")

    just_changed = False
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
            if not get_user_git_username() or get_user_git_username()[0] is None:
                response = input("\nWhat is you GitHub user name: ").strip()
                update_user_git_username(response)
                just_changed = True
            print("\nYour github username is:"+str(get_user_git_username()))
            # Path to the ZIP file
            zip_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../test.zip"))
            ic = identify_contributors(zip_path=zip_path)
            # Extract the repo
            repo_path = ic.extract_repo()
            if repo_path is None:
                print("No git repository found in the ZIP.")
                return
            # Get the full contribution profile
            profile = ic.get_full_contribution_profile()
                
        if not just_changed and not get_user_git_username()[0] is None and not is_start:
            while True:
                response = input("\nWould you like to change you GitHub username? (y/n) ")
                if response in ['yes', 'y']:
                    new_username = input("\nWhat is you GitHub user name: ").strip()
                    update_user_git_username(new_username)
                    break
                elif response in ['no', 'n']:
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")

def manage_external_services_menu():
    """
    Manage external service permissions (settings menu).
    Issue #10: Allow user to manage external service preferences.
    """
    print("\n" + "-"*50)
    print("External Service Settings")
    print("-"*50)
    print("1. View current permission status")
    print("2. Grant/Update external service permission")
    print("3. Revoke external service permission")
    print("4. Back to main menu")
    print("-"*50)
    
    choice = input("Choose an option (1-4): ").strip()
    
    if choice == '1':
        # View current status
        from external_services.permission_manager import ExternalServicePermission
        permission_manager = ExternalServicePermission('default_user')
        has_permission = permission_manager.has_permission('LLM')
        
        print("\n" + "="*50)
        if has_permission is None:
            print("Status: No permission set (will be asked on first analysis)")
        elif has_permission:
            print("Status: External service permission GRANTED")
            print("  Enhanced analysis is enabled")
        else:
            print("Status: External service permission DECLINED")
            print("  Local analysis only (data stays private)")
        print("="*50)
        
    elif choice == '2':
        # Grant/Update permission
        request_external_service_permission('default_user', 'LLM')
        
    elif choice == '3':
        # Revoke permission
        from external_services.external_service_prompt import ExternalServicePrompt
        confirm = input("\nAre you sure you want to revoke external service permission? (yes/no): ").strip().lower()
        if confirm in ['yes', 'y']:
            ExternalServicePrompt.store_permission('default_user', 'LLM', False)
            print("\nExternal service permission has been REVOKED")
            print("  Local analysis will be used (your data stays private)")
        else:
            print("\nAction cancelled")
    
    elif choice == '4':
        return
    else:
        print("Invalid choice. Please enter 1, 2, 3, or 4.")

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

    collab_manager = CollaborativeManager()
    
    # Check/request collaborative consent
    if not collab_manager.request_collaborative_if_needed():
        print("Collaborative not granted. Doing individual.")
    else:
        print("Collaborative granted. Doing collaborative and individual.")

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
        print("\n" + "="*70)
        print("MINING DIGITAL WORK ARTIFACTS - Main Menu")
        print("="*70)
        print("1. Upload a ZIP file")
        print("2. List stored projects")
        print("3. Analyze project metrics")
        print("4. Summarize a project (basic summary)")
        print("5. Analyze a project (detailed analysis with local fallback)")
        print("6. Rank all projects")
        print("7. Manage external service settings")
        print("8. Cleanup insights for a project")
        print("9. Exit")
        print("="*70)
        
        choice = input("Choose an option (1-9): ").strip()
        
        if choice == '1':
            filepath = input("Enter the path to your zip file: ")
            add_file_to_db(filepath)
            
        elif choice == '2':
            list_projects()
            
        elif choice == '3':
            selected_project = _select_project_interactive("Analyze project metrics")
            if selected_project:
                analyze_project_from_db(int(selected_project['id']))
                
        elif choice == '4':
            summarize_project_menu()
            
        elif choice == '5':
            analyze_project_menu()
            
        elif choice == '6':
            print("\nRanking all projects...")
            ranked = rank_all_projects()
            display_rankings(ranked)
            input("\nPress Enter to continue...")
            
        elif choice == '7':
            manage_external_services_menu()
            
        elif choice == '8':
            pid = input("Enter project ID to clean: ").strip()
            if pid.isdigit():
                confirm = input(
                    f"Delete insights and the uploaded file for project {pid}? "
                    f"This cannot be undone. (y/n): "
                ).strip().lower()
                if confirm in ('y', 'yes'):
                    m, f, p = delete_insights(int(pid))
                    print(f"Deleted: project_metrics={m}, file_contents={f}, uploaded_files={p}")
                else:
                    print("Cancelled.")
            else:
                print("Invalid project ID.")
                
        elif choice == '9':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1-9.")

if __name__ == "__main__":
    main()