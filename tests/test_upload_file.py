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
from src.upload_file import add_file_to_db, UPLOAD_FOLDER, UploadResult


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
    
    @patch('src.upload_file.get_connection')
    def test_add_file_to_db_success(self, mock_get_connection):
        """Test successful file upload to database"""
        # Create a valid ZIP file for testing
        zip_path = self.create_test_zip()
        
        # Mock the database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [123]  # Mock file_id

        # Call the function to add the file to the Database
        result = add_file_to_db(zip_path)
        
        # Verify result is UploadResult with success=True
        assert isinstance(result, UploadResult)
        assert result.success is True
        assert result.error_type is None
        assert "uploaded successfully" in result.message
        assert "file_id" in result.data
        assert result.data["filename"] == "test.zip"
        assert result.data["file_count"] >= 1
        
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
        
        # Should return UploadResult with error
        result = add_file_to_db(nonexistent_path)
        assert isinstance(result, UploadResult)
        assert result.success is False
        assert result.error_type == "FILE_NOT_FOUND"
        assert "does not exist" in result.message
    
    def test_add_file_to_db_invalid_extension(self):
        """Test handling of file with invalid extension"""
        invalid_file = self.create_invalid_file("test.txt")
        
        # Should return UploadResult with format error
        result = add_file_to_db(invalid_file)
        assert isinstance(result, UploadResult)
        assert result.success is False
        assert result.error_type == "INVALID_FORMAT"
        assert "Invalid file format" in result.message
    
    @patch('src.upload_file.get_connection')
    # This is a mock database connection and it mocks it to return None to see if the function handles it correctly when the database fails to connect
    def test_add_file_to_db_database_connection_failure(self, mock_get_connection):
        """Test handling of database connection failure"""
        zip_path = self.create_test_zip()
        
        # Mock database connection failure
        mock_get_connection.return_value = None
        
        # Should return UploadResult with database error
        result = add_file_to_db(zip_path)
        assert isinstance(result, UploadResult)
        assert result.success is False
        assert result.error_type == "DATABASE_CONNECTION_ERROR"
        assert "Could not connect to database" in result.message
    
    def test_add_file_to_db_invalid_zip_file(self):
        """Test handling of corrupted/invalid ZIP file"""
        # Create a file with .zip extension but invalid content
        fake_zip_path = os.path.join(self.test_dir, "fake.zip")
        with open(fake_zip_path, 'w') as f:
            f.write("This is not a valid ZIP file")
        
        result = add_file_to_db(fake_zip_path)
        assert isinstance(result, UploadResult)
        assert result.success is False
        assert result.error_type == "INVALID_FORMAT"
        assert "Invalid file format" in result.message
    
    @patch('src.upload_file.get_connection')
    def test_add_file_to_db_database_save_failure(self, mock_get_connection):
        """Test handling of database save failure"""
        zip_path = self.create_test_zip()
        
        # Mock database connection that fails on execute
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")
        
        result = add_file_to_db(zip_path)
        assert isinstance(result, UploadResult)
        assert result.success is False
        assert result.error_type == "DATABASE_SAVE_ERROR"
        assert "Database save failed" in result.message
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('src.upload_file.shutil.copy')
    def test_add_file_to_db_copy_failure(self, mock_copy):
        """Test handling of file copy failure"""
        zip_path = self.create_test_zip()
        
        # Mock file copy failure
        mock_copy.side_effect = Exception("Permission denied")
        
        result = add_file_to_db(zip_path)
        assert isinstance(result, UploadResult)
        assert result.success is False
        assert result.error_type == "COPY_ERROR"
        assert "File copy failed" in result.message
        assert "source" in result.data
        assert "destination" in result.data
    
    @patch('src.upload_file.os.makedirs')
    def test_add_file_to_db_directory_creation_failure(self, mock_makedirs):
        """Test handling of directory creation failure"""
        zip_path = self.create_test_zip()
        
        # Mock directory creation failure
        mock_makedirs.side_effect = Exception("Permission denied")
        
        result = add_file_to_db(zip_path)
        assert isinstance(result, UploadResult)
        assert result.success is False
        assert result.error_type == "DIRECTORY_ERROR"
        assert "Failed to create upload directory" in result.message
    
    @patch('src.upload_file.get_connection')
    def test_upload_result_to_dict(self, mock_get_connection):
        """Test UploadResult.to_dict() method from actual upload operation"""
        zip_path = self.create_test_zip()
        
        # Mock successful database operation
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [456]
        
        # Execute actual upload
        result = add_file_to_db(zip_path)
        
        # Convert to dict and verify structure
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["success"] is True
        assert "message" in result_dict
        assert "error_type" in result_dict
        assert "data" in result_dict
        assert result_dict["error_type"] is None
        assert result_dict["data"]["file_id"] == 456
        assert result_dict["data"]["filename"] == "test.zip"
    
    def test_upload_result_with_error(self):
        """Test UploadResult error handling from actual failed operation"""
        # Test with multiple error scenarios
        nonexistent_path = os.path.join(self.test_dir, "nonexistent.zip")
        result = add_file_to_db(nonexistent_path)
        
        # Verify error result structure
        assert isinstance(result, UploadResult)
        assert result.success is False
        assert result.error_type == "FILE_NOT_FOUND"
        assert len(result.message) > 0
        
        # Test to_dict() on error result
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["error_type"] == "FILE_NOT_FOUND"
        assert "does not exist" in result_dict["message"]


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
