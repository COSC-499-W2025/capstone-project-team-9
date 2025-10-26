# tests/test_project_summarizer.py
import sys
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.project_summarizer import ProjectSummarizer, summarize_project, get_available_projects


class TestProjectSummarizer:
    """Test suite for ProjectSummarizer functionality"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.summarizer = ProjectSummarizer()
        
        # Sample project info
        self.sample_project_info = {
            'id': 1,
            'filename': 'test_project.zip',
            'created_at': datetime(2024, 1, 1, 10, 0, 0)
        }
        
        # Sample file contents
        self.sample_file_contents = [
            {
                'id': 1,
                'file_path': 'test_project/main.py',
                'file_name': 'main.py',
                'file_extension': '.py',
                'file_size': 1024,
                'file_content': '50',
                'content_type': 'text/x-python',
                'is_binary': False,
                'created_at': datetime(2024, 1, 1, 10, 0, 0)
            },
            {
                'id': 2,
                'file_path': 'test_project/README.md',
                'file_name': 'README.md',
                'file_extension': '.md',
                'file_size': 512,
                'file_content': '25',
                'content_type': 'text/markdown',
                'is_binary': False,
                'created_at': datetime(2024, 1, 1, 10, 5, 0)
            },
            {
                'id': 3,
                'file_path': 'test_project/src/utils.py',
                'file_name': 'utils.py',
                'file_extension': '.py',
                'file_size': 256,
                'file_content': '30',
                'content_type': 'text/x-python',
                'is_binary': False,
                'created_at': datetime(2024, 1, 1, 10, 10, 0)
            }
        ]
        
        # Sample file statistics
        self.sample_file_stats = {
            'total_files': 3,
            'total_size_bytes': 1792,
            'text_files': 3,
            'binary_files': 0,
            'file_extensions': [
                {'extension': '.py', 'count': 2},
                {'extension': '.md', 'count': 1}
            ],
            'folders': [
                {'folder': 'test_project', 'file_count': 3}
            ]
        }
    
    def test_language_detection_basic(self):
        """Test basic language detection functionality"""
        languages = self.summarizer._detect_languages(self.sample_file_contents)
        
        assert languages['primary_language'] == 'Python'
        assert languages['total_programming_files'] == 3
        assert len(languages['all_languages']) == 2
        assert languages['all_languages'][0]['language'] == 'Python'
        assert languages['all_languages'][0]['file_count'] == 2
        assert languages['all_languages'][1]['language'] == 'Markdown'
        assert languages['all_languages'][1]['file_count'] == 1
    
    def test_language_detection_no_files(self):
        """Test language detection with no files"""
        languages = self.summarizer._detect_languages([])
        
        assert languages['primary_language'] == 'Unknown'
        assert languages['total_programming_files'] == 0
        assert len(languages['all_languages']) == 0
    
    def test_language_detection_multiple_languages(self):
        """Test language detection with multiple programming languages"""
        multi_lang_files = [
            {'file_extension': '.py', 'file_name': 'main.py'},
            {'file_extension': '.js', 'file_name': 'app.js'},
            {'file_extension': '.java', 'file_name': 'Main.java'},
            {'file_extension': '.cpp', 'file_name': 'main.cpp'},
            {'file_extension': '.py', 'file_name': 'utils.py'}
        ]
        
        languages = self.summarizer._detect_languages(multi_lang_files)
        
        assert languages['primary_language'] == 'Python'
        assert languages['total_programming_files'] == 5
        assert len(languages['all_languages']) == 4
        
        # Check that languages are sorted by count
        assert languages['all_languages'][0]['language'] == 'Python'
        assert languages['all_languages'][0]['file_count'] == 2
    
    def test_project_description_generation(self):
        """Test project description generation"""
        description = self.summarizer._generate_project_description(
            self.sample_file_contents, 
            self.sample_file_stats
        )
        
        assert description['project_type'] == 'backend'
        assert 'backend/server application' in description['description']
        assert len(description['key_files']) > 0
        
        # Check that main.py is identified as a key file
        key_file_names = [f['filename'] for f in description['key_files']]
        assert 'main.py' in key_file_names
    
    def test_project_description_web_project(self):
        """Test project description for web projects"""
        web_files = [
            {'file_extension': '.html', 'file_name': 'index.html', 'file_path': 'index.html'},
            {'file_extension': '.css', 'file_name': 'style.css', 'file_path': 'style.css'},
            {'file_extension': '.js', 'file_name': 'script.js', 'file_path': 'script.js'}
        ]
        
        web_stats = {
            'total_files': 3,
            'total_size_bytes': 1500,
            'text_files': 3,
            'binary_files': 0,
            'file_extensions': [],
            'folders': []
        }
        
        description = self.summarizer._generate_project_description(web_files, web_stats)
        
        assert description['project_type'] == 'web'
        assert 'web application' in description['description']
    
    def test_collaboration_analysis_individual(self):
        """Test collaboration analysis for individual projects"""
        collaboration = self.summarizer._analyze_collaboration(self.sample_file_contents)
        
        assert 'collaboration_level' in collaboration
        assert 'indicators' in collaboration
        assert 'analysis' in collaboration
        assert collaboration['indicators']['collaboration_score'] >= 0
        assert collaboration['indicators']['collaboration_score'] <= 100
    
    def test_collaboration_analysis_team_project(self):
        """Test collaboration analysis for team projects"""
        team_files = [
            {'file_name': '.gitignore'},
            {'file_name': 'team_utils.py'},
            {'file_name': 'shared_config.py'},
            {'file_name': 'common_helpers.py'}
        ]
        
        collaboration = self.summarizer._analyze_collaboration(team_files)
        
        # Should have higher collaboration score due to Git files and team indicators
        assert collaboration['indicators']['collaboration_score'] > 40
    
    def test_time_analysis_basic(self):
        """Test basic time analysis functionality"""
        time_analysis = self.summarizer._analyze_time_patterns(self.sample_file_contents)
        
        assert 'earliest_file' in time_analysis
        assert 'latest_file' in time_analysis
        assert 'development_span_days' in time_analysis
        assert 'development_intensity' in time_analysis
        assert 'files_per_day' in time_analysis
        
        # Should be single day development based on sample data
        assert time_analysis['development_intensity'] == 'Single day development'
        assert time_analysis['development_span_days'] == 0
    
    def test_time_analysis_long_term_project(self):
        """Test time analysis for long-term projects"""
        long_term_files = []
        base_date = datetime(2024, 1, 1)
        
        # Create files spread over 2 months
        for i in range(10):
            file_date = base_date + timedelta(days=i*6)  # Every 6 days
            long_term_files.append({
                'created_at': file_date
            })
        
        time_analysis = self.summarizer._analyze_time_patterns(long_term_files)
        
        assert time_analysis['development_intensity'] == 'Long-term project (over 1 month)'
        assert time_analysis['development_span_days'] > 30
    
    def test_time_analysis_no_timestamps(self):
        """Test time analysis with no timestamp data"""
        files_no_time = [
            {'file_name': 'test.py'},
            {'file_name': 'test2.py'}
        ]
        
        time_analysis = self.summarizer._analyze_time_patterns(files_no_time)
        
        assert 'error' in time_analysis
        assert 'No timestamp data available' in time_analysis['error']
    
    @patch('src.project_summarizer.get_project_by_id')
    @patch('src.project_summarizer.get_file_contents_by_upload_id')
    @patch('src.project_summarizer.get_file_statistics')
    def test_generate_project_summary_success(self, mock_stats, mock_contents, mock_project):
        """Test successful project summary generation"""
        # Mock the dependencies
        mock_project.return_value = self.sample_project_info
        mock_contents.return_value = self.sample_file_contents
        mock_stats.return_value = self.sample_file_stats
        
        summary = self.summarizer.generate_project_summary(1)
        
        # Check that all required sections are present
        assert 'project_info' in summary
        assert 'languages' in summary
        assert 'project_description' in summary
        assert 'collaboration_analysis' in summary
        assert 'time_analysis' in summary
        assert 'file_statistics' in summary
        assert 'summary_generated_at' in summary
        
        # Check project info
        assert summary['project_info']['id'] == 1
        assert summary['project_info']['filename'] == 'test_project.zip'
        
        # Check languages
        assert summary['languages']['primary_language'] == 'Python'
        assert summary['languages']['total_programming_files'] == 3
    
    @patch('src.project_summarizer.get_project_by_id')
    def test_generate_project_summary_project_not_found(self, mock_project):
        """Test project summary generation when project is not found"""
        mock_project.return_value = None
        
        summary = self.summarizer.generate_project_summary(999)
        
        assert 'error' in summary
        assert summary['error'] == 'Project not found'
    
    @patch('src.project_summarizer.get_project_by_id')
    @patch('src.project_summarizer.get_file_contents_by_upload_id')
    def test_generate_project_summary_no_file_contents(self, mock_contents, mock_project):
        """Test project summary generation when no file contents are found"""
        mock_project.return_value = self.sample_project_info
        mock_contents.return_value = []
        
        summary = self.summarizer.generate_project_summary(1)
        
        assert 'error' in summary
        assert summary['error'] == 'No file contents found for this project'
    
    def test_format_summary_for_display(self):
        """Test summary formatting for display"""
        sample_summary = {
            'project_info': {
                'id': 1,
                'filename': 'test_project.zip',
                'created_at': '2024-01-01 10:00:00'
            },
            'languages': {
                'primary_language': 'Python',
                'total_programming_files': 3,
                'all_languages': [
                    {'language': 'Python', 'file_count': 2},
                    {'language': 'Markdown', 'file_count': 1}
                ]
            },
            'project_description': {
                'project_type': 'backend',
                'description': 'A backend/server application with 3 files (0.0 MB).',
                'key_files': [
                    {'filename': 'main.py', 'type': 'main/documentation'}
                ]
            },
            'collaboration_analysis': {
                'collaboration_level': 'Possibly collaborative',
                'indicators': {'collaboration_score': 40},
                'analysis': 'Based on file structure and Git presence.'
            },
            'time_analysis': {
                'development_intensity': 'Single day development',
                'development_span_days': 0,
                'files_per_day': 3,
                'earliest_file': '2024-01-01 10:00:00',
                'latest_file': '2024-01-01 10:10:00'
            },
            'file_statistics': {
                'total_files': 3,
                'text_files': 3,
                'binary_files': 0,
                'total_size_bytes': 1792
            },
            'summary_generated_at': '2024-01-01 12:00:00'
        }
        
        formatted = self.summarizer.format_summary_for_display(sample_summary)
        
        # Check that key information is present in formatted output
        assert 'PROJECT SUMMARY: test_project.zip' in formatted
        assert 'Project Information:' in formatted
        assert 'Programming Languages:' in formatted
        assert 'Primary Language: Python' in formatted
        assert 'Project Description:' in formatted
        assert 'Collaboration Analysis:' in formatted
        assert 'Time Analysis:' in formatted
        assert 'File Statistics:' in formatted
    
    def test_format_summary_for_display_error(self):
        """Test summary formatting when there's an error"""
        error_summary = {'error': 'Test error message'}
        
        formatted = self.summarizer.format_summary_for_display(error_summary)
        
        assert 'Error: Test error message' in formatted


