"""Menu handlers for CLI interactions."""
import os
import subprocess
import sys
from project_display import select_project_interactive, list_projects_menu
from project_summarizer import summarize_project
from project_analyzer import analyze_project_by_id
from analysis.key_metrics import analyze_project_from_db
from analysis.project_ranking import rank_all_projects, display_rankings, rank_and_summarize_top_projects, save_rankings_with_summaries
from analysis.ranking_storage import (
    get_stored_rankings, 
    get_stored_ranking_by_project_id,
    update_ranking_score,
    update_ranking_summary,
    update_ranking_position
)
from external_services.external_service_prompt import request_external_service_permission, ExternalServicePrompt
from external_services.permission_manager import ExternalServicePermission
from collaborative.identify_contributors import identify_contributors
from database.user_preferences import get_user_git_username, update_user_git_username
from account.user_manager import AuthManager
from tools.cleanup_insights import delete_insights
from cli.display import display_success, display_error
from cli.cli_output import print_header, print_section, print_success, print_error, pause, safe_input
from .menu_runner import MenuSpec, run_menu

def analyze_project_menu():
    """
    Handle the project analysis menu.
    This is the main menu for Issue #10: Analysis if User Declines Outside Sources.
    """
    # Get current user for data isolation
    current_user = AuthManager.get_current_username()
    if not current_user:
        print_error("Error: No user is currently logged in.")
        return
    
    selected_project = select_project_interactive("Project Analysis (with Local Fallback)")
    
    if not selected_project:
        return
    
    print(f"\nAnalyzing: {selected_project['filename']}")
    print("Please wait...")
    # Tell user the analysis mode
    print("Analysis Mode: PRIVACY MODE (local fallback if external services declined)")
    
    # Perform analysis (respects user's external service permission)
    analyze_project_by_id(selected_project['id'], user_id=current_user)
    
    # Ask if user wants to continue
    continue_choice = safe_input("\nPress Enter to continue or 'q' to quit: ", default = "").strip()
    if continue_choice.lower() == 'q':
        return


def analysis_menu():
    permission_manager = ExternalServicePermission(AuthManager.get_current_username() or 'default_user')
    if permission_manager.has_permission('LLM') is True:
        handle_analyze_metrics_and_summary()
    else:
        analyze_project_menu()


def resume_menu():
    """Unified resume menu that consolidates all resume-related options."""
    options = [
        "Generate Resume",
        "Export Resume",
        "Delete Resume",
        "Back to main menu",
    ]

    spec = MenuSpec(
        title="RESUME OPTIONS",
        options=options,
        prompt="Choose an option",
    )

    handlers = {
        "1": lambda: handle_generate_resume(),
        "2": lambda: handle_view_resume(),
        "3": lambda: handle_delete_resume(),
        "4": "BACK",
    }

    run_menu(spec, handlers, pause_after_action=False)
    return

def project_menu():
    """Unified menu to manage projects"""
    options = [
        "Upload a ZIP file",
        "List stored projects",
        "Add a thumbnail to a project",
        "Delete a project",
        "Back to main menu",
    ]

    spec = MenuSpec(
        title="PROJECTS OPTIONS",
        options=options,
        prompt="Choose an option",
    )

    handlers = {
        "1": lambda: handle_upload_file(),
        "2": lambda: handle_list_projects(),
        "3": lambda: handle_add_project_thumbnail(),
        "4": lambda: handle_cleanup_insights(),
        "5": "BACK",
    }

    run_menu(spec, handlers, pause_after_action=False)
    return


def settings_menu(consent_manager, collab_manager):
    """Unified settings menu that consolidates all settings-related options."""
    from cli.user_menus import user_account_menu

    options = [
        "External Service Settings",
        "User Preferences",
        "User Account",
        "Back to main menu",
    ]

    spec = MenuSpec(
        title="SETTINGS",
        options=options,
        prompt="Choose an option",
    )

    handlers = {
        "1": lambda: manage_external_services_menu(),
        "2": lambda: ask_user_preferences(consent_manager, collab_manager, False),
        "3": lambda: user_account_menu(),
        "4": "BACK",
    }

    run_menu(spec, handlers, pause_after_action=False)
    return


