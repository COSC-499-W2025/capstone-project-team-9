"""Core application initialization and setup."""
from consent.consent_manager import ConsentManager
from collaborative.collaborative_manager import CollaborativeManager
from upload_file import init_uploaded_files_table
from database.user_informations import init_user_informations_table
from analysis.ranking_storage import init_ranking_storage_table
from resume.resume_manager import ResumeManager


def ensure_user_preferences_schema():
    """Ensure user_preferences table has git_username column."""
    try:
        from config.db_config import with_db_cursor
        with with_db_cursor() as cur:
            # Add git_username column if missing
            cur.execute("""
                ALTER TABLE user_preferences
                ADD COLUMN IF NOT EXISTS git_username VARCHAR(255);
            """)
    except Exception as e:
        print(f"[WARN] Exception caught: {e}")


def initialize_app():
    """
    Initialize the application managers and request user consent.
    Should be called AFTER user login.
    Returns tuple of (consent_manager, collab_manager) or None if initialization fails.
    """
    # Ensure user_preferences table schema is up to date
    try:
        ensure_user_preferences_schema()
    except Exception as e:
        print(f"[WARN] Schema update failed: {e}")
    
    # Initialize managers (they will use current logged-in user)
    consent_manager = ConsentManager()
    collab_manager = CollaborativeManager()
    
    consent_manager.initialize()
    
    # Check/request user consent
    if not consent_manager.request_consent_if_needed():
        print("Consent not granted. Exiting...")
        return None
    else:
        print("User consent granted. Proceeding with backend setup.")
    
    # Check/request collaborative consent
    if not collab_manager.request_collaborative_if_needed():
        print("Collaborative not granted. Doing individual.")
    else:
        print("Collaborative granted. Doing collaborative and individual.")
    
    return consent_manager, collab_manager