class TestSummarizeProjectFunction:
    """Test suite for the convenience summarize_project function"""
    
    @patch('src.project_summarizer.ProjectSummarizer')
    def test_summarize_project_success(self, mock_summarizer_class):
        """Test the summarize_project convenience function"""
        # Mock the summarizer instance
        mock_summarizer = Mock()
        mock_summarizer_class.return_value = mock_summarizer
        
        # Mock the summary generation and formatting
        mock_summary = {'test': 'summary'}
        mock_formatted = 'Formatted summary output'
        mock_summarizer.generate_project_summary.return_value = mock_summary
        mock_summarizer.format_summary_for_display.return_value = mock_formatted
        
        result = summarize_project(1)
        
        # Verify the function calls
        mock_summarizer_class.assert_called_once()
        mock_summarizer.generate_project_summary.assert_called_once_with(1)
        mock_summarizer.format_summary_for_display.assert_called_once_with(mock_summary)
        
        assert result == mock_formatted


class TestGetAvailableProjects:
    """Test suite for the get_available_projects function"""
    
    @patch('src.project_summarizer.get_connection')
    def test_get_available_projects_success(self, mock_get_connection):
        """Test successful retrieval of available projects"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock database results
        mock_projects = [
            (1, 'project1.zip', datetime(2024, 1, 1, 10, 0, 0)),
            (2, 'project2.zip', datetime(2024, 1, 2, 11, 0, 0))
        ]
        mock_cursor.fetchall.return_value = mock_projects
        
        projects = get_available_projects()
        
        # Verify the function calls
        mock_get_connection.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        
        # Check results
        assert len(projects) == 2
        assert projects[0]['id'] == 1
        assert projects[0]['filename'] == 'project1.zip'
        assert projects[1]['id'] == 2
        assert projects[1]['filename'] == 'project2.zip'
    
    @patch('src.project_summarizer.get_connection')
    def test_get_available_projects_no_connection(self, mock_get_connection):
        """Test get_available_projects when database connection fails"""
        mock_get_connection.return_value = None
        
        projects = get_available_projects()
        
        assert projects == []
    
    @patch('src.project_summarizer.get_connection')
    def test_get_available_projects_database_error(self, mock_get_connection):
        """Test get_available_projects when database query fails"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock database error
        mock_cursor.execute.side_effect = Exception("Database error")
        
        projects = get_available_projects()
        
        assert projects == []


