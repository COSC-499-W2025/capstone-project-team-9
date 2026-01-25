"""Main CLI menu loop and routing."""
import os
import sys
from .menus import (
    handle_upload_file,
    handle_list_projects,
    handle_analyze_metrics_and_summary,
    analyze_project_menu,
    handle_rank_projects,
    handle_rank_and_summarize_projects,
    handle_view_edit_rankings,
    manage_external_services_menu,
    handle_cleanup_insights,
    ask_user_preferences,
    portfolio_menu,
    handle_generate_resume,
    handle_view_resume,
    handle_delete_resume,
    handle_add_project_thumbnail,
    handle_llm_summary,
    handle_delete_project
)
from cli.user_menus import user_account_menu
from account.user_manager import AuthManager

MENU_ITEMS = [
    "Upload a ZIP file",                                  # 1
    "List stored projects",                               # 2
    "Analyze a project (FULL MODE: metrics + summary)",   # 3
    "Analyze a project (PRIVACY MODE: analysis with local fallback)",  # 4
    "Rank all projects",                                  # 5
    "Rank and summarize top 3 projects",                  # 6
    "View and edit stored rankings",                      # 7
    "Manage external service settings",                   # 8
    "Cleanup insights for a project",                     # 9
    "Change User Preferences",                            # 10
    "User Account",                                       # 11
    "Generate Resume",                                    # 12
    "View Resume",                                        # 13
    "Delete Resume",                                      # 14
    "View Portfolio",                                     # 15
    "Add thumbnail to a project",                         # 16
    "Run LLM summary (test.zip)",                         # 17
    "Delete a project",                                   # 18
    "Exit"                                                # 19
]

def run_main_menu(consent_manager, collab_manager):
    """Run the main menu loop."""
    while True:
        # Check if user is still logged in (in case of session timeout or logout)
        if not AuthManager.is_user_logged_in():
            print("\nSession expired or user logged out. Please log in again.")
            from cli.user_menus import login_menu
            if not login_menu():
                # User chose to exit
                return
        
        print("\n" + "="*70)
        print("MINING DIGITAL WORK ARTIFACTS - Main Menu")
        print("="*70)
        
        # Show user info
        current_user = AuthManager.get_current_username()
        print(f"Logged in as: {current_user}")
        print("="*70)
        
        for idx, label in enumerate(MENU_ITEMS, start=1):
            if idx == 11:
                # Dynamically show login status in User Account menu
                if AuthManager.is_user_logged_in():
                    current_user = AuthManager.get_current_username()
                    print(f"{idx}. User Account ({current_user})")
                else:
                    print(f"{idx}. User Account (Login/Register)")
            else:
                print(f"{idx}. {label}")

        print("="*70) 
        
        if os.getenv("GITHUB_ACTIONS") == "true" or not sys.stdin.isatty():
            choice = "17"
        else:
            try:
                choice = input("Choose an option (1-19): ").strip()
            except EOFError:
                choice = "17"
        
        # Check authentication before processing any choice
        if not AuthManager.is_user_logged_in():
            print("Error: User session invalid. Please log in again.")
            continue
            
        handlers = {
            "1": lambda: handle_upload_file(),
            "2": lambda: handle_list_projects(),
            "3": lambda: handle_analyze_metrics_and_summary(),
            "4": lambda: analyze_project_menu(),
            "5": lambda: handle_rank_projects(),
            "6": lambda: handle_rank_and_summarize_projects(),
            "7": lambda: handle_view_edit_rankings(),
            "8": lambda: manage_external_services_menu(),
            "9": lambda: handle_cleanup_insights(),
            "10": lambda: ask_user_preferences(consent_manager, collab_manager, False),
            "11": lambda: user_account_menu(),
            "12": lambda: handle_generate_resume(),
            "13": lambda: handle_view_resume(),
            "14": lambda: handle_delete_resume(),
            "15": lambda: portfolio_menu(),
            "16": lambda: handle_add_project_thumbnail(),
            "17": lambda: handle_llm_summary(),
            "18": lambda: handle_delete_project(),
            "19": "EXIT"
        }

        handler = handlers.get(choice)

        if handler is None:
            print("Invalid choice. Please enter 1-19.")
            continue

        if handler == "EXIT":
            if AuthManager.is_user_logged_in():
                current_user = AuthManager.get_current_username()
                AuthManager.logout()
                print(f"Logging out {current_user}...")
            print("Goodbye!")
            break

        handler()
