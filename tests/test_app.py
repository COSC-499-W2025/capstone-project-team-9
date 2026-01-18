"""
Tests for application initialization and setup
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock, Mock

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import initialize_app, ensure_user_preferences_schema


class TestEnsureUserPreferencesSchema:
    """Test user preferences schema migration"""
    
    @patch('config.db_config.with_db_cursor')
    def test_ensure_user_preferences_schema_table_exists(self, mock_with_db_cursor):
        """Test schema update when table exists"""
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_context.__exit__.return_value = None
        mock_with_db_cursor.return_value = mock_context
        
        ensure_user_preferences_schema()
        
        # Should add column if not exists
        assert mock_cursor.execute.called
        mock_with_db_cursor.assert_called_once()
    
    @patch('config.db_config.with_db_cursor')
    def test_ensure_user_preferences_schema_table_not_exists(self, mock_with_db_cursor):
        """Test schema update when table doesn't exist"""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("user_preferences table does not exist")
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_context.__exit__.return_value = None
        mock_with_db_cursor.return_value = mock_context
        
        # Exception should be caught and printed, not raised
        ensure_user_preferences_schema()
    
    @patch('config.db_config.with_db_cursor')
    def test_ensure_user_preferences_schema_error(self, mock_with_db_cursor):
        """Test error handling in schema update"""
        mock_with_db_cursor.side_effect = Exception("Database connection error")
        
        # Exception should be caught and printed, not raised
        ensure_user_preferences_schema()


class TestInitializeApp:
    """Test application initialization"""
    
    @patch('app.ensure_user_preferences_schema')
    @patch('app.CollaborativeManager')
    @patch('app.ConsentManager')
    def test_initialize_app_success(
        self,
        mock_consent_manager_class,
        mock_collab_manager_class,
        mock_ensure_schema
    ):
        """Test successful application initialization"""
        # Setup mocks
        mock_consent_manager = MagicMock()
        mock_consent_manager.request_consent_if_needed.return_value = True
        mock_consent_manager_class.return_value = mock_consent_manager
        
        mock_collab_manager = MagicMock()
        mock_collab_manager.request_collaborative_if_needed.return_value = True
        mock_collab_manager_class.return_value = mock_collab_manager
        
        result = initialize_app()
        
        # Verify initialization steps were called
        mock_consent_manager.initialize.assert_called_once()
        mock_consent_manager.request_consent_if_needed.assert_called_once()
        mock_collab_manager.request_collaborative_if_needed.assert_called_once()
        mock_ensure_schema.assert_called_once()
        
        # Should return tuple of managers
        assert result is not None
        assert len(result) == 2
        assert result[0] == mock_consent_manager
        assert result[1] == mock_collab_manager
    
    @patch('app.ensure_user_preferences_schema')
    @patch('app.CollaborativeManager')
    @patch('app.ConsentManager')
    def test_initialize_app_consent_not_granted(
        self,
        mock_consent_manager_class,
        mock_collab_manager_class,
        mock_ensure_schema
    ):
        """Test initialization when consent is not granted"""
        mock_consent_manager = MagicMock()
        mock_consent_manager.request_consent_if_needed.return_value = False
        mock_consent_manager_class.return_value = mock_consent_manager
        
        mock_collab_manager = MagicMock()
        mock_collab_manager_class.return_value = mock_collab_manager
        
        result = initialize_app()
        
        # Should return None when consent not granted
        assert result is None
        mock_consent_manager.request_consent_if_needed.assert_called_once()
    
    @patch('app.ensure_user_preferences_schema')
    @patch('app.CollaborativeManager')
    @patch('app.ConsentManager')
    def test_initialize_app_collaborative_not_granted(
        self,
        mock_consent_manager_class,
        mock_collab_manager_class,
        mock_ensure_schema
    ):
        """Test initialization when collaborative consent is not granted"""
        mock_consent_manager = MagicMock()
        mock_consent_manager.request_consent_if_needed.return_value = True
        mock_consent_manager_class.return_value = mock_consent_manager
        
        mock_collab_manager = MagicMock()
        mock_collab_manager.request_collaborative_if_needed.return_value = False
        mock_collab_manager_class.return_value = mock_collab_manager
        
        result = initialize_app()
        
        # Should still succeed but collaborative not granted
        assert result is not None
        mock_collab_manager.request_collaborative_if_needed.assert_called_once()
    
    @patch('app.ensure_user_preferences_schema')
    @patch('app.CollaborativeManager')
    @patch('app.ConsentManager')
    def test_initialize_app_database_init_error(
        self,
        mock_consent_manager_class,
        mock_collab_manager_class,
        mock_ensure_schema
    ):
        """Test initialization when database schema update fails"""
        # Make ensure_user_preferences_schema raise an exception
        mock_ensure_schema.side_effect = Exception("Database initialization error")
        
        # Mock managers to avoid stdin issues
        mock_consent_manager = MagicMock()
        mock_consent_manager_class.return_value = mock_consent_manager
        mock_collab_manager = MagicMock()
        mock_collab_manager_class.return_value = mock_collab_manager
        
        # Should not raise exception, as errors are caught in ensure_user_preferences_schema
        result = initialize_app()
        
        # The function should continue and potentially succeed despite schema error
        # (since ensure_user_preferences_schema catches its own exceptions)
        # So this test actually verifies graceful degradation
        assert mock_ensure_schema.called
    
    @patch('app.ensure_user_preferences_schema')
    @patch('app.CollaborativeManager')
    @patch('app.ConsentManager')
    def test_initialize_app_database_connection_fails(
        self,
        mock_consent_manager_class,
        mock_collab_manager_class,
        mock_ensure_schema
    ):
        """Test initialization when database schema check fails"""
        # Setup mocks
        mock_consent_manager = MagicMock()
        mock_consent_manager.request_consent_if_needed.return_value = True
        mock_consent_manager_class.return_value = mock_consent_manager
        
        mock_collab_manager = MagicMock()
        mock_collab_manager.request_collaborative_if_needed.return_value = True
        mock_collab_manager_class.return_value = mock_collab_manager
        
        # Database connection fails in schema check
        mock_ensure_schema.side_effect = ConnectionError("Could not connect to database")
        
        result = initialize_app()
        
        # Should still return managers tuple as ensure_user_preferences_schema
        # catches and prints exceptions without stopping initialization
        assert result is not None
        assert len(result) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

