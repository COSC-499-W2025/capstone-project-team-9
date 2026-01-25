"""
Project display and selection UI functions.
Handles all user interface interactions for listing and selecting projects.
"""
from project_manager import list_projects, list_project_files
from project_summarizer import get_available_projects
from account.user_manager import AuthManager
from api.client import get_api_client


def select_project_interactive(title: str):
    """
    Unified project selection UI. Returns selected project dict or None.
    
    Args:
        title: Title to display for the selection menu
        
    Returns:
        Selected project dictionary or None if cancelled
    """
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
        # Handle both datetime objects and ISO string dates from API
        created_at = project.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                # Parse ISO string date (YYYY-MM-DD or full ISO format)
                created_date = created_at.split('T')[0] if 'T' in created_at else created_at
            else:
                # datetime object
                created_date = created_at.strftime("%Y-%m-%d")
        else:
            created_date = "Unknown"
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


def list_projects_menu():
    """
    Handle the list projects menu option.
    Lists all stored projects and allows viewing files within a selected project.
    Data Isolation: Uses current user's username to filter projects.
    """
    # Get current logged-in user for data isolation
    current_username = AuthManager.get_current_username()
    if not current_username:
        print("Error: No user is currently logged in.")
        return
    
    # Use API to get projects
    try:
        client = get_api_client()
        api_response = client.get_projects(user_name=current_username)
        projects_data = api_response.get('projects', [])
        
        # Convert API response to format expected by existing code
        projects = []
        for proj in projects_data:
            projects.append({
                'id': proj['id'],
                'filename': proj['filename'],
                'created_at': proj.get('created_at'),  # Will be string from API
                'file_count': proj.get('file_count', 0),
                'has_thumbnail': proj.get('has_thumbnail', False)
            })
    except Exception as e:
        # Fallback to direct call if API fails
        print(f"API call failed, using direct database access: {e}")
        projects = list_projects(current_username)
    
    # Display projects if any exist
    if not projects:
        print("No projects found in database.")
        return
    
    print("-"*80)
    print("Stored Projects (Alphabetical Order)")
    print("-"*80)
    
    for i, proj in enumerate(projects, 1):
        # Handle datetime conversion for display
        created_at = proj.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                # Parse ISO string date (YYYY-MM-DD or full ISO format)
                created_date = created_at.split('T')[0] if 'T' in created_at else created_at
            else:
                # datetime object
                created_date = created_at.strftime("%Y-%m-%d")
        else:
            created_date = "Unknown"
        
        thumbnail_label = "Yes" if proj.get('has_thumbnail', False) else "No"
        print(f"\n{i}. {proj['filename']}")
        print(f"   ID: {proj['id']}, Created: {created_date}, Files: {proj.get('file_count', 0)}, Thumbnail: {thumbnail_label}")
    
    print("\n" + "-"*80)
    print(f"Total projects: {len(projects)}")
    print("-"*80)
    
    if projects:
        print("\nWould you like to view files for a specific project or delete one?")
        view_choice = input(
            "Enter project number to view files, 'd' to delete a project, or 'q' to go back: "
        ).strip()
        if view_choice.lower() == 'q':
            return
        if view_choice.lower() == 'd':
            from project_manager import delete_project
            project_num_input = input(f"Enter project number to delete (1-{len(projects)}): ").strip()
            if project_num_input.isdigit():
                project_num = int(project_num_input)
                if 1 <= project_num <= len(projects):
                    selected_project = projects[project_num - 1]
                    project_id = selected_project['id']
                    confirm = input(
                        f"Delete '{selected_project['filename']}' (ID {project_id}) and all related data? "
                        "This cannot be undone. (y/n): "
                    ).strip().lower()
                    if confirm in ('y', 'yes'):
                        result = delete_project(project_id, current_username)
                        if result.get("success"):
                            deleted = result.get("deleted", {})
                            print(
                                "Deleted records: "
                                f"project_metrics={deleted.get('project_metrics', 0)}, "
                                f"analysis_results={deleted.get('analysis_results', 0)}, "
                                f"project_rankings={deleted.get('project_rankings', 0)}, "
                                f"file_contents={deleted.get('file_contents', 0)}, "
                                f"uploaded_files={deleted.get('uploaded_files', 0)}"
                            )
                            if result.get("file_deleted"):
                                print(f"Removed upload file: {result.get('filepath')}")
                        else:
                            print(f"Failed to delete project: {result.get('error', 'Unknown error')}")
                    else:
                        print("Cancelled.")
                else:
                    print(f"Please enter a number between 1 and {len(projects)}")
            else:
                print("Please enter a valid number.")
            return
        try:
            project_num = int(view_choice)
            if 1 <= project_num <= len(projects):
                selected_project = projects[project_num - 1]
                print(f"\n" + "-"*80)
                print(f"Files in project: {selected_project['filename']}")
                print("-"*80)
                # Data Isolation: Pass user_name to verify project ownership
                files = list_project_files(selected_project['id'], current_username)
                if files:
                    for i, file_path in enumerate(files, 1):
                        print(f"{i}. {file_path}")
                    print("-"*80)
                    print(f"Total files: {len(files)}")
                input("\nPress Enter to continue...")
            else:
                print(f"Please enter a number between 1 and {len(projects)}")
        except ValueError:
            print("Please enter a valid number, 'd', or 'q'")
