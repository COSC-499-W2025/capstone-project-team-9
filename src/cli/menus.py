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
from tools.cleanup_insights import delete_insights
from cli.display import display_success, display_error

def analyze_project_menu():
    """
    Handle the project analysis menu.
    This is the main menu for Issue #10: Analysis if User Declines Outside Sources.
    """
    selected_project = select_project_interactive("Project Analysis (with Local Fallback)")
    
    if not selected_project:
        return
    
    print(f"\nAnalyzing: {selected_project['filename']}")
    print("Please wait...")
    # Tell user the analysis mode
    print("Analysis Mode: PRIVACY MODE (local fallback if external services declined)")
    
    # Perform analysis (respects user's external service permission)
    analyze_project_by_id(selected_project['id'])
    
    # Ask if user wants to continue
    continue_choice = input("\nPress Enter to continue or 'q' to quit: ").strip()
    if continue_choice.lower() == 'q':
        return


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
        permission_manager = ExternalServicePermission()
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


def ask_user_preferences(consent_manager, collab_manager, is_start):
    """Handle user preferences menu."""
    just_changed = False
    
    # Check/request user consent first
    if not is_start and consent_manager.has_access():
        # Allow user to withdraw consent
        response = input("\nWould you like to withdraw consent? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            consent_manager.withdraw()
    # Request consent if needed (for is_start=True or if consent was withdrawn)
    else:
        consent_manager.request_consent_if_needed()
    
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
        # Check/request collaborative consent
        if not collab_manager.request_collaborative_if_needed():
            print("Collaborative not granted. Doing individual.")
        else:
            print("Collaborative granted. Doing colabrative and individual.")
            git_username = get_user_git_username()
            if not git_username:
                response = input("\nWhat is you GitHub user name: ").strip()
                update_user_git_username(response)
                just_changed = True
            print("\nYour github username is:"+str(get_user_git_username()))
            # Path to the ZIP file
            zip_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../test.zip"))
            ic = identify_contributors(zip_path=zip_path)
            # Extract the repo
            repo_path = ic.extract_repo()
            if repo_path is None:
                print("No git repository found in the ZIP.")
                return
            # Get the full contribution profile
            profile = ic.get_full_contribution_profile()
            ic.cleanup()
            
    if not just_changed and get_user_git_username() is not None and not is_start:
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


def handle_upload_file():
    """Handle file upload menu option."""
    filepath = input("Enter the path to your zip file: ")
    from upload_file import add_file_to_db
    from account.user_manager import AuthManager
    
    # Get current logged in user
    current_username = AuthManager.get_current_username()
    
    result = add_file_to_db(filepath, user_name=current_username)
    
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

    summary_text = summarize_project(project_id)
    print(summary_text)

    input("\nPress Enter to continue...")

def handle_rank_projects():
    """Handle rank all projects menu option."""
    print("\nRanking all projects...")
    ranked = rank_all_projects()
    display_rankings(ranked)
    
    if ranked:
        print("\n" + "-"*80)
        save_choice = input("Would you like to save these rankings to the database? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes']:
            generate_summaries = input("Generate and save summaries for all projects? (y/n): ").strip().lower()
            save_rankings_with_summaries(ranked, generate_summaries in ['y', 'yes'])
    
    input("\nPress Enter to continue...")


def handle_rank_and_summarize_projects():
    """Handle rank and summarize top 3 projects menu option."""
    rank_and_summarize_top_projects()
    
    # Ask if user wants to save results
    print("\n" + "-"*80)
    save_choice = input("Would you like to save these rankings and summaries to the database? (y/n): ").strip().lower()
    if save_choice in ['y', 'yes']:
        ranked = rank_all_projects()
        if ranked:
            # Generate summaries for all projects (not just top 3)
            generate_all = input("Generate summaries for ALL projects (not just top 3)? (y/n): ").strip().lower()
            save_rankings_with_summaries(ranked, generate_all in ['y', 'yes'])
    
    input("\nPress Enter to continue...")


def handle_view_edit_rankings():
    """Handle view and edit stored rankings menu option."""
    print("\n" + "="*80)
    print("VIEW AND EDIT STORED RANKINGS")
    print("="*80)
    
    stored_rankings = get_stored_rankings()
    
    if not stored_rankings:
        print("\nNo stored rankings found. Please rank projects first and save them.")
        input("\nPress Enter to continue...")
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
        print("4. Change rank position for a project")
        print("5. Back to main menu")
        
        choice = input("\nChoose an option (1-5): ").strip()
        
        if choice == '1':
            # View full details
            project_id = input("Enter project ID to view: ").strip()
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
            project_id = input("Enter project ID to edit score: ").strip()
            if project_id.isdigit():
                new_score = input("Enter new score: ").strip()
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
            project_id = input("Enter project ID to edit summary: ").strip()
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
                        line = input()
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
            # Change rank position
            project_id = input("Enter project ID to change rank: ").strip()
            if project_id.isdigit():
                new_position = input("Enter new rank position: ").strip()
                try:
                    pos_int = int(new_position)
                    if pos_int < 1:
                        print("Rank position must be at least 1.")
                    else:
                        if update_ranking_position(int(project_id), pos_int):
                            print(f"\n Successfully updated rank position for project {project_id} to {pos_int}")
                        else:
                            print(f"\n Failed to update rank position. Project {project_id} may not exist in stored rankings.")
                except ValueError:
                    print("Invalid position. Please enter a number.")
            else:
                print("Invalid project ID.")
        
        elif choice == '5':
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")


def handle_cleanup_insights():
    """Handle cleanup insights menu option."""
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
        input("\nPress Enter to continue...")
        return
    
    current_user = AuthManager.get_current_user()
    user_id = current_user.get('user_name', 'default_user') if current_user else 'default_user'
    
    # Check if resume already exists
    if ResumeManager.resume_exists(user_id):
        print("\nA resume already exists for your account.")
        regenerate = input("Would you like to regenerate it? (y/n): ").strip().lower()
        if regenerate not in ('y', 'yes'):
            print("Cancelled.")
            return
    
    # Ask how many top projects to include
    while True:
        top_count = input("\nHow many top projects to include in resume? (1-10, default 5): ").strip()
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
        input("\nPress Enter to continue...")
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
    
    input("\nPress Enter to continue...")


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
        input("\nPress Enter to continue...")
        return
    
    current_user = AuthManager.get_current_user()
    user_id = current_user.get('user_name', 'default_user') if current_user else 'default_user'
    
    # Check if resume exists
    if not ResumeManager.resume_exists(user_id):
        print("\nNo resume found. Please generate a resume first.")
        input("\nPress Enter to continue...")
        return
    
    # Retrieve resume
    resume_record = ResumeManager.get_user_resume(user_id)
    
    if not resume_record:
        print("\nFailed to retrieve resume from database.")
        input("\nPress Enter to continue...")
        return
    
    resume_data = resume_record['resume_data']
    
    # Ask for format
    print("\nAvailable formats:")
    print("1. Text (default)")
    print("2. Markdown")
    print("3. JSON")
    print("4. Export as PDF")
    
    format_choice = input("\nSelect format (1-4, default 1): ").strip()
    
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
    
    input("\nPress Enter to continue...")


def handle_llm_summary():
    """Run the LLM summary against the bundled test.zip archive."""
    print("\n" + "-"*70)
    print("LLM Summary (test.zip)")
    print("-"*70)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    zip_path = os.path.join(project_root, "test.zip")

    if not os.path.exists(zip_path):
        print(f"Default archive not found at: {zip_path}")
        zip_path = input("Enter path to a zip file (or press Enter to cancel): ").strip()
        if not zip_path:
            print("Cancelled.")
            return

    command = [
        sys.executable,
        "-m",
        "src.tools.ollama_analyze_file",
        zip_path,
        "--zip",
        "--max-files",
        "200",
        "--max-bytes-per-file",
        "4000",
    ]

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout.strip())
    except subprocess.CalledProcessError as exc:
        print("LLM summary failed to run.")
        if exc.stdout:
            print(exc.stdout.strip())
        if exc.stderr:
            print(exc.stderr.strip())
    except OSError as exc:
        print(f"Failed to start LLM summary: {exc}")

    input("\nPress Enter to continue...")


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
    
    filename = input(f"Enter filename (press Enter for default): ").strip()
    
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
        input("\nPress Enter to continue...")
        return
    
    current_user = AuthManager.get_current_user()
    user_id = current_user.get('user_name', 'default_user') if current_user else 'default_user'
    
    # Check if resume exists
    if not ResumeManager.resume_exists(user_id):
        print("\nNo resume found.")
        input("\nPress Enter to continue...")
        return
    
    # Confirm deletion
    confirm = input("\nAre you sure you want to delete your resume? This cannot be undone. (y/n): ").strip().lower()
    
    if confirm in ('y', 'yes'):
        success = ResumeManager.delete_user_resume(user_id)
        
        if success:
            print("\nResume deleted successfully.")
        else:
            print("\nFailed to delete resume.")
    else:
        print("\nCancelled.")
    
    input("\nPress Enter to continue...")