class TestProjectSummarizerIntegration:
    """Integration tests for the project summarization feature"""
    
    @patch('src.project_summarizer.get_project_by_id')
    @patch('src.project_summarizer.get_file_contents_by_upload_id')
    @patch('src.project_summarizer.get_file_statistics')
    def test_full_summarization_workflow(self, mock_stats, mock_contents, mock_project):
        """Test the complete summarization workflow"""
        # Mock project data
        project_info = {
            'id': 1,
            'filename': 'integration_test.zip',
            'created_at': datetime(2024, 1, 1, 10, 0, 0)
        }
        
        file_contents = [
            {
                'file_extension': '.py',
                'file_name': 'main.py',
                'file_path': 'main.py',
                'created_at': datetime(2024, 1, 1, 10, 0, 0)
            },
            {
                'file_extension': '.js',
                'file_name': 'app.js',
                'file_path': 'app.js',
                'created_at': datetime(2024, 1, 1, 10, 5, 0)
            },
            {
                'file_extension': '.html',
                'file_name': 'index.html',
                'file_path': 'index.html',
                'created_at': datetime(2024, 1, 1, 10, 10, 0)
            }
        ]
        
        file_stats = {
            'total_files': 3,
            'total_size_bytes': 2000,
            'text_files': 3,
            'binary_files': 0,
            'file_extensions': [
                {'extension': '.py', 'count': 1},
                {'extension': '.js', 'count': 1},
                {'extension': '.html', 'count': 1}
            ],
            'folders': [{'folder': 'root', 'file_count': 3}]
        }
        
        # Set up mocks
        mock_project.return_value = project_info
        mock_contents.return_value = file_contents
        mock_stats.return_value = file_stats
        
        # Create summarizer and generate summary
        summarizer = ProjectSummarizer()
        summary = summarizer.generate_project_summary(1)
        
        # Verify all components are present and correct
        assert summary['project_info']['filename'] == 'integration_test.zip'
        assert summary['languages']['primary_language'] == 'Python'
        assert summary['project_description']['project_type'] == 'web'
        assert summary['file_statistics']['total_files'] == 3
        
        # Test formatting
        formatted = summarizer.format_summary_for_display(summary)
        assert 'PROJECT SUMMARY: integration_test.zip' in formatted
        assert 'Primary Language: Python' in formatted


if __name__ == '__main__':
    pytest.main([__file__])
