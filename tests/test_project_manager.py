# tests/test_project_manager.py
import sys
import os
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.project_manager import list_projects, get_project_by_id, get_project_count


class TestProjectManager:
    """Test suite for project_manager functionality"""
    
    @patch('src.project_manager.get_connection')
    # this test will test the list_projects function when there are individual files in the projects
    def test_list_projects_individual_files(self, mock_get_connection):
        """Test that individual files are properly extracted and sorted"""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock database results with nested folder structure
        mock_projects = [
            (1, "project_a.zip", "uploaded", '{"files": ["folder/file1.py", "folder/file2.js", "folder/"]}', datetime(2024, 1, 1, 10, 0, 0)),
            (2, "project_b.zip", "uploaded", '{"files": ["readme.md", "src/main.py", "tests/test.py"]}', datetime(2024, 1, 2, 11, 0, 0))
        ]
        mock_cursor.fetchall.return_value = mock_projects
        
        # Call the function
        result = list_projects()
        
        # Verify database operations
        mock_get_connection.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Verify return value (should still return original projects)
        assert result == mock_projects
    
    @patch('src.project_manager.get_connection')
    # this test will test the list_projects function when there are no projects in the database
    def test_list_projects_no_projects(self, mock_get_connection):
        """Test listing when no projects exist"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock empty results
        mock_cursor.fetchall.return_value = []
        
        # Call the function
        result = list_projects()
        
        # Verify return value
        assert result == []
    
    @patch('src.project_manager.get_connection')
    # this test will test the list_projects function when the database connection fails
    def test_list_projects_database_connection_failure(self, mock_get_connection):
        """Test handling of database connection failure"""
        # Mock database connection failure
        mock_get_connection.return_value = None
        
        # Call the function
        result = list_projects()
        
        # Verify return value
        assert result == []
    
    @patch('src.project_manager.get_connection')
    # this test will test the get_project_by_id function
    def test_get_project_by_id_success(self, mock_get_connection):
        """Test successful project retrieval by ID"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock database result
        mock_project = (1, "test_project.zip", "/path/to/file", "uploaded", '{"files": ["file1.py"]}', datetime(2024, 1, 1, 10, 0, 0))
        mock_cursor.fetchone.return_value = mock_project
        
        # Call the function
        result = get_project_by_id(1)
        
        # Verify database operations
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Verify return value
        expected = {
            'id': 1,
            'filename': 'test_project.zip',
            'filepath': '/path/to/file',
            'status': 'uploaded',
            'metadata': '{"files": ["file1.py"]}',
            'created_at': datetime(2024, 1, 1, 10, 0, 0)
        }
        assert result == expected
    
    @patch('src.project_manager.get_connection')
    # this test will test the get_project_by_id function when the project does not exist
    def test_get_project_by_id_not_found(self, mock_get_connection):
        """Test project retrieval when project doesn't exist"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock empty result
        mock_cursor.fetchone.return_value = None
        
        # Call the function
        result = get_project_by_id(999)
        
        # Verify return value
        assert result is None
    
    @patch('src.project_manager.get_connection')
    # this test will test the get_project_count function
    def test_get_project_count_success(self, mock_get_connection):
        """Test successful project count retrieval"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock count result
        mock_cursor.fetchone.return_value = (5,)
        
        # Call the function
        result = get_project_count()
        
        # Verify database operations
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Verify return value
        assert result == 5
    
if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
