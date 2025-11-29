"""
Tests for resume CLI menu handlers.
Tests the user-facing resume generation, viewing, deletion, and PDF export functionality.
"""
import sys
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock, Mock, call
from io import StringIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestHandleGenerateResume:
    """Test suite for handle_generate_resume function."""
    
    @patch('resume.resume_manager.ResumeManager.store_user_resume')
    @patch('resume.resume_manager.ResumeManager.generate_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_generate_resume_new(self, mock_input, mock_exists, mock_generate, mock_store):
        """Test generating a new resume when none exists."""
        from cli.menus import handle_generate_resume
        
        # Mock that no resume exists
        mock_exists.return_value = False
        
        # Mock user inputs: top_count = 5 (default), then Enter to continue
        mock_input.side_effect = ['', '']
        
        # Mock successful generation with enriched data
        mock_resume_data = {
            'total_projects_analyzed': 10,
            'top_projects_displayed': 5,
            'all_skills': ['Python', 'JavaScript', 'Docker'],
            'summary_stats': {
                'total_lines_of_code': 5000,
                'total_files': 50,
                'unique_languages': 3,
                'unique_frameworks': 2
            }
        }
        mock_generate.return_value = mock_resume_data
        mock_store.return_value = True
        
        # Execute
        handle_generate_resume()
        
        # Verify calls
        mock_exists.assert_called_once_with("default_user")
        mock_generate.assert_called_once_with("default_user", top_projects_count=5)
        mock_store.assert_called_once_with("default_user", mock_resume_data)
    
    @patch('resume.resume_manager.ResumeManager.store_user_resume')
    @patch('resume.resume_manager.ResumeManager.generate_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_generate_resume_regenerate_confirmed(self, mock_input, mock_exists, mock_generate, mock_store):
        """Test regenerating resume when user confirms."""
        from cli.menus import handle_generate_resume
        
        # Mock that resume exists
        mock_exists.return_value = True
        
        # Mock user inputs: yes to regenerate, 3 top projects, Enter to continue
        mock_input.side_effect = ['y', '3', '']
        
        # Mock successful generation
        mock_resume_data = {
            'total_projects_analyzed': 10,
            'top_projects_displayed': 3,
            'all_skills': ['Python'],
            'summary_stats': {
                'total_lines_of_code': 3000,
                'total_files': 30,
                'unique_languages': 1,
                'unique_frameworks': 1
            }
        }
        mock_generate.return_value = mock_resume_data
        mock_store.return_value = True
        
        # Execute
        handle_generate_resume()
        
        # Verify regeneration happened
        mock_generate.assert_called_once_with("default_user", top_projects_count=3)
    
    @patch('resume.resume_manager.ResumeManager.generate_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_generate_resume_cancel_regenerate(self, mock_input, mock_exists, mock_generate):
        """Test cancelling regeneration when resume exists."""
        from cli.menus import handle_generate_resume
        
        # Mock that resume exists
        mock_exists.return_value = True
        
        # Mock user input: no to regenerate
        mock_input.return_value = 'no'
        
        # Execute
        handle_generate_resume()
        
        # Verify generation was not called
        mock_generate.assert_not_called()
    
    @patch('resume.resume_manager.ResumeManager.store_user_resume')
    @patch('resume.resume_manager.ResumeManager.generate_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_generate_resume_invalid_then_valid_count(self, mock_input, mock_exists, mock_generate, mock_store):
        """Test handling invalid project count input."""
        from cli.menus import handle_generate_resume
        
        # Mock that no resume exists
        mock_exists.return_value = False
        
        # Mock user inputs: invalid count, then valid count, then Enter
        mock_input.side_effect = ['0', '11', 'abc', '7', '']
        
        # Mock successful generation
        mock_resume_data = {
            'total_projects_analyzed': 10,
            'top_projects_displayed': 7,
            'all_skills': [],
            'summary_stats': {}
        }
        mock_generate.return_value = mock_resume_data
        mock_store.return_value = True
        
        # Execute
        handle_generate_resume()
        
        # Verify correct count was used
        mock_generate.assert_called_once_with("default_user", top_projects_count=7)
    
    @patch('resume.resume_manager.ResumeManager.store_user_resume')
    @patch('resume.resume_manager.ResumeManager.generate_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_generate_resume_no_projects(self, mock_input, mock_exists, mock_generate, mock_store):
        """Test handling when no projects exist."""
        from cli.menus import handle_generate_resume
        
        # Mock that no resume exists
        mock_exists.return_value = False
        
        # Mock user inputs
        mock_input.side_effect = ['', '']
        
        # Mock failed generation (no projects)
        mock_generate.return_value = None
        
        # Execute
        handle_generate_resume()
        
        # Verify store was not called
        mock_store.assert_not_called()
    
    @patch('resume.resume_manager.ResumeManager.store_user_resume')
    @patch('resume.resume_manager.ResumeManager.generate_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_generate_resume_store_failure(self, mock_input, mock_exists, mock_generate, mock_store):
        """Test handling when resume storage fails."""
        from cli.menus import handle_generate_resume
        
        # Mock that no resume exists
        mock_exists.return_value = False
        
        # Mock user inputs
        mock_input.side_effect = ['', '']
        
        # Mock successful generation but failed storage
        mock_resume_data = {
            'total_projects_analyzed': 5,
            'top_projects_displayed': 5,
            'all_skills': ['Python'],
            'summary_stats': {}
        }
        mock_generate.return_value = mock_resume_data
        mock_store.return_value = False
        
        # Execute - should not raise exception
        handle_generate_resume()
        
        # Verify store was attempted
        mock_store.assert_called_once()


class TestHandleViewResume:
    """Test suite for handle_view_resume function."""
    
    @patch('resume.resume_formatter.ResumeFormatter.get_formatted_resume')
    @patch('resume.resume_manager.ResumeManager.get_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_view_resume_text_format(self, mock_input, mock_exists, mock_get_resume, mock_format):
        """Test viewing resume in text format."""
        from cli.menus import handle_view_resume
        
        # Mock that resume exists
        mock_exists.return_value = True
        
        # Mock resume data
        mock_resume_data = {
            'user_id': 'default_user',
            'all_skills': ['Python'],
            'summary_stats': {}
        }
        mock_get_resume.return_value = {
            'resume_data': mock_resume_data
        }
        
        # Mock user input: format choice 1 (text), then Enter
        mock_input.side_effect = ['1', '']
        
        # Mock formatted output
        mock_format.return_value = "Formatted resume text"
        
        # Execute
        handle_view_resume()
        
        # Verify formatter was called with correct format
        mock_format.assert_called_once_with(mock_resume_data, 'text')
    
    @patch('resume.resume_formatter.ResumeFormatter.get_formatted_resume')
    @patch('resume.resume_manager.ResumeManager.get_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_view_resume_markdown_format(self, mock_input, mock_exists, mock_get_resume, mock_format):
        """Test viewing resume in markdown format."""
        from cli.menus import handle_view_resume
        
        # Mock that resume exists
        mock_exists.return_value = True
        
        # Mock resume data
        mock_resume_data = {'user_id': 'default_user'}
        mock_get_resume.return_value = {
            'resume_data': mock_resume_data
        }
        
        # Mock user input: format choice 2 (markdown)
        mock_input.side_effect = ['2', '']
        
        # Mock formatted output
        mock_format.return_value = "# Resume"
        
        # Execute
        handle_view_resume()
        
        # Verify formatter was called with markdown format
        mock_format.assert_called_once_with(mock_resume_data, 'markdown')
    
    @patch('resume.resume_formatter.ResumeFormatter.get_formatted_resume')
    @patch('resume.resume_manager.ResumeManager.get_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_view_resume_json_format(self, mock_input, mock_exists, mock_get_resume, mock_format):
        """Test viewing resume in JSON format."""
        from cli.menus import handle_view_resume
        
        # Mock that resume exists
        mock_exists.return_value = True
        
        # Mock resume data
        mock_resume_data = {'user_id': 'default_user'}
        mock_get_resume.return_value = {
            'resume_data': mock_resume_data
        }
        
        # Mock user input: format choice 3 (json)
        mock_input.side_effect = ['3', '']
        
        # Mock formatted output
        mock_format.return_value = '{"user_id": "default_user"}'
        
        # Execute
        handle_view_resume()
        
        # Verify formatter was called with json format
        mock_format.assert_called_once_with(mock_resume_data, 'json')
    
    @patch('resume.resume_manager.ResumeManager.get_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_view_resume_not_found(self, mock_input, mock_exists, mock_get_resume):
        """Test viewing resume when none exists."""
        from cli.menus import handle_view_resume
        
        # Mock that no resume exists
        mock_exists.return_value = False
        
        # Mock user input
        mock_input.return_value = ''
        
        # Execute
        handle_view_resume()
        
        # Verify get_user_resume was not called
        mock_get_resume.assert_not_called()
    
    @patch('resume.resume_formatter.ResumeFormatter.get_formatted_resume')
    @patch('resume.resume_manager.ResumeManager.get_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_view_resume_default_format(self, mock_input, mock_exists, mock_get_resume, mock_format):
        """Test viewing resume with default format (empty input)."""
        from cli.menus import handle_view_resume
        
        # Mock that resume exists
        mock_exists.return_value = True
        
        # Mock resume data
        mock_resume_data = {'user_id': 'default_user'}
        mock_get_resume.return_value = {
            'resume_data': mock_resume_data
        }
        
        # Mock user input: empty (default to text), then Enter
        mock_input.side_effect = ['', '']
        
        # Mock formatted output
        mock_format.return_value = "Formatted resume text"
        
        # Execute
        handle_view_resume()
        
        # Verify formatter was called with text format
        mock_format.assert_called_once_with(mock_resume_data, 'text')


class TestHandlePDFExport:
    """Test suite for PDF export functionality."""
    
    @patch('resume.resume_formatter.ResumeFormatter.format_pdf')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    @patch('builtins.input')
    def test_pdf_export_default_filename(self, mock_input, mock_exists, mock_getsize, mock_format_pdf):
        """Test PDF export with default filename."""
        from cli.menus import _handle_pdf_export
        
        # Mock user input: empty (default filename)
        mock_input.return_value = ''
        
        # Mock successful PDF generation
        mock_format_pdf.return_value = True
        mock_exists.return_value = True
        mock_getsize.return_value = 12345
        
        # Mock resume data
        mock_resume_data = {'user_id': 'default_user'}
        
        # Execute
        _handle_pdf_export(mock_resume_data)
        
        # Verify format_pdf was called
        mock_format_pdf.assert_called_once()
        
        # Verify the output path ends with resume.pdf
        call_args = mock_format_pdf.call_args
        output_path = call_args[0][1]
        assert output_path.endswith('resume.pdf')
    
    @patch('resume.resume_formatter.ResumeFormatter.format_pdf')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    @patch('builtins.input')
    def test_pdf_export_custom_filename(self, mock_input, mock_exists, mock_getsize, mock_format_pdf):
        """Test PDF export with custom filename."""
        from cli.menus import _handle_pdf_export
        
        # Mock user input: custom filename
        mock_input.return_value = 'my_resume'
        
        # Mock successful PDF generation
        mock_format_pdf.return_value = True
        mock_exists.return_value = True
        mock_getsize.return_value = 12345
        
        # Mock resume data
        mock_resume_data = {'user_id': 'default_user'}
        
        # Execute
        _handle_pdf_export(mock_resume_data)
        
        # Verify format_pdf was called with custom filename (with .pdf extension)
        call_args = mock_format_pdf.call_args
        output_path = call_args[0][1]
        assert output_path.endswith('my_resume.pdf')
    
    @patch('resume.resume_formatter.ResumeFormatter.format_pdf')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    @patch('builtins.input')
    def test_pdf_export_with_pdf_extension(self, mock_input, mock_exists, mock_getsize, mock_format_pdf):
        """Test PDF export when user includes .pdf extension."""
        from cli.menus import _handle_pdf_export
        
        # Mock user input: filename with .pdf already
        mock_input.return_value = 'my_resume.pdf'
        
        # Mock successful PDF generation
        mock_format_pdf.return_value = True
        mock_exists.return_value = True
        mock_getsize.return_value = 12345
        
        # Mock resume data
        mock_resume_data = {'user_id': 'default_user'}
        
        # Execute
        _handle_pdf_export(mock_resume_data)
        
        # Verify filename doesn't have double .pdf
        call_args = mock_format_pdf.call_args
        output_path = call_args[0][1]
        assert output_path.endswith('my_resume.pdf')
        assert not output_path.endswith('.pdf.pdf')
    
    @patch('resume.resume_formatter.ResumeFormatter.format_pdf')
    @patch('builtins.input')
    def test_pdf_export_failure(self, mock_input, mock_format_pdf):
        """Test PDF export when generation fails."""
        from cli.menus import _handle_pdf_export
        
        # Mock user input
        mock_input.return_value = ''
        
        # Mock failed PDF generation
        mock_format_pdf.return_value = False
        
        # Mock resume data
        mock_resume_data = {'user_id': 'default_user'}
        
        # Execute - should not raise exception
        _handle_pdf_export(mock_resume_data)
        
        # Verify format_pdf was called
        mock_format_pdf.assert_called_once()
    
    @patch('resume.resume_formatter.ResumeFormatter.format_pdf')
    @patch('resume.resume_manager.ResumeManager.get_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    @patch('builtins.input')
    def test_view_resume_pdf_option(self, mock_input, mock_exists_file, mock_getsize, 
                                     mock_resume_exists, mock_get_resume, mock_format_pdf):
        """Test selecting PDF export option from view menu."""
        from cli.menus import handle_view_resume
        
        # Mock that resume exists
        mock_resume_exists.return_value = True
        
        # Mock resume data
        mock_resume_data = {'user_id': 'default_user'}
        mock_get_resume.return_value = {
            'resume_data': mock_resume_data
        }
        
        # Mock user input: format choice 4 (PDF), empty filename, then Enter
        mock_input.side_effect = ['4', '', '']
        
        # Mock successful PDF generation
        mock_format_pdf.return_value = True
        mock_exists_file.return_value = True
        mock_getsize.return_value = 12345
        
        # Execute
        handle_view_resume()
        
        # Verify PDF format was called
        mock_format_pdf.assert_called_once()


class TestHandleDeleteResume:
    """Test suite for handle_delete_resume function."""
    
    @patch('resume.resume_manager.ResumeManager.delete_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_delete_resume_confirmed(self, mock_input, mock_exists, mock_delete):
        """Test deleting resume when user confirms."""
        from cli.menus import handle_delete_resume
        
        # Mock that resume exists
        mock_exists.return_value = True
        
        # Mock user inputs: yes to confirm, then Enter
        mock_input.side_effect = ['y', '']
        
        # Mock successful deletion
        mock_delete.return_value = True
        
        # Execute
        handle_delete_resume()
        
        # Verify deletion was called
        mock_delete.assert_called_once_with("default_user")
    
    @patch('resume.resume_manager.ResumeManager.delete_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_delete_resume_cancelled(self, mock_input, mock_exists, mock_delete):
        """Test cancelling resume deletion."""
        from cli.menus import handle_delete_resume
        
        # Mock that resume exists
        mock_exists.return_value = True
        
        # Mock user inputs: no to confirm, then Enter
        mock_input.side_effect = ['no', '']
        
        # Execute
        handle_delete_resume()
        
        # Verify deletion was not called
        mock_delete.assert_not_called()
    
    @patch('resume.resume_manager.ResumeManager.delete_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_delete_resume_not_found(self, mock_input, mock_exists, mock_delete):
        """Test deleting resume when none exists."""
        from cli.menus import handle_delete_resume
        
        # Mock that no resume exists
        mock_exists.return_value = False
        
        # Mock user input
        mock_input.return_value = ''
        
        # Execute
        handle_delete_resume()
        
        # Verify delete was not called
        mock_delete.assert_not_called()
    
    @patch('resume.resume_manager.ResumeManager.delete_user_resume')
    @patch('resume.resume_manager.ResumeManager.resume_exists')
    @patch('builtins.input')
    def test_delete_resume_failure(self, mock_input, mock_exists, mock_delete):
        """Test handling when deletion fails."""
        from cli.menus import handle_delete_resume
        
        # Mock that resume exists
        mock_exists.return_value = True
        
        # Mock user inputs: yes to confirm, then Enter
        mock_input.side_effect = ['yes', '']
        
        # Mock failed deletion
        mock_delete.return_value = False
        
        # Execute - should not raise exception
        handle_delete_resume()
        
        # Verify deletion was attempted
        mock_delete.assert_called_once_with("default_user")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])