def manage_external_services_menu():
    """Manage external service permissions (settings menu)."""
    current_user = AuthManager.get_current_username() or 'default_user'

    def view_status():
        permission_manager = ExternalServicePermission(current_user)
        has_permission = permission_manager.has_permission('LLM')
        status_messages = {
            None: "No permission set (will be asked on first analysis)",
            True: "External service permission GRANTED\n  Enhanced analysis is enabled",
            False: "External service permission DECLINED\n  Local analysis only (data stays private)",
        }
        print("\n" + "=" * 50)
        print(f"Status: {status_messages[has_permission]}")
        print("=" * 50)

    def grant_or_update():
        # Keep existing behavior
        request_external_service_permission(current_user, 'LLM')

    def revoke_permission():
        confirm = safe_input("\nAre you sure you want to revoke external service permission? (yes/no): ", default= "").strip().lower()
        if confirm in ['yes', 'y']:
            ExternalServicePrompt.store_permission(current_user, 'LLM', False)
            print("\nExternal service permission has been REVOKED")
            print("  Local analysis will be used (your data stays private)")
        else:
            print("\nAction cancelled")

    options = [
        "View current permission status",
        "Grant/Update external service permission",
        "Revoke external service permission",
        "Back to main menu",
    ]

    spec = MenuSpec(
        title="External Service Settings",
        options=options,
        prompt="Choose an option",
        show_header=True,
    )

    handlers = {
        "1": lambda: (view_status() or "BACK"),
        "2": lambda: (grant_or_update() or "BACK"),
        "3": lambda: (revoke_permission() or "BACK"),
        "4": "BACK",
    }

    # Loop until user chooses BACK (run_menu will keep looping internally)
    run_menu(spec, handlers, pause_after_action=False)
    return



def ask_user_preferences(consent_manager, collab_manager, is_start):
    """Handle user preferences menu."""
    just_changed = False
    user_name = collab_manager.user_name
    
    # Check/request user consent first
    if not is_start and consent_manager.has_access():
        # Allow user to withdraw consent
        response = safe_input("\nWould you like to withdraw consent? (yes/no): ", default = "").strip().lower()
        if response in ['yes', 'y']:
            consent_manager.withdraw()
    # Request consent if needed (for is_start=True or if consent was withdrawn)
    else:
        consent_manager.request_consent_if_needed()
    
    prefs = collab_manager.get_preferences()
    if prefs and prefs[1] and not is_start: 
        while True:
            response = safe_input("\nWould you like to not include collaborative work? (yes/no): ", default = "").strip().lower()
            if response in ['yes', 'y']:
                collab_manager.update_collaborative(False)
                print("\nCollaborative not granted. Thank you!")
                break
            elif response in ['no', 'n']:
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
    else:
        # Check/request collaborative consent
        if not collab_manager.request_collaborative_if_needed():
            print("Collaborative not granted. Doing individual.")
        else:
            print("Collaborative granted. Doing colabrative and individual.")
            git_username = get_user_git_username(user_name)
            if not git_username:
                response = safe_input("\nWhat is you GitHub user name: ", default = "").strip()
                update_user_git_username(user_name, response)
                just_changed = True
            print("\nYour github username is:"+str(get_user_git_username(user_name)))
            # Path to the ZIP file
            zip_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../fixtures/sample-projects/test.zip")
            )
            ic = identify_contributors(zip_path=zip_path)
            # Extract the repo
            repo_path = ic.extract_repo()
            if repo_path is None:
                print("No git repository found in the ZIP.")
                return
            # Get the full contribution profile
            profile = ic.get_full_contribution_profile()
            ic.cleanup()
            
    if not just_changed and get_user_git_username(user_name) is not None and not is_start:
        while True:
            response = safe_input("\nWould you like to change you GitHub username? (y/n) ", default = "").strip().lower()
            if response in ['yes', 'y']:
                new_username = safe_input("\nWhat is you GitHub user name: ", default = "").strip()
                update_user_git_username(user_name, new_username)
                break
            elif response in ['no', 'n']:
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")


