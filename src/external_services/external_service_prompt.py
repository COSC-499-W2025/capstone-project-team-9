# src/external_services/external_service_prompt.py
"""
Module for requesting and managing external service permissions from users.
Implements the user-facing prompt for Issue #10.
"""

from external_services.permission_manager import ExternalServicePermission
from external_services.service_config import ServiceConfig


class ExternalServicePrompt:
    """
    Handles user interaction for external service permissions.
    """
    
    @staticmethod
    def show_external_service_info():
        """
        Display information about external services and their implications.
        Requirement #4: Explain implications on data privacy.
        """
        info_text = """
╔════════════════════════════════════════════════════════════════════════╗
║              EXTERNAL SERVICE PERMISSION REQUEST                       ║
╚════════════════════════════════════════════════════════════════════════╝

This application can use external services (such as AI/LLM APIs) to provide
enhanced analysis of your projects. However, this requires sending your 
project data to external providers.

┌─ WHAT EXTERNAL SERVICES PROVIDE ─────────────────────────────────────┐
│                                                                         │
│  • More accurate project descriptions and summaries                    │
│  • Enhanced skill extraction and categorization                        │
│  • Better identification of project types and purposes                 │
│  • More sophisticated contribution analysis                            │
│  • Improved understanding of code quality and patterns                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─ DATA PRIVACY IMPLICATIONS ──────────────────────────────────────────┐
│                                                                         │
│  WARNING: YOUR DATA WILL BE SENT TO EXTERNAL PROVIDERS:                │
│     - File contents may be analyzed by third-party services            │
│     - Code and documentation will leave your local machine             │
│     - External providers may have their own data retention policies    │
│                                                                         │
│  CONSIDER BEFORE GRANTING PERMISSION:                                  │
│     - Do your projects contain proprietary/confidential information?   │
│     - Are you comfortable with external analysis of your code?         │
│     - Have you reviewed the external service provider's privacy policy?│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─ LOCAL ANALYSIS ALTERNATIVE ─────────────────────────────────────────┐
│                                                                         │
│  If you decline, the system will use LOCAL ANALYSIS ONLY:              │
│     ✓ All analysis happens on your machine                             │
│     ✓ No data sent to external services                                │
│     ✓ Complete privacy and data security                               │
│     ✓ Language and framework detection                                 │
│     ✓ Project structure analysis                                       │
│     ✓ Basic skill extraction                                           │
│     ✓ Contribution metrics                                             │
│                                                                         │
│  Local analysis provides comprehensive feedback without compromising   │
│  your privacy. The analysis may be less sophisticated but covers all   │
│  essential metrics you need for your portfolio.                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

NOTE: You can change this preference at any time in the settings.

"""
        print(info_text)
    
    @staticmethod
    def prompt_for_permission(service_name='LLM'):
        """
        Prompt the user to grant or deny permission for external services.
        
        Args:
            service_name (str): Name of the external service
            
        Returns:
            bool: True if permission granted, False otherwise
        """
        while True:
            response = input(f"\nDo you want to allow external {service_name} analysis? (yes/no): ").strip().lower()
            
            if response in ['yes', 'y']:
                print(f"\nExternal {service_name} service permission GRANTED.")
                print("Enhanced analysis will be available for your projects.")
                return True
            elif response in ['no', 'n']:
                print(f"\nExternal {service_name} service permission DECLINED.")
                print("Local analysis will be used instead (your data stays private).")
                return False
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
    
    @staticmethod
    def store_permission(user_id, service_name, permission_granted):
        """
        Store the user's permission choice in the database.
        
        Args:
            user_id (str): User identifier
            service_name (str): Name of the service
            permission_granted (bool): Whether permission was granted
            
        Returns:
            bool: True if stored successfully
        """
        from config.db_config import get_connection
        
        conn = get_connection()
        if not conn:
            print("Error: Could not connect to database")
            return False
        
        try:
            cursor = conn.cursor()
            
            # Insert or update permission
            cursor.execute("""
                INSERT INTO external_service_permissions 
                (user_id, service_name, permission_granted, updated_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id, service_name) 
                DO UPDATE SET 
                    permission_granted = EXCLUDED.permission_granted,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, service_name, permission_granted))
            
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error storing permission: {e}")
            return False
        finally:
            conn.close()


def request_external_service_permission(user_id='default_user', service_name='LLM', force=False):
    """
    Complete workflow for requesting external service permission.
    This is the main entry point for Issue #10.
    
    Args:
        user_id (str): User identifier
        service_name (str): Name of the external service
        force (bool): If True, always ask. If False, skip if already set.
        
    Returns:
        bool: True if permission granted, False if declined
    """
    # Initialize the external service permissions table
    try:
        config = ServiceConfig()
        config.initialize_table()
    except Exception as e:
        print(f"Warning: Could not initialize external service table: {e}")
    
    # Check if permission already exists
    permission_manager = ExternalServicePermission(user_id)
    existing_permission = permission_manager.has_permission(service_name)
    
    # If permission already exists and not forced, return it
    if existing_permission is not None and not force:
        if existing_permission:
            print(f"\nUsing enhanced analysis (external {service_name} services enabled)")
        else:
            print(f"\nUsing local analysis only (your data stays private)")
        return existing_permission
    
    # Show information about external services
    ExternalServicePrompt.show_external_service_info()
    
    # Prompt for permission
    permission_granted = ExternalServicePrompt.prompt_for_permission(service_name)
    
    # Store the permission
    ExternalServicePrompt.store_permission(user_id, service_name, permission_granted)
    
    return permission_granted