# tests/test_upload_file.py
import sys
import os
import pytest
import zipfile
import tempfile
import shutil
from unittest.mock import Mock, patch

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.upload_file import add_file_to_db, UPLOAD_FOLDER


class TestUploadFile:
    """Test suite for upload_file.py functionality"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up after each test"""
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_zip(self, filename="test.zip", content="test content"):
        """Helper method to create a test ZIP file"""
        zip_path = os.path.join(self.test_dir, filename)
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("test_file.txt", content)
        return zip_path
    
    def create_invalid_file(self, filename="test.txt", content="not a zip"):
        """Helper method to create an invalid file"""
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path
    
    @patch('src.upload_file.extract_and_store_file_contents')
    @patch('src.upload_file.get_connection')
    # This is a mock database connection
    def test_add_file_to_db_success(self, mock_get_connection, mock_extract_contents):
        """Test successful file upload to database"""
        # Create a valid ZIP file for testing
        zip_path = self.create_test_zip()
        
        # mock the database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Configure the cursor to return a mock ID when fetchone() is called
        mock_cursor.fetchone.return_value = (1,)  # Return tuple with ID 1
        
        # Mock the extract_and_store_file_contents function to return success
        mock_extract_contents.return_value = {
            "success": True,
            "total_files": 1,
            "errors": []
        }

        # Call the function to add the file to the Database
        add_file_to_db(zip_path)
        
        # Verify database operations
        mock_get_connection.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Verify the execute call contains correct parameters
        call_args = mock_cursor.execute.call_args
        assert "INSERT INTO uploaded_files" in call_args[0][0]
        assert call_args[0][1][0] == "test.zip"  # filename
        assert call_args[0][1][2] == "uploaded"  # status
    
    # this is a test for a non-existent file
    def test_add_file_to_db_nonexistent_file(self):

        """Test handling of non-existent file"""
        nonexistent_path = os.path.join(self.test_dir, "nonexistent.zip")
        
        # Should not raise exception, but should return early
        result = add_file_to_db(nonexistent_path)
        assert result is None
    # this is a test for a file with an invalid extension
    def test_add_file_to_db_invalid_extension(self):
        """Test handling of file with invalid extension"""
        invalid_file = self.create_invalid_file("test.txt")
        
        # Should not raise exception, but should return early due to validation
        result = add_file_to_db(invalid_file)
        assert result is None
    
    @patch('src.upload_file.get_connection')
    # This is a mock database connection and it mocks it to return None to see if the function handles it correctly when the database fails to connect
    def test_add_file_to_db_database_connection_failure(self, mock_get_connection):
        """Test handling of database connection failure"""
        zip_path = self.create_test_zip()
        
        # Mock database connection failure
        mock_get_connection.return_value = None
        
        # Should not raise exception, but should return early
        result = add_file_to_db(zip_path)
        assert result is None


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