def handle_upload_file():
    """Handle file upload menu option."""
    filepath = safe_input("Enter the path to your zip file: ", default = "").strip()
    from api.client import get_api_client
    from upload_file import UploadResult
    from account.user_manager import AuthManager
    
    # Get current logged in user
    current_username = AuthManager.get_current_username()
    
    try:
        client = get_api_client()
        api_result = client.upload_project(filepath, user_name=current_username)
        
        # Convert API response to UploadResult for compatibility
        result = UploadResult(
            success=api_result.get('success', False),
            message=api_result.get('message', ''),
            error_type=api_result.get('error_type'),
            data=api_result.get('data', {})
        )
        
        if result.success:
            display_success(result)
        else:
            display_error(result)
    except Exception as e:
        # Fallback to direct call if API fails
        from upload_file import add_file_to_db
        result = add_file_to_db(filepath, user_name=current_username)
        if result.success:
            display_success(result)
        else:
            display_error(result)


def handle_add_project_thumbnail():
    """Handle adding a thumbnail image to an existing project."""
    selected_project = select_project_interactive("Add thumbnail to project")
    if not selected_project:
        return

    thumbnail_path = safe_input("Enter the path to the thumbnail image: ", default = "").strip()
    if not thumbnail_path:
        print("No thumbnail path provided.")
        return

    from upload_file import add_thumbnail_to_project
    result = add_thumbnail_to_project(int(selected_project['id']), thumbnail_path)

    if result.success:
        display_success(result)
    else:
        display_error(result)



def handle_list_projects():
    """Handle list projects menu option."""
    list_projects_menu()


def handle_analyze_metrics_and_summary():
    """Combined key metrics + project summary flow."""
    print("\n" + "-"*50)
    print("Analyze project (metrics + summary)")
    print("-"*50)
    selected_project = select_project_interactive("Analyze project (metrics + summary)")
    if not selected_project:
        return

    project_id = int(selected_project['id'])
    filename = selected_project['filename']

    print(f"\nAnalyzing: {filename}")
    print("Please wait...")
    # Tell user the analysis mode, different from analyze_project_menu
    print("Analysis Mode: FULL (metrics + summary)")

    # print Key Metrics (original option 3)
    analyze_project_from_db(project_id)

    # Data Isolation: Get current user for project ownership verification
    current_username = AuthManager.get_current_username()
    summary_text = summarize_project(project_id, user_name=current_username)
    print(summary_text)

    safe_input("\nPress Enter to continue...")

def handle_rank_projects():
    """Handle rank all projects menu option."""
    print("\nRanking all projects...")
    # Data Isolation: Get current user to rank only their projects
    current_username = AuthManager.get_current_username()
    ranked = rank_all_projects(user_name=current_username)
    display_rankings(ranked)

    if ranked:
        print("\n" + "-"*80)
        save_choice = safe_input("Would you like to save these rankings to the database? (y/n): ", default = "").strip().lower()
        if save_choice in ['y', 'yes']:
            generate_summaries = safe_input("Generate summaries for all projects? (y/n): ", default = "").strip().lower()
            save_rankings_with_summaries(ranked, generate_summaries in ['y', 'yes'])

    safe_input("\nPress Enter to continue...")


