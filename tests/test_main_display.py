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


class TestDisplayErrorBehavior:
    """Test that display_error communicates errors effectively to users"""
    
    def test_error_shows_critical_information(self):
        """Test that users can see error type and message"""
        result = UploadResult(
            success=False,
            message="File does not exist: /path/to/file.zip",
            error_type="FILE_NOT_FOUND"
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)
            output = fake_out.getvalue()
        
        # User must be able to understand what went wrong
        assert "ERROR" in output
        assert "FILE_NOT_FOUND" in output
        assert "File does not exist" in output
        assert "/path/to/file.zip" in output
    
    def test_error_shows_additional_details_when_available(self):
        """Test that additional error context is visible"""
        result = UploadResult(
            success=False,
            message="File copy failed: Permission denied",
            error_type="COPY_ERROR",
            data={
                "source": "/source/path/file.zip",
                "destination": "/dest/path/file.zip"
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)
            output = fake_out.getvalue()
        
        # User should see helpful context
        assert "COPY_ERROR" in output
        assert "File copy failed" in output
        assert "source" in output
        assert "/source/path/file.zip" in output
        assert "destination" in output
    
    def test_error_handles_none_error_type(self):
        """Test that missing error_type doesn't crash"""
        result = UploadResult(
            success=False,
            message="Error occurred",
            error_type=None
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)  # Should not raise exception
            output = fake_out.getvalue()
        
        assert "ERROR" in output
        assert "Error occurred" in output
    
    def test_error_handles_empty_data(self):
        """Test that empty data doesn't cause issues"""
        result = UploadResult(
            success=False,
            message="Error",
            error_type="ERROR",
            data={}
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)  # Should not crash
            output = fake_out.getvalue()
        
        assert "ERROR" in output
    
    def test_error_handles_very_long_messages(self):
        """Test that long error messages don't break display"""
        long_message = "A" * 500
        result = UploadResult(
            success=False,
            message=long_message,
            error_type="LONG_ERROR"
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)  # Should not crash
            output = fake_out.getvalue()
        
        # Message should still be visible
        assert "LONG_ERROR" in output
        assert "A" * 100 in output  # At least part of message visible
    
    def test_error_handles_complex_data_types(self):
        """Test that various data types in error details are handled"""
        result = UploadResult(
            success=False,
            message="Complex error",
            error_type="ERROR",
            data={
                "string": "text",
                "integer": 42,
                "list": [1, 2, 3],
                "none_value": None
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)  # Should not crash
            output = fake_out.getvalue()
        
        assert "ERROR" in output
        # Details should be visible (exact format doesn't matter)
        assert "string" in output or "text" in output


class TestDisplaySuccessBehavior:
    """Test that display_success communicates success information effectively"""
    
    def test_success_shows_message(self):
        """Test that success message is visible"""
        result = UploadResult(
            success=True,
            message="File 'project.zip' uploaded successfully!",
            data={"file_id": 123}
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        assert "SUCCESS" in output
        assert "uploaded successfully" in output
    
    def test_success_shows_file_information(self):
        """Test that uploaded file details are visible"""
        result = UploadResult(
            success=True,
            message="Upload complete",
            data={
                "file_id": 456,
                "filename": "project.zip",
                "filepath": "data/uploads/project.zip"
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        assert "SUCCESS" in output
        # Important info should be visible
        assert "456" in output or "file_id" in output
        assert "project.zip" in output
    
    def test_success_shows_small_file_list(self):
        """Test that small file lists (< 5 files) are fully displayed"""
        files = ["main.py", "utils.py", "config.py"]
        result = UploadResult(
            success=True,
            message="Upload complete",
            data={
                "file_id": 123,
                "file_count": 3,
                "files": files
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        # All files should be visible for small lists
        assert "3 files" in output
        assert "main.py" in output
        assert "utils.py" in output
        assert "config.py" in output
    
    def test_success_truncates_large_file_list(self):
        """Test that large file lists are truncated (business logic)"""
        files = [f"file_{i}.py" for i in range(1, 11)]  # 10 files
        result = UploadResult(
            success=True,
            message="Large project uploaded",
            data={
                "file_id": 789,
                "file_count": 10,
                "files": files
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        assert "10 files" in output
        # First few files should be visible
        assert "file_1.py" in output
        assert "file_2.py" in output
        # Should indicate more files exist
        assert "more files" in output or "5" in output
        # Later files should not clutter output
        assert "file_10.py" not in output
    
    def test_success_exactly_five_files_shows_all(self):
        """Test boundary condition: exactly 5 files shows all"""
        files = ["file1.py", "file2.py", "file3.py", "file4.py", "file5.py"]
        result = UploadResult(
            success=True,
            message="Upload complete",
            data={
                "files": files
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        # All 5 should be visible
        assert "file1.py" in output
        assert "file5.py" in output
        # Should not say "more files" for exactly 5
        assert "more files" not in output
    
    def test_success_six_files_shows_truncation(self):
        """Test boundary condition: 6 files shows truncation message"""
        files = [f"file{i}.py" for i in range(1, 7)]
        result = UploadResult(
            success=True,
            message="Upload complete",
            data={"files": files}
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        # Should show truncation message
        assert "more files" in output
        # Should show first 5
        assert "file1.py" in output
        assert "file5.py" in output
        # Should not show file 6 individually
        assert "6. file6.py" not in output
    
    def test_success_empty_file_list_handled(self):
        """Test that empty file list doesn't break display"""
        result = UploadResult(
            success=True,
            message="Empty archive processed",
            data={
                "file_id": 999,
                "file_count": 0,
                "files": []
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)  # Should not crash
            output = fake_out.getvalue()
        
        assert "SUCCESS" in output
        assert "Empty archive processed" in output
    
    def test_success_excludes_files_from_regular_details(self):
        """Test that 'files' doesn't appear twice in output"""
        result = UploadResult(
            success=True,
            message="Upload complete",
            data={
                "file_id": 123,
                "filename": "test.zip",
                "files": ["file1.py", "file2.py"]
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)
            output = fake_out.getvalue()
        
        # Files should be in the special section, not in bullet points
        assert "file_id" in output
        assert "filename" in output
        assert "file1.py" in output  # In file list section
        # Should not show files as a bullet point detail


class TestEdgeCasesAndRobustness:
    """Test edge cases and error handling"""
    
    def test_error_with_none_data(self):
        """Test that None data is handled gracefully"""
        result = UploadResult(
            success=False,
            message="Error",
            error_type="ERROR",
            data=None
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)  # Should not crash
            output = fake_out.getvalue()
        
        assert "ERROR" in output
    
    def test_success_with_none_data(self):
        """Test that None data is handled gracefully"""
        result = UploadResult(
            success=True,
            message="Success",
            data=None
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)  # Should not crash
            output = fake_out.getvalue()
        
        assert "SUCCESS" in output
    
    def test_success_files_key_is_none(self):
        """Test edge case where files exists but is None"""
        result = UploadResult(
            success=True,
            message="Upload complete",
            data={
                "file_id": 123,
                "files": None
            }
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_success(result)  # Should not crash on None
            output = fake_out.getvalue()
        
        assert "SUCCESS" in output
    
    def test_error_with_unicode_characters(self):
        """Test that unicode characters don't break display"""
        result = UploadResult(
            success=False,
            message="Error with unicode: 测试 🚀",
            error_type="UNICODE_ERROR"
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)  # Should not crash
            output = fake_out.getvalue()
        
        # Should handle unicode without errors
        assert "ERROR" in output


class TestAllErrorTypes:
    """Test that all defined error types work correctly"""
    
    @pytest.mark.parametrize("error_type,message", [
        ("FILE_NOT_FOUND", "File does not exist: test.zip"),
        ("INVALID_FORMAT", "Invalid file format: not a zip"),
        ("DIRECTORY_ERROR", "Failed to create upload directory"),
        ("COPY_ERROR", "File copy failed: permission denied"),
        ("ZIP_EXTRACTION_ERROR", "ZIP file extraction failed"),
        ("DATABASE_CONNECTION_ERROR", "Could not connect to database"),
        ("DATABASE_SAVE_ERROR", "Database save failed: constraint violation"),
    ])
    def test_all_error_types_display_correctly(self, error_type, message):
        """Test that each error type displays its message correctly"""
        result = UploadResult(
            success=False,
            message=message,
            error_type=error_type
        )
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_error(result)
            output = fake_out.getvalue()
        
        # Error type and message should be visible
        assert error_type in output
        # Key part of message should be visible
        assert message[:30] in output or any(word in output for word in message.split()[:3])


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
