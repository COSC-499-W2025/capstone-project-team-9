"""
Main consent management module that orchestrates consent operations.
This module ties together display, storage, and validation logic.
"""

from consent.consent_display import ConsentDisplay
from consent.consent_storage import ConsentStorage


class ConsentManager:
    """
    Main class for managing user consent throughout the application.
    Implements all three sub-issues for Requirement #1.
    """
    
    def __init__(self, user_id='default_user'):
        """
        Initialize the consent manager.
        
        Args:
            user_id (str): User identifier (default for single-user mode)
        """
        self.user_id = user_id
        self.storage = ConsentStorage()
    
    def initialize(self):
        """Initialize consent system (create tables)."""
        try:
            self.storage.initialize_consent_table()
            return True
        except Exception as e:
            print(f"✗ Failed to initialize consent system: {e}")
            return False
    
    def request_consent_if_needed(self):
        """
        Main workflow: Request consent only if not already granted.
        Combines all 3 sub-issues:
        - #11: Display consent scope
        - #14: Check consent status
        - Returns access decision
        """
        # Sub-issue #14: Check if consent already exists
        if self.storage.has_valid_consent(self.user_id):
            print("✓ Valid consent exists. Access granted.\n")
            return True
        
        # Sub-issue #11: Display consent information
        ConsentDisplay.show_consent_message()
        consent_granted = ConsentDisplay.prompt_for_consent()
        
        # Store the consent decision
        if self.storage.store_consent(consent_granted, self.user_id):
            return consent_granted
        else:
            print("✗ Error storing consent.")
            return False
    
    def has_access(self):
        """
        Sub-issue #14: Check if user has access.
        Returns True only if valid consent exists.
        """
        return self.storage.has_valid_consent(self.user_id)
    
    def withdraw(self):
        """
        Sub-issue #18: Allow user to withdraw consent.
        """
        consent_data = self.storage.get_consent_status(self.user_id)
        
        if not consent_data or not consent_data['consent_given']:
            print("\n✗ No active consent to withdraw.\n")
            return False
        
        print("\n" + "="*70)
        print("WITHDRAW CONSENT")
        print("="*70)
        print("Are you sure? This will block data access.")
        
        response = input("\nConfirm withdrawal (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            if self.storage.withdraw_consent(self.user_id):
                print("\n✓ Consent withdrawn successfully.")
                print("✗ Application no longer has data access.\n")
                return True
        
        print("\n✓ Withdrawal cancelled.\n")
        return False
    
    def require_consent(self, func):
        """
        Instance method decorator that checks THIS manager's consent.
        Sub-issue #14: Block access to data until consent is given.
        
        Usage:
            manager = ConsentManager(user_id='test_user')
            
            @manager.require_consent
            def protected_function():
                return "success"
        """
        def wrapper(*args, **kwargs):
            if not self.has_access():
                raise PermissionError("Data access denied: Valid consent required")
            return func(*args, **kwargs)
        return wrapper


def requires_consent(func):
    """
    Decorator to protect functions that need consent.
    Uses the default user_id.
    Sub-issue #14: Block access without consent.
    
    Usage:
        @requires_consent
        def process_data():
            # This will only run if default user has consent
            pass
    """
    def wrapper(*args, **kwargs):
        manager = ConsentManager()
        if not manager.has_access():
            print("\n✗ ACCESS DENIED: Valid consent required.\n")
            raise PermissionError("Data access denied")
        return func(*args, **kwargs)
    return wrapper