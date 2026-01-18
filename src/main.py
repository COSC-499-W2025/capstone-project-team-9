"""Main entry point for the application."""
from app import initialize_app
from cli.main_menu import run_main_menu
from cli.user_menus import login_menu
from account.user_manager import AuthManager


def main():
    """Main entry point - initializes app and runs CLI."""
    print("STARTING BACKEND SETUP...")
    
    # Initialize database tables first (without consent/collaborative prompts)
    try:
        from upload_file import init_uploaded_files_table
        from database.user_informations import init_user_informations_table
        from analysis.ranking_storage import init_ranking_storage_table
        from resume.resume_manager import ResumeManager
        
        # IMPORTANT: init_user_informations_table() must be called BEFORE init_uploaded_files_table()
        # because uploaded_files has a foreign key reference to user_informations.user_name
        init_user_informations_table()
        init_uploaded_files_table()
        init_ranking_storage_table()
        ResumeManager.init_resume_table()
    except Exception as e:
        print(f"Failed to initialize database tables: {e}")
        return
    
    # Test database connection
    try:
        from config.db_config import with_db_cursor
        with with_db_cursor() as _:
            print("Database is connected!")
    except Exception as e:
        print(f"Database is not connected: {e}")
        return
    
    # Check if user is already logged in from a previous session
    if not AuthManager.is_user_logged_in():
        # Show login menu if no user is logged in
        if not login_menu():
            # User chose to exit from login menu
            return
    
    # User is now logged in, initialize app with consent/collaborative prompts
    managers = initialize_app()
    if managers is None:
        return
    
    consent_manager, collab_manager = managers
    
    # User is now logged in and consents granted, show main menu
    run_main_menu(consent_manager, collab_manager)

if __name__ == "__main__":
    main()