def handle_zip_success_report():
    """Show a success report for a selected zip project."""
    from analysis import analyze_zip_project
    from project_manager import get_project_by_id
    from parsing.file_contents_manager import get_zip_file
    import tempfile

    print("\n" + "-"*50)
    print("Project Success Report (ZIP)")
    print("-"*50)
    selected_project = select_project_interactive("Select project for success report")
    if not selected_project:
        return

    project_id = int(selected_project["id"])
    project = get_project_by_id(project_id)
    if not project:
        print("Project not found.")
        pause()
        return

    zip_bytes = get_zip_file(project_id)
    if not zip_bytes:
        print("ZIP file not found for this project.")
        pause()
        return

    try:
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            tmp_file.write(zip_bytes)
            temp_zip_path = tmp_file.name
        result = analyze_zip_project(temp_zip_path)
    except Exception as exc:
        print(f"Failed to analyze ZIP: {exc}")
        pause()
        return
    finally:
        if "temp_zip_path" in locals() and os.path.exists(temp_zip_path):
            try:
                os.remove(temp_zip_path)
            except OSError:
                pass

    success = result.get("success", {})
    signals = result.get("signals", {})
    evidence = result.get("evidence", {})

    print("\n" + "="*70)
    print(f"Project: {result.get('project_name')}")
    print(f"Archive: {result.get('zip_path')}")
    print(f"Status : {success.get('status')}")
    print(f"Score  : {success.get('score')} (confidence {success.get('confidence')})")
    print(f"Result : {'SUCCESS' if success.get('is_successful') else 'NOT SUCCESSFUL'}")
    print("="*70)

    print("\nSignals:")
    for key in sorted(signals.keys()):
        print(f"- {key}: {signals[key]}")

    if evidence:
        print("\nEvidence:")
        if evidence.get("entrypoints"):
            print(f"- entrypoints: {', '.join(evidence['entrypoints'])}")
        if evidence.get("dependency_manifests"):
            print(f"- dependencies: {', '.join(evidence['dependency_manifests'])}")
        if evidence.get("test_files"):
            print(f"- tests: {', '.join(evidence['test_files'][:10])}")
        if evidence.get("readme_file"):
            print(f"- readme: {evidence['readme_file']}")
        if evidence.get("incomplete_markers"):
            print(f"- incomplete_markers: {', '.join(evidence['incomplete_markers'])}")

    pause()


def handle_rank_and_summarize_projects():
    """Handle rank and summarize top 3 projects menu option."""
    rank_and_summarize_top_projects()
    
    # Ask if user wants to save results
    print("\n" + "-"*80)
    save_choice = safe_input("Would you like to save these rankings and summaries to the database? (y/n): ", default = "").strip().lower()
    if save_choice in ['y', 'yes']:
        # Data Isolation: Get current user to rank only their projects
        current_username = AuthManager.get_current_username()
        ranked = rank_all_projects(user_name=current_username)
        if ranked:
            # Generate summaries for all projects (not just top 3)
            generate_all = safe_input("Generate summaries for ALL projects (not just top 3)? (y/n): ", default = "").strip().lower()
            save_rankings_with_summaries(ranked, generate_all in ['y', 'yes'])
    
    pause()


