"""
Pytest tests for Requirement #1: User Consent Management
Tests all 3 sub-issues:
- Sub-issue #11: Define consent scope
- Sub-issue #14: Check consent status before access
- Sub-issue #18: Allow withdrawal of consent

Run with: $env:PYTHONPATH="."; pytest tests -v
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

import pytest
from consent.consent_manager import ConsentManager, requires_consent
from consent.consent_storage import ConsentStorage
from consent.consent_display import ConsentDisplay
from config.db_config import get_connection


@pytest.fixture(scope="function")
def consent_manager():
    """
    Fixture to provide a fresh ConsentManager instance for each test.
    Uses a unique test user ID to avoid conflicts between tests.
    """
    test_user_id = 'test_user_pytest'
    manager = ConsentManager(user_id=test_user_id)
    
    # Initialize tables
    manager.initialize()
    
    yield manager
    
    # Cleanup: Remove test consent after each test
    try:
        manager.storage.withdraw_consent(test_user_id)
    except:
        pass


@pytest.fixture(scope="session")
def db_connection():
    """
    Session-level fixture to verify database connection.
    Runs once for the entire test session.
    """
    conn = get_connection()
    assert conn is not None, "Database connection failed"
    conn.close()
    return True


class TestDatabaseSetup:
    """Test database connection and setup."""
    
    def test_database_connection(self, db_connection):
        """Test that database connection works."""
        assert db_connection == True
    
    def test_consent_table_initialization(self, consent_manager):
        """Test that consent table is created successfully."""
        # If we get here, initialization worked
        assert consent_manager is not None


class TestSubIssue11_ConsentScope:
    """
    Tests for Sub-issue #11: Define the consent scope
    Verifies that consent information is properly structured and accessible.
    """
    
    def test_consent_display_has_all_required_info(self):
        """Test that consent message includes all required information."""
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            ConsentDisplay.show_consent_message()
        output = f.getvalue()
        
        # Verify all required sections are present
        assert "WHAT DATA WILL BE ACCESSED" in output
        assert "HOW YOUR DATA WILL BE USED" in output
        assert "DATA STORAGE & RETENTION" in output
        assert "YOUR RIGHTS" in output
        
        # Verify specific data types mentioned
        assert "File metadata" in output
        assert "Programming code" in output
        assert "Git commit history" in output
        
        # Verify purposes mentioned
        assert "Analyze project structure" in output
        assert "Extract contribution metrics" in output
        
        # Verify duration mentioned
        assert "Duration:" in output
        assert "Local PostgreSQL database" in output
        
        # Verify user rights mentioned
        assert "withdraw consent" in output
    
    def test_consent_scope_includes_external_services_notice(self):
        """Test that consent mentions external services will be asked separately."""
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            ConsentDisplay.show_consent_message()
        output = f.getvalue()
        
        assert "External Services" in output
        assert "LLM" in output or "external service" in output.lower()


class TestSubIssue14_CheckConsent:
    """
    Tests for Sub-issue #14: Check consent status before granting access
    Verifies that data access is properly controlled by consent status.
    """
    
    def test_no_consent_blocks_access(self, consent_manager):
        """Test that access is blocked when no consent exists."""
        # Don't store any consent
        has_access = consent_manager.has_access()
        assert has_access == False
    
    def test_granted_consent_allows_access(self, consent_manager):
        """Test that access is granted when consent is given."""
        # Store consent
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        
        # Check access
        has_access = consent_manager.has_access()
        assert has_access == True
    
    def test_denied_consent_blocks_access(self, consent_manager):
        """Test that explicitly denied consent blocks access."""
        # Store denied consent
        consent_manager.storage.store_consent(False, consent_manager.user_id)
        
        # Check access
        has_access = consent_manager.has_access()
        assert has_access == False
    
    def test_consent_status_retrieval(self, consent_manager):
        """Test retrieving consent status from database."""
        # Store consent
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        
        # Retrieve status
        status = consent_manager.storage.get_consent_status(consent_manager.user_id)
        
        assert status is not None
        assert status['consent_given'] == True
        assert status['consent_date'] is not None
        assert status['withdrawn_date'] is None
    
    def test_requires_consent_decorator_allows_with_consent(self, consent_manager):
        """Test that consent checking allows execution with valid consent."""
        # Grant consent
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        
        # Use instance method decorator
        @consent_manager.require_consent
        def protected_function():
            return "success"
        
        # Should execute successfully
        result = protected_function()
        assert result == "success"
    
    def test_requires_consent_decorator_blocks_without_consent(self, consent_manager):
        """Test that consent checking blocks execution without consent."""
        # Don't grant consent
        
        # Use instance method decorator
        @consent_manager.require_consent
        def protected_function():
            return "success"
        
        # Should raise PermissionError
        with pytest.raises(PermissionError):
            protected_function()


class TestSubIssue18_WithdrawConsent:
    """
    Tests for Sub-issue #18: Allow user to withdraw consent
    Verifies that consent can be withdrawn and access is immediately blocked.
    """
    
    def test_withdraw_consent_success(self, consent_manager):
        """Test that consent can be successfully withdrawn."""
        # First grant consent
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        assert consent_manager.has_access() == True
        
        # Withdraw consent
        result = consent_manager.storage.withdraw_consent(consent_manager.user_id)
        
        assert result == True
    
    def test_access_blocked_after_withdrawal(self, consent_manager):
        """Test that access is blocked immediately after withdrawal."""
        # Grant consent
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        assert consent_manager.has_access() == True
        
        # Withdraw consent
        consent_manager.storage.withdraw_consent(consent_manager.user_id)
        
        # Verify access is now blocked
        has_access = consent_manager.has_access()
        assert has_access == False
    
    def test_withdrawn_date_recorded(self, consent_manager):
        """Test that withdrawal date is properly recorded."""
        # Grant then withdraw
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        consent_manager.storage.withdraw_consent(consent_manager.user_id)
        
        # Check status
        status = consent_manager.storage.get_consent_status(consent_manager.user_id)
        
        assert status is not None
        assert status['consent_given'] == False
        assert status['withdrawn_date'] is not None
    
    def test_decorator_blocks_after_withdrawal(self, consent_manager):
        """Test that consent checking blocks execution after withdrawal."""
        # Grant consent first
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        
        # Use instance method decorator
        @consent_manager.require_consent
        def protected_function():
            return "success"
        
        # Should work with consent
        assert protected_function() == "success"
        
        # Withdraw consent
        consent_manager.storage.withdraw_consent(consent_manager.user_id)
        
        # Should now raise PermissionError
        with pytest.raises(PermissionError):
            protected_function()
    
    def test_re_consent_after_withdrawal(self, consent_manager):
        """Test that user can grant consent again after withdrawal."""
        # Grant, withdraw, then grant again
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        consent_manager.storage.withdraw_consent(consent_manager.user_id)
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        
        # Should have access again
        assert consent_manager.has_access() == True
        
        # Withdrawn date should be cleared
        status = consent_manager.storage.get_consent_status(consent_manager.user_id)
        assert status['withdrawn_date'] is None


class TestConsentWorkflow:
    """Integration tests for the complete consent workflow."""
    
    def test_complete_consent_workflow(self, consent_manager):
        """Test the complete consent workflow from start to finish."""
        # 1. Initially no consent
        assert consent_manager.has_access() == False
        
        # 2. Grant consent
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        assert consent_manager.has_access() == True
        
        # 3. Withdraw consent
        consent_manager.storage.withdraw_consent(consent_manager.user_id)
        assert consent_manager.has_access() == False
        
        # 4. Re-grant consent
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        assert consent_manager.has_access() == True
    
    def test_consent_persistence(self, consent_manager):
        """Test that consent persists in database."""
        # Store consent
        consent_manager.storage.store_consent(True, consent_manager.user_id)
        
        # Create new manager instance (simulates app restart)
        new_manager = ConsentManager(user_id=consent_manager.user_id)
        
        # Should still have access
        assert new_manager.has_access() == True