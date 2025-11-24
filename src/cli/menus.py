"""Menu handlers for CLI interactions."""
import os
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


def summarize_project_menu():
    """Handle the project summarization menu."""
    print("\n" + "-"*50)
    print("Project Summarization")
    print("-"*50)
    
    selected_project = select_project_interactive("Project Summarization")
    if not selected_project:
        return
    print(f"\nGenerating summary for: {selected_project['filename']}")
    print("Please wait...")
    summary = summarize_project(selected_project['id'])
    print(summary)
    input("\nPress Enter to continue...")


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
    add_file_to_db(filepath)


def handle_list_projects():
    """Handle list projects menu option."""
    list_projects_menu()


def handle_analyze_metrics():
    """Handle analyze project metrics menu option."""
    selected_project = select_project_interactive("Analyze project metrics")
    if selected_project:
        analyze_project_from_db(int(selected_project['id']))


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