def handle_view_edit_rankings():
    """Handle view and edit stored rankings menu option."""
    print("\n" + "="*80)
    print("VIEW AND EDIT STORED RANKINGS")
    print("="*80)
    
    stored_rankings = get_stored_rankings()
    
    if not stored_rankings:
        print("\nNo stored rankings found. Please rank projects first and save them.")
        pause()
        return
    
    # Display stored rankings
    print("\n" + "-"*80)
    print(f"{'Rank':<6} {'Project ID':<12} {'Score':<10} {'Project Name':<50}")
    print("-"*80)
    
    for ranking in stored_rankings:
        filename = ranking.get('ranking_data', {}).get('filename', 'Unknown')
        filename = filename[:48] + ".." if len(filename) > 50 else filename
        print(f"{ranking['rank_position']:<6} {ranking['project_id']:<12} {ranking['score']:<10} {filename:<50}")
    
    print("-"*80)
    
    # Menu for editing
    while True:
        print("\nOptions:")
        print("1. View full details for a project")
        print("2. Edit score for a project")
        print("3. Edit summary for a project")
        print("4. Clean error summaries from database")
        print("5. Back to main menu")
        
        choice = safe_input("\nChoose an option (1-5): ", default = "").strip()
        
        if choice == '1':
            # View full details
            project_id = safe_input("Enter project ID to view: ", default = "").strip()
            if project_id.isdigit():
                ranking = get_stored_ranking_by_project_id(int(project_id))
                if ranking:
                    print("\n" + "="*80)
                    print(f"PROJECT RANKING DETAILS")
                    print("="*80)
                    print(f"Project ID: {ranking['project_id']}")
                    print(f"Rank Position: {ranking['rank_position']}")
                    print(f"Score: {ranking['score']}")
                    print(f"Created At: {ranking['created_at']}")
                    print(f"Updated At: {ranking['updated_at']}")
                    print("\nSummary:")
                    print("-"*80)
                    if ranking['summary']:
                        print(ranking['summary'])
                    else:
                        print("(No summary available)")
                    print("="*80)
                else:
                    print(f"\nNo stored ranking found for project ID {project_id}")
            else:
                print("Invalid project ID.")
        
        elif choice == '2':
            # Edit score
            project_id = safe_input("Enter project ID to edit score: ", default = "").strip()
            if project_id.isdigit():
                new_score = safe_input("Enter new score: ", default = "").strip()
                try:
                    score_float = float(new_score)
                    if update_ranking_score(int(project_id), score_float):
                        print(f"\n Successfully updated score for project {project_id} to {score_float}")
                    else:
                        print(f"\n Failed to update score. Project {project_id} may not exist in stored rankings.")
                except ValueError:
                    print("Invalid score. Please enter a number.")
            else:
                print("Invalid project ID.")
        
        elif choice == '3':
            # Edit summary
            project_id = safe_input("Enter project ID to edit summary: ", default = "").strip()
            if project_id.isdigit():
                ranking = get_stored_ranking_by_project_id(int(project_id))
                if ranking:
                    print("\nCurrent summary:")
                    print("-"*80)
                    print(ranking['summary'] if ranking['summary'] else "(No summary)")
                    print("-"*80)
                    print("\nEnter new summary (press Enter on empty line to finish, or 'cancel' to cancel):")
                    new_summary_lines = []
                    while True:
                        line = safe_input("", default = "").strip()
                        if line.strip().lower() == 'cancel':
                            print("Cancelled.")
                            break
                        if line == "" and new_summary_lines:
                            # Empty line after content means done
                            break
                        new_summary_lines.append(line)
                    
                    if new_summary_lines and new_summary_lines[0].strip().lower() != 'cancel':
                        new_summary = "\n".join(new_summary_lines)
                        if update_ranking_summary(int(project_id), new_summary):
                            print(f"\n Successfully updated summary for project {project_id}")
                        else:
                            print(f"\n Failed to update summary.")
                else:
                    print(f"\nNo stored ranking found for project ID {project_id}")
            else:
                print("Invalid project ID.")
        
        elif choice == '4':
            # Clean error summaries
            from analysis.ranking_storage import clean_error_summaries
            confirm = safe_input("\nThis will remove all error messages from stored summaries. Continue? (y/n): ", default = "").strip().lower()
            if confirm in ['y', 'yes']:
                if clean_error_summaries():
                    print("\n✓ Error summaries cleaned successfully")
                else:
                    print("\n✗ Failed to clean error summaries")
            else:
                print("Cancelled.")
        
        elif choice == '5':
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")


