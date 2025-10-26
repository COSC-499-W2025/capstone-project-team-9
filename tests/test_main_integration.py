# tests/test_main_integration.py
import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.main import summarize_project_menu


class TestMainIntegration:
    """Test suite for main.py integration with project summarization"""
    
    @patch('src.main.get_available_projects')
    @patch('src.main.summarize_project')
    def test_summarize_project_menu_no_projects(self, mock_summarize, mock_get_projects):
        """Test summarize_project_menu when no projects are available"""
        mock_get_projects.return_value = []
        
        # Capture stdout to verify output
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            summarize_project_menu()
            output = mock_stdout.getvalue()
            
            assert "No projects found in database." in output
            assert "Please upload a project first using option 1." in output
            mock_summarize.assert_not_called()
    
    @patch('src.main.get_available_projects')
    @patch('src.main.summarize_project')
    def test_summarize_project_menu_with_projects(self, mock_summarize, mock_get_projects):
        """Test summarize_project_menu when projects are available"""
        from datetime import datetime
        
        mock_projects = [
            {
                'id': 1,
                'filename': 'test_project1.zip',
                'created_at': datetime(2024, 1, 1, 10, 0, 0)
            },
            {
                'id': 2,
                'filename': 'test_project2.zip',
                'created_at': datetime(2024, 1, 2, 11, 0, 0)
            }
        ]
        
        mock_get_projects.return_value = mock_projects
        mock_summarize.return_value = "Mock summary output"
        
        # Mock user input to select first project
        with patch('builtins.input', side_effect=['1', 'q']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                summarize_project_menu()
                output = mock_stdout.getvalue()
                
                # Verify project list is displayed
                assert "Available projects:" in output
                assert "1. test_project1.zip" in output
                assert "2. test_project2.zip" in output
                
                # Verify summarization was called
                mock_summarize.assert_called_once_with(1)
    
    @patch('src.main.get_available_projects')
    @patch('src.main.summarize_project')
    def test_summarize_project_menu_invalid_input(self, mock_summarize, mock_get_projects):
        """Test summarize_project_menu with invalid user input"""
        from datetime import datetime
        
        mock_projects = [
            {
                'id': 1,
                'filename': 'test_project.zip',
                'created_at': datetime(2024, 1, 1, 10, 0, 0)
            }
        ]
        
        mock_get_projects.return_value = mock_projects
        
        # Mock user input: invalid number, then quit
        with patch('builtins.input', side_effect=['5', 'q']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                summarize_project_menu()
                output = mock_stdout.getvalue()
                
                # Verify error message for invalid input
                assert "Please enter a number between 1 and 1" in output
                mock_summarize.assert_not_called()
    
    @patch('src.main.get_available_projects')
    @patch('src.main.summarize_project')
    def test_summarize_project_menu_non_numeric_input(self, mock_summarize, mock_get_projects):
        """Test summarize_project_menu with non-numeric input"""
        from datetime import datetime
        
        mock_projects = [
            {
                'id': 1,
                'filename': 'test_project.zip',
                'created_at': datetime(2024, 1, 1, 10, 0, 0)
            }
        ]
        
        mock_get_projects.return_value = mock_projects
        
        # Mock user input: non-numeric, then quit
        with patch('builtins.input', side_effect=['abc', 'q']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                summarize_project_menu()
                output = mock_stdout.getvalue()
                
                # Verify error message for non-numeric input
                assert "Please enter a valid number or 'q' to quit" in output
                mock_summarize.assert_not_called()
    
    @patch('src.main.get_available_projects')
    @patch('src.main.summarize_project')
    def test_summarize_project_menu_quit_option(self, mock_summarize, mock_get_projects):
        """Test summarize_project_menu quit option"""
        from datetime import datetime
        
        mock_projects = [
            {
                'id': 1,
                'filename': 'test_project.zip',
                'created_at': datetime(2024, 1, 1, 10, 0, 0)
            }
        ]
        
        mock_get_projects.return_value = mock_projects
        
        # Mock user input: quit immediately
        with patch('builtins.input', return_value='q'):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                summarize_project_menu()
                output = mock_stdout.getvalue()
                
                # Verify project list is still displayed
                assert "Available projects:" in output
                assert "1. test_project.zip" in output
                
                # Verify summarization was not called
                mock_summarize.assert_not_called()


class TestProjectSummarizerEdgeCases:
    """Test edge cases and error conditions for project summarization"""
    
    def setup_method(self):
        """Set up test fixtures"""
        from src.project_summarizer import ProjectSummarizer
        self.summarizer = ProjectSummarizer()
    
    def test_language_detection_unknown_extensions(self):
        """Test language detection with unknown file extensions"""
        unknown_files = [
            {'file_extension': '.xyz', 'file_name': 'unknown.xyz'},
            {'file_extension': '.abc', 'file_name': 'mystery.abc'},
            {'file_extension': '', 'file_name': 'no_extension'}
        ]
        
        languages = self.summarizer._detect_languages(unknown_files)
        
        assert languages['primary_language'] == 'Unknown'
        assert languages['total_programming_files'] == 0
        assert len(languages['all_languages']) == 0
    
    def test_collaboration_analysis_empty_files(self):
        """Test collaboration analysis with empty file list"""
        collaboration = self.summarizer._analyze_collaboration([])
        
        assert collaboration['collaboration_level'] == 'Likely individual project'
        assert collaboration['indicators']['collaboration_score'] == 0
    
    def test_time_analysis_empty_files(self):
        """Test time analysis with empty file list"""
        time_analysis = self.summarizer._analyze_time_patterns([])
        
        assert 'error' in time_analysis
        assert 'No file data available for time analysis' in time_analysis['error']
    
    def test_project_description_empty_files(self):
        """Test project description generation with empty files"""
        empty_stats = {
            'total_files': 0,
            'total_size_bytes': 0,
            'text_files': 0,
            'binary_files': 0,
            'file_extensions': [],
            'folders': []
        }
        
        description = self.summarizer._generate_project_description([], empty_stats)
        
        assert description['project_type'] == 'general'
        assert '0 files' in description['description']
    
    def test_key_files_identification_edge_cases(self):
        """Test key file identification with various file names"""
        edge_case_files = [
            {'file_name': 'README.txt', 'file_path': 'README.txt'},
            {'file_name': 'MAIN.py', 'file_path': 'MAIN.py'},
            {'file_name': 'index.html', 'file_path': 'index.html'},
            {'file_name': 'app.js', 'file_path': 'app.js'},
            {'file_name': 'config.json', 'file_path': 'config.json'},
            {'file_name': 'package.json', 'file_path': 'package.json'},
            {'file_name': 'requirements.txt', 'file_path': 'requirements.txt'},
            {'file_name': 'normal_file.py', 'file_path': 'normal_file.py'}
        ]
        
        key_files = self.summarizer._identify_key_files(edge_case_files)
        
        # Should identify various key files
        key_file_names = [f['filename'] for f in key_files]
        assert 'README.txt' in key_file_names
        assert 'MAIN.py' in key_file_names
        assert 'index.html' in key_file_names
        assert 'app.js' in key_file_names
        assert 'config.json' in key_file_names
        assert 'package.json' in key_file_names
        assert 'requirements.txt' in key_file_names
        # normal_file.py should not be identified as a key file
        assert 'normal_file.py' not in key_file_names


if __name__ == '__main__':
    pytest.main([__file__])
