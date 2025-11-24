
"""Main CLI menu loop and routing."""
import os
import sys
from .menus import (
    handle_upload_file,
    handle_list_projects,
    handle_analyze_metrics,
    summarize_project_menu,
    analyze_project_menu,
    handle_rank_projects,
    handle_rank_and_summarize_projects,
    handle_view_edit_rankings,
    manage_external_services_menu,
    handle_cleanup_insights,
    ask_user_preferences
)


def run_main_menu(consent_manager, collab_manager):
    """Run the main menu loop."""
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
        print("7. Rank and summarize top 3 projects")
        print("8. View and edit stored rankings")
        print("9. Manage external service settings")
        print("10. Cleanup insights for a project")
        print("11. Change User Preferences")
        print("12. Exit")
        print("="*70) 
        
        if os.getenv("GITHUB_ACTIONS") == "true" or not sys.stdin.isatty():
            choice = "12"
        else:
            try:
                choice = input("Choose an option (1-12): ").strip()
            except EOFError:
                choice = "12"
        
        if choice == '1':
            handle_upload_file()
            
        elif choice == '2':
            handle_list_projects()
            
        elif choice == '3':
            handle_analyze_metrics()
                
        elif choice == '4':
            summarize_project_menu()
            
        elif choice == '5':
            analyze_project_menu()
            
        elif choice == '6':
            handle_rank_projects()
            
        elif choice == '7':
            handle_rank_and_summarize_projects()
            
        elif choice == '8':
            handle_view_edit_rankings()
            
        elif choice == '9':
            manage_external_services_menu()
            
        elif choice == '10':
            handle_cleanup_insights()
                
        elif choice == '11':
            ask_user_preferences(consent_manager, collab_manager, False)

        elif choice == '12':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1-12.")