def handle_cleanup_insights():
    """Handle delete project data menu option."""
    pid = safe_input("Enter project ID to delete data for: ", default = "").strip()
    if pid.isdigit():
        from project_manager import get_project_by_id

        project_id = int(pid)
        
        # Get current logged-in user for data isolation
        current_username = AuthManager.get_current_username()
        if not current_username:
            print("Error: You must be logged in to delete projects.")
            return
        
        # Verify project exists and belongs to current user
        project = get_project_by_id(project_id, user_name=current_username)
        if not project:
            print(f"No project found with ID {project_id} or you don't have permission to delete it.")
            return

        confirm = safe_input(
            f"Delete all data for project {pid}? "
            f"This cannot be undone. (y/n): "
        ).strip().lower()
        if confirm in ('y', 'yes'):
            try:
                m, f, p = delete_insights(project_id, user_name=current_username)
                print(f"Deleted: project_metrics={m}, file_contents={f}, uploaded_files={p}")
            except PermissionError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Error deleting project: {e}")
        else:
            print("Cancelled.")
    else:
        print("Invalid project ID.")


def portfolio_menu():
    """Wrapper function that imports and calls portfolio_menu from portfolio.portfolio_display."""
    from portfolio.portfolio_display import portfolio_menu as _portfolio_menu
    _portfolio_menu()
    
def handle_generate_resume():
    """Handle resume generation menu option."""
    from resume.resume_manager import ResumeManager
    from account.user_manager import AuthManager
    
    print("\n" + "-"*70)
    print("Generate Resume")
    print("-"*70)
    
    # Get logged-in user
    if not AuthManager.is_user_logged_in():
        print("\nError: You must be logged in to generate a resume.")
        pause()
        return
    
    current_user = AuthManager.get_current_user()
    user_id = current_user.get('user_name', 'default_user') if current_user else 'default_user'
    
    # Check if resume already exists
    if ResumeManager.resume_exists(user_id):
        print("\nA resume already exists for your account.")
        regenerate = safe_input("Would you like to regenerate it? (y/n): ", default = "").strip().lower()
        if regenerate not in ('y', 'yes'):
            print("Cancelled.")
            return
    
    # Ask how many top projects to include
    while True:
        top_count = safe_input("\nHow many top projects to include in resume? (1-10, default 5): ", default = "").strip()
        if not top_count:
            top_count = 5
            break
        if top_count.isdigit() and 1 <= int(top_count) <= 10:
            top_count = int(top_count)
            break
        print("Please enter a number between 1 and 10.")
    
    print(f"\nGenerating resume with top {top_count} projects...")
    print("This may take a moment...")
    
    # Generate resume
    resume_data = ResumeManager.generate_user_resume(user_id, top_projects_count=top_count)
    
    if not resume_data:
        print("\nFailed to generate resume. Please ensure you have uploaded projects.")
        pause()
        return
    
    # Store resume
    success = ResumeManager.store_user_resume(user_id, resume_data)
    
    if success:
        print("\n" + "="*70)
        print("Resume generated successfully!")
        print("="*70)
        print(f"Total projects analyzed: {resume_data['total_projects_analyzed']}")
        print(f"Top projects included: {resume_data['top_projects_displayed']}")
        print(f"Skills identified: {len(resume_data['all_skills'])}")
        
        summary_stats = resume_data.get('summary_stats', {})
        if summary_stats:
            print(f"Total lines of code: {summary_stats.get('total_lines_of_code', 0):,}")
            print(f"Total files: {summary_stats.get('total_files', 0):,}")
            print(f"Languages: {summary_stats.get('unique_languages', 0)}")
            print(f"Frameworks: {summary_stats.get('unique_frameworks', 0)}")
        
        print("\nUse 'View Resume' option to see the full resume.")
    else:
        print("\nFailed to save resume to database.")
    
    pause()


