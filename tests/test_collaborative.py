"""
Pytest tests for CollaborativeManager functionality
Tests implemented features:
- Table initialization
- Retrieving preferences
- Requesting collaborative consent

Run with: $env:PYTHONPATH="."; pytest tests -vv
"""

import sys
import os
import pytest

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from collaborative.collaborative_manager import CollaborativeManager
from collaborative.collaborative_storage import CollaborativeStorage
from collaborative.collaborative_display import CollaborativeDisplay

from config.db_config import get_connection

@pytest.fixture(scope="function")
def collaborative_manager():
    """
    Fixture to provide a fresh CollaborativeManager instance for each test.
    """
    manager = CollaborativeManager()
    # Ensure clean state
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_preferences;")
    conn.commit()
    conn.close()
    
    yield manager

    # Cleanup after test
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_preferences;")
    conn.commit()
    conn.close()

@pytest.fixture(scope="session")
def db_connection():
    """
    Session-level fixture to verify database connection.
    """
    conn = get_connection()
    assert conn is not None, "Database connection failed"
    conn.close()
    return True

class TestDatabaseSetup:
    """Test database connection and setup."""
    
    def test_database_connection(self, db_connection):
        assert db_connection == True
    
    def test_user_preferences_table_initialization(self, collaborative_manager):
        # If we can create a manager without error, table exists
        assert collaborative_manager is not None

class TestGetPreferences:
    """Test retrieving preferences from the database."""
    
    def test_no_preferences_returns_false_false_none(self, collaborative_manager):
        consent, collaborative, last_updated = collaborative_manager.get_preferences()
        assert consent == False
        assert collaborative == False
        assert last_updated is None
    
    def test_preferences_after_insert(self, collaborative_manager):
        # Insert a row manually
        CollaborativeStorage.update_collaborative(True)
        CollaborativeStorage.update_consent(True)
        
        consent, collaborative, last_updated = collaborative_manager.get_preferences()
        assert consent == True
        assert collaborative == True
        assert last_updated is not None

class TestRequestCollaborative:
    """Test requesting collaborative consent behavior."""
    
    def test_request_collaborative_grants_consent(self, collaborative_manager, monkeypatch):
        # Simulate user always granting collaborative consent
        monkeypatch.setattr(CollaborativeDisplay, "request_collaborative", lambda: True)
