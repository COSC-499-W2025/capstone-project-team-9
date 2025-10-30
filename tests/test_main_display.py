# tests/test_main_display.py
import sys
import os
import pytest
from io import StringIO
from unittest.mock import patch

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.main import display_error, display_success
from src.upload_file import UploadResult


class TestDisplayFunctions:
    """Test suite for main.py display functions"""
    
    def test_display_error_file_not_found(self):
        """Test display_error with FILE_NOT_FOUND error"""
        result = UploadResult(
            success=False,
            message="File does not exist: /path/to/file.zip",
            error_type="FILE_NOT_FOUND"
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)
            output = fake_out.getvalue()
        
        # Verify error banner
        assert "=" * 60 in output
        assert "ERROR" in output
        
        # Verify error details
        assert "Error Type: FILE_NOT_FOUND" in output
        assert "File does not exist" in output
        assert "/path/to/file.zip" in output
    
    def test_display_error_invalid_format(self):
        """Test display_error with INVALID_FORMAT error"""
        result = UploadResult(
            success=False,
            message="Invalid file format: File must be a .zip file",
            error_type="INVALID_FORMAT",
            data={"filepath": "test.txt"}
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)
            output = fake_out.getvalue()
        
        assert "ERROR" in output
        assert "INVALID_FORMAT" in output
        assert "Invalid file format" in output
        assert "Details:" in output
        assert "filepath" in output
        assert "test.txt" in output
    
    def test_display_error_database_connection(self):
        """Test display_error with DATABASE_CONNECTION_ERROR"""
        result = UploadResult(
            success=False,
            message="Could not connect to database",
            error_type="DATABASE_CONNECTION_ERROR"
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)
            output = fake_out.getvalue()
        
        assert "DATABASE_CONNECTION_ERROR" in output
        assert "Could not connect to database" in output
        # Should not show Details section when no data
        lines = output.strip().split('\n')
        assert not any("Details:" in line for line in lines if "Details:" in output and result.data)
    
    def test_display_error_with_multiple_data_fields(self):
        """Test display_error with multiple data fields"""
        result = UploadResult(
            success=False,
            message="File copy failed: Permission denied",
            error_type="COPY_ERROR",
            data={
                "source": "/source/path/file.zip",
                "destination": "/dest/path/file.zip",
                "error_code": 13
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)
            output = fake_out.getvalue()
        
        assert "COPY_ERROR" in output
        assert "File copy failed" in output
        assert "Details:" in output
        assert "source" in output
        assert "/source/path/file.zip" in output
        assert "destination" in output
        assert "/dest/path/file.zip" in output
        assert "error_code" in output
    
    def test_display_success_basic(self):
        """Test display_success with basic information"""
        result = UploadResult(
            success=True,
            message="File 'project.zip' uploaded successfully!",
            data={
                "file_id": 123,
                "filename": "project.zip",
                "filepath": "data/uploads/project.zip"
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        # Verify success banner
        assert "=" * 60 in output
        assert "SUCCESS" in output
        
        # Verify message and details
        assert "File 'project.zip' uploaded successfully!" in output
        assert "Details:" in output
        assert "file_id: 123" in output
        assert "filename: project.zip" in output
        assert "filepath: data/uploads/project.zip" in output
    
    def test_display_success_with_small_file_list(self):
        """Test display_success with less than 5 files"""
        files = ["main.py", "utils.py", "config.py"]
        result = UploadResult(
            success=True,
            message="Upload complete",
            data={
                "file_id": 456,
                "filename": "small_project.zip",
                "file_count": 3,
                "files": files
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        assert "SUCCESS" in output
        assert "Upload complete" in output
        assert "Contains 3 files:" in output
        assert "1. main.py" in output
        assert "2. utils.py" in output
        assert "3. config.py" in output
        # Should not show "more files" message
        assert "more files" not in output
    
    def test_display_success_with_large_file_list(self):
        """Test display_success with more than 5 files"""
        files = [f"file_{i}.py" for i in range(1, 11)]  # 10 files
        result = UploadResult(
            success=True,
            message="Large project uploaded",
            data={
                "file_id": 789,
                "filename": "large_project.zip",
                "file_count": 10,
                "files": files
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        assert "SUCCESS" in output
        assert "Large project uploaded" in output
        assert "Contains 10 files:" in output
        
        # Should show first 5 files
        assert "1. file_1.py" in output
        assert "2. file_2.py" in output
        assert "3. file_3.py" in output
        assert "4. file_4.py" in output
        assert "5. file_5.py" in output
        
        # Should show "more files" message
        assert "and 5 more files" in output
        
        # Should NOT show files 6-10 individually
        assert "file_6.py" not in output
        assert "file_10.py" not in output
    
    def test_display_success_with_empty_file_list(self):
        """Test display_success with empty file list"""
        result = UploadResult(
            success=True,
            message="Empty archive processed",
            data={
                "file_id": 999,
                "filename": "empty.zip",
                "file_count": 0,
                "files": []
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        assert "SUCCESS" in output
        assert "Empty archive processed" in output
        # Empty list should not trigger file display
        assert "Contains 0 files:" not in output.split("Details:")[-1]
    
    def test_display_success_without_files_key(self):
        """Test display_success when files key is not in data"""
        result = UploadResult(
            success=True,
            message="Operation completed",
            data={
                "file_id": 111,
                "status": "processed"
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        assert "SUCCESS" in output
        assert "Operation completed" in output
        assert "file_id: 111" in output
        assert "status: processed" in output
        # Should not crash or show file list
        assert "Contains" not in output


class TestAllErrorTypes:
    """Test all error types can be properly displayed"""
    
    @pytest.mark.parametrize("error_type,message,expected_in_output", [
        ("FILE_NOT_FOUND", "File does not exist: test.zip", ["FILE_NOT_FOUND", "File does not exist"]),
        ("INVALID_FORMAT", "Invalid file format: not a zip", ["INVALID_FORMAT", "Invalid file format"]),
        ("DIRECTORY_ERROR", "Failed to create upload directory", ["DIRECTORY_ERROR", "Failed to create"]),
        ("COPY_ERROR", "File copy failed: permission denied", ["COPY_ERROR", "File copy failed"]),
        ("ZIP_EXTRACTION_ERROR", "ZIP file extraction failed", ["ZIP_EXTRACTION_ERROR", "extraction failed"]),
        ("DATABASE_CONNECTION_ERROR", "Could not connect to database", ["DATABASE_CONNECTION_ERROR", "Could not connect"]),
        ("DATABASE_SAVE_ERROR", "Database save failed: constraint violation", ["DATABASE_SAVE_ERROR", "Database save failed"]),
    ])
    def test_error_type_display(self, error_type, message, expected_in_output):
        """Test that each error type is properly displayed"""
        result = UploadResult(
            success=False,
            message=message,
            error_type=error_type
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)
            output = fake_out.getvalue()
        
        # Verify all expected strings are in output
        for expected in expected_in_output:
            assert expected in output
        
        # Verify error banner
        assert "ERROR" in output
        assert "=" * 60 in output


class TestDisplayOutput:
    """Test output formatting and structure"""
    
    def test_error_output_structure(self):
        """Test that error output has correct structure"""
        result = UploadResult(
            success=False,
            message="Test error",
            error_type="TEST_ERROR",
            data={"key": "value"}
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)
            output = fake_out.getvalue()
        
        lines = output.strip().split('\n')
        
        # Check for section separators
        separator_count = sum(1 for line in lines if "=" * 60 in line)
        assert separator_count >= 2  # At least opening and closing
        
        # Check for required sections
        assert any("ERROR" in line for line in lines)
        assert any("Error Type:" in line for line in lines)
        assert any("Message:" in line for line in lines)
    
    def test_success_output_structure(self):
        """Test that success output has correct structure"""
        result = UploadResult(
            success=True,
            message="Test success",
            data={"file_id": 1}
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        lines = output.strip().split('\n')
        
        # Check for section separators
        separator_count = sum(1 for line in lines if "=" * 60 in line)
        assert separator_count >= 2
        
        # Check for required sections
        assert any("SUCCESS" in line for line in lines)
        assert any("Message:" in line for line in lines)
    
    def test_display_with_special_characters(self):
        """Test display with special characters in message"""
        result = UploadResult(
            success=False,
            message="Error with special chars: 'quotes', \"double\", & ampersand",
            error_type="TEST_ERROR"
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)
            output = fake_out.getvalue()
        
        # Special characters should be preserved
        assert "'" in output
        assert '"' in output
        assert "&" in output


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