def handle_view_resume():
    """Handle resume viewing menu option."""
    from resume.resume_manager import ResumeManager
    from resume.resume_formatter import ResumeFormatter
    from account.user_manager import AuthManager
    
    print("\n" + "-"*70)
    print("View Resume")
    print("-"*70)
    
    # Get logged-in user
    if not AuthManager.is_user_logged_in():
        print("\nError: You must be logged in to view your resume.")
        pause()
        return
    
    current_user = AuthManager.get_current_user()
    user_id = current_user.get('user_name', 'default_user') if current_user else 'default_user'
    
    # Check if resume exists
    if not ResumeManager.resume_exists(user_id):
        print("\nNo resume found. Please generate a resume first.")
        pause()
        return
    
    # Retrieve resume
    resume_record = ResumeManager.get_user_resume(user_id)
    
    if not resume_record:
        print("\nFailed to retrieve resume from database.")
        pause()
        return
    
    resume_data = resume_record['resume_data']
    
    # Ask for format
    print("\nAvailable formats:")
    print("1. Text (default)")
    print("2. Markdown")
    print("3. JSON")
    print("4. Export as PDF")
    
    format_choice = safe_input("\nSelect format (1-4, default 1): ", default = "").strip()
    
    if format_choice == '4':
        # PDF export
        _handle_pdf_export(resume_data)
    else:
        # Console display formats
        format_map = {
            '1': 'text',
            '2': 'markdown',
            '3': 'json',
            '': 'text'
        }
        
        selected_format = format_map.get(format_choice, 'text')
        
        # Format and display resume
        formatted_resume = ResumeFormatter.get_formatted_resume(resume_data, selected_format)
        
        if formatted_resume:
            print("\n" + "="*70)
            print(formatted_resume)
            print("="*70)
        else:
            print("\nFailed to format resume.")
    
    pause()


def _handle_pdf_export(resume_data):
    """
    Handle PDF export functionality for resume.
    
    Args:
        resume_data: Resume data dictionary to export
    """
    from resume.resume_formatter import ResumeFormatter
    
    print("\n" + "-"*70)
    print("Export Resume as PDF")
    print("-"*70)
    
    # Get default filename
    default_filename = "resume.pdf"
    
    # Prompt for filename
    print(f"\nDefault filename: {default_filename}")
    print("The file will be saved in the project root directory.")
    
    filename = safe_input(f"Enter filename (press Enter for default): ", default = "").strip()
    
    if not filename:
        filename = default_filename
    
    # Ensure .pdf extension
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    
    # Determine output path (project root directory)
    # Get the directory where the script is located and go up to project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up from cli/ to src/ to project root
    project_root = os.path.dirname(os.path.dirname(current_dir))
    output_path = os.path.join(project_root, filename)
    
    print(f"\nGenerating PDF...")
    print(f"Output path: {output_path}")
    
    # Generate PDF
    success = ResumeFormatter.format_pdf(resume_data, output_path)
    
    if success:
        print("\n" + "="*70)
        print("PDF generated successfully!")
        print("="*70)
        print(f"File saved to: {output_path}")
        
        # Verify file exists and show size
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"File size: {file_size:,} bytes")
    else:
        print("\nFailed to generate PDF.")
        print("Make sure reportlab is installed: pip install reportlab")


def handle_delete_resume():
    """Handle resume deletion menu option."""
    from resume.resume_manager import ResumeManager
    from account.user_manager import AuthManager
    
    print("\n" + "-"*70)
    print("Delete Resume")
    print("-"*70)
    
    # Get logged-in user
    if not AuthManager.is_user_logged_in():
        print("\nError: You must be logged in to delete your resume.")
        pause()
        return
    
    current_user = AuthManager.get_current_user()
    user_id = current_user.get('user_name', 'default_user') if current_user else 'default_user'
    
    # Check if resume exists
    if not ResumeManager.resume_exists(user_id):
        print("\nNo resume found.")
        pause()
        return
    
    # Confirm deletion
    confirm = safe_input("\nAre you sure you want to delete your resume? This cannot be undone. (y/n): ", default = "").strip().lower()
    
    if confirm in ('y', 'yes'):
        success = ResumeManager.delete_user_resume(user_id)
        
        if success:
            print("\nResume deleted successfully.")
        else:
            print("\nFailed to delete resume.")
    else:
        print("\nCancelled.")
    
    pause()
