from config.db_config import get_connection
from upload_file import add_file_to_db
from project_manager import list_projects
from consent.consent_manager import ConsentManager
from collaborative.collaborative_manager import CollaborativeManager
from project_summarizer import summarize_project, get_available_projects
from external_services.external_service_prompt import request_external_service_permission
from project_analyzer import analyze_project_by_id


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


def manage_external_services_menu():
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
            print("\n✓ External service permission has been REVOKED")
            print("  Local analysis will be used (your data stays private)")
        else:
            print("\n✗ Action cancelled")
    
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

    # Test database connection
    conn = get_connection()
    if conn:
        print("Database is connected!")
        conn.close()
    else:
        print("Database is not connected.")
        return
    
    # Request external service permission (Issue #10)
    print("\n" + "="*70)
    print("EXTERNAL SERVICE CONFIGURATION")
    print("="*70)
    request_external_service_permission('default_user', 'LLM')
    
    # Main menu interface
    while True:
        print("\n" + "="*70)
        print("MINING DIGITAL WORK ARTIFACTS - Main Menu")
        print("="*70)
        print("1. Upload a ZIP file")
        print("2. List stored projects")
        print("3. Summarize a project (basic summary)")
        print("4. Analyze a project (detailed analysis with local fallback)")
        print("5. Manage external service settings")
        print("6. Exit")
        print("="*70)
        
        choice = input("Choose an option (1-6): ").strip()
        
        if choice == '1':
            filepath = input("Enter the path to your zip file: ")
            add_file_to_db(filepath)
            
        elif choice == '2':
            list_projects()
            
        elif choice == '3':
            summarize_project_menu()
            
        elif choice == '4':
            # Issue #10: Main menu option for analysis with local fallback
            analyze_project_menu()
            
        elif choice == '5':
            manage_external_services_menu()
            
        elif choice == '6':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")

    # Initialize CollaborativeManager
    collab_manager = CollaborativeManager()
    
    # Check/request collaborative consent
    if not collab_manager.request_collaborative_if_needed():
        print("Collaborative not granted. Doing individual.")
    else:
        print("Collaborative granted. Doing collaborative and individual.")


if __name__ == "__main__":
    main()