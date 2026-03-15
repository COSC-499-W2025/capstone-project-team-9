"""
Tests for ResumeManager functionality.
Tests resume table initialization, storage, retrieval, deletion, and generation.
"""
import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from resume.resume_manager import ResumeManager


class TestResumeTableInitialization:
    """Test database table creation."""
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_init_resume_table_success(self, mock_with_db_cursor):
        """Test successful initialization of resume table."""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = ResumeManager.init_resume_table()
        
        assert result == True
        # 4 execute calls: CREATE TABLE, migration check, CREATE INDEX, and FK constraint
        assert mock_cursor.execute.call_count == 4
        assert mock_with_db_cursor.called
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_init_resume_table_failure(self, mock_with_db_cursor):
        """Test handling of table initialization failure."""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = ResumeManager.init_resume_table()
        
        assert result == False


class TestUserResumeStorage:
    """Test user resume storage and retrieval."""
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_store_user_resume_success(self, mock_with_db_cursor):
        """Test successful storage of user resume."""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        user_id = "test_user"
        resume_data = {
            'total_projects_analyzed': 10,
            'top_projects_displayed': 5,
            'all_skills': ['Python', 'JavaScript'],
            'summary_stats': {
                'total_lines_of_code': 5000,
                'total_files': 50,
                'unique_languages': 3,
                'unique_frameworks': 2
            }
        }
        
        result = ResumeManager.store_user_resume(user_id, resume_data)
        
        assert result == True
        mock_cursor.execute.assert_called_once()
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_store_user_resume_failure(self, mock_with_db_cursor):
        """Test handling of storage failure."""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = ResumeManager.store_user_resume("test_user", {})
        
        assert result == False
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_get_user_resume_success(self, mock_with_db_cursor):
        """Test successful retrieval of user resume."""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        resume_data_json = '{"total_projects_analyzed": 10, "all_skills": ["Python"]}'
        resume_data_dict = {"total_projects_analyzed": 10, "all_skills": ["Python"]}
        created_at = datetime(2024, 1, 1, 10, 0, 0)
        updated_at = datetime(2024, 1, 1, 11, 0, 0)
        # Mock can return either string or dict depending on PostgreSQL driver
        mock_cursor.fetchone.return_value = (resume_data_dict, created_at, updated_at)
        
        result = ResumeManager.get_user_resume("test_user")
        
        assert result is not None
        # Resume data is now parsed from JSON to dict
        assert result['resume_data'] == resume_data_dict
        assert result['created_at'] == created_at
        assert result['updated_at'] == updated_at
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_get_user_resume_not_found(self, mock_with_db_cursor):
        """Test retrieval when user resume does not exist."""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        mock_cursor.fetchone.return_value = None
        
        result = ResumeManager.get_user_resume("nonexistent_user")
        
        assert result is None
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_get_user_resume_failure(self, mock_with_db_cursor):
        """Test handling of retrieval failure."""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = ResumeManager.get_user_resume("test_user")
        
        assert result is None


class TestResumeExistenceCheck:
    """Test resume existence checking."""
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_resume_exists_true(self, mock_with_db_cursor):
        """Test checking when resume exists."""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        mock_cursor.fetchone.return_value = (1,)
        
        result = ResumeManager.resume_exists("test_user")
        
        assert result == True
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_resume_exists_false(self, mock_with_db_cursor):
        """Test checking when resume does not exist."""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        mock_cursor.fetchone.return_value = None
        
        result = ResumeManager.resume_exists("nonexistent_user")
        
        assert result == False
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_resume_exists_failure(self, mock_with_db_cursor):
        """Test handling of existence check failure."""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = ResumeManager.resume_exists("test_user")
        
        assert result == False


class TestResumeOperations:
    """Test resume helper operations."""
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_delete_user_resume_success(self, mock_with_db_cursor):
        """Test successful deletion of user resume."""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = ResumeManager.delete_user_resume("test_user")
        
        assert result == True
        mock_cursor.execute.assert_called_once()
    
    @patch('resume.resume_manager.with_db_cursor')
    def test_delete_user_resume_failure(self, mock_with_db_cursor):
        """Test handling of deletion failure."""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = ResumeManager.delete_user_resume("test_user")
        
        assert result == False


class TestResumeGeneration:
    """Test resume generation from projects."""
    
    @patch('resume.resume_manager.get_stored_ranking_by_project_id')
    @patch('resume.resume_manager.summarize_project')
    @patch('resume.resume_manager.get_user_git_username')
    @patch('resume.resume_manager._extract_common_names_from_filenames')
    @patch('resume.resume_manager._identify_authors_from_zip')
    @patch('builtins.input')
    @patch('resume.resume_manager.get_file_contents_by_upload_id')
    @patch('resume.resume_manager.analyze_project_from_db')
    @patch('resume.resume_manager.SkillMapper')
    @patch('resume.resume_manager.ProjectSummarizer')
    @patch('resume.resume_manager.rank_all_projects')
    def test_generate_user_resume_success(self, mock_rank, mock_summarizer_class, 
                                          mock_skill_mapper_class, mock_analyze, mock_get_files,
                                          mock_input, mock_identify_authors, mock_extract_names,
                                          mock_git_username, mock_summarize, mock_stored_ranking):
        """Test successful generation of user resume with enriched data."""
        # Setup mocks for author selection
        mock_identify_authors.return_value = {'Alice', 'Bob'}
        mock_extract_names.return_value = set()
        mock_git_username.return_value = None
        mock_input.side_effect = ['1']  # Select first author (Alice)
        mock_stored_ranking.return_value = {'summary': 'Project summary text'}
        mock_summarize.return_value = 'Project summary text'
        
        # Setup mocks
        mock_summarizer = Mock()
        mock_summarizer_class.return_value = mock_summarizer
        
        mock_skill_mapper = Mock()
        mock_skill_mapper_class.return_value = mock_skill_mapper
        mock_skill_mapper.extract_skills_from_deep_analysis.return_value = ['OOP', 'Testing']
        mock_skill_mapper.categorize_skills.return_value = {
            'Languages': ['Python', 'JavaScript'],
            'Concepts': ['OOP', 'Testing']
        }
        
        mock_rank.return_value = [
            {'project_id': 1, 'filename': 'project1.zip', 'score': 100},
            {'project_id': 2, 'filename': 'project2.zip', 'score': 85}
        ]
        
        mock_summarizer.generate_project_summary.return_value = {
            'languages': {
                'primary_language': 'Python',
                'languages': ['Python', 'JavaScript']
            },
            'time_analysis': {
                'duration_days': 30,
                'intensity': 'High',
                'first_file': '2024-01-01',
                'last_file': '2024-01-31'
            },
            'collaboration_analysis': {
                'collaboration_level': 'Team'
            },
            'code_analysis': {
                'code_quality_summary': {'average_quality_score': 85.5},
                'oop_principles_summary': {
                    'abstraction': {'count': 5},
                    'encapsulation': {'count': 3},
                    'polymorphism': {'count': 2},
                    'inheritance': {'count': 1}
                },
                'optimization_summary': ['caching', 'lazy_loading']
            },
            'project_info': {
                'filename': 'project1.zip',
                'created_at': '2024-01-01'
            }
        }
        
        mock_analyze.return_value = {
            'totals': {'files': 25, 'lines': 2500}
        }
        
        mock_get_files.return_value = [
            {'file_name': 'app.py', 'file_path': 'src/app.py'},
            {'file_name': 'test_app.py', 'file_path': 'tests/test_app.py'},
            {'file_name': 'README.md', 'file_path': 'README.md'},
            {'file_name': 'package.json', 'file_path': 'package.json'}
        ]
        
        result = ResumeManager.generate_user_resume("test_user", top_projects_count=2)
        
        # Verify result structure
        assert result is not None
        assert result['user_name'] == 'test_user'
        assert result['display_name'] == 'Alice'  # Selected author name
        assert result['total_projects_analyzed'] == 2
        assert result['top_projects_displayed'] == 2
        
        # Verify enriched data fields (summary_stats removed in new version)
        assert 'categorized_skills' in result
        assert 'languages' in result
        assert 'frameworks' in result
        assert 'all_skills' in result
        assert 'top_projects' in result
        assert 'generated_at' in result
        
        # Verify project data structure
        if result['top_projects']:
            project = result['top_projects'][0]
            assert 'project_name' in project
            assert 'primary_language' in project
            assert 'languages' in project
            assert 'frameworks' in project
            assert 'duration_days' in project
            assert 'intensity' in project
            assert 'collaboration_level' in project
            assert 'summary' in project  # Project summary from database
    
    @patch('resume.resume_manager._extract_common_names_from_filenames')
    @patch('resume.resume_manager._identify_authors_from_zip')
    @patch('builtins.input')
    @patch('resume.resume_manager.rank_all_projects')
    def test_generate_user_resume_no_projects(self, mock_rank, mock_input, mock_identify_authors, mock_extract_names):
        """Test resume generation when no projects exist."""
        mock_rank.return_value = []
        # No authors to mock since no projects
        
        result = ResumeManager.generate_user_resume("test_user")
        
        assert result is None
    
    @patch('resume.resume_manager._extract_common_names_from_filenames')
    @patch('resume.resume_manager._identify_authors_from_zip')
    @patch('builtins.input')
    @patch('resume.resume_manager.rank_all_projects')
    def test_generate_user_resume_failure(self, mock_rank, mock_input, mock_identify_authors, mock_extract_names):
        """Test handling of generation failure."""
        mock_rank.side_effect = Exception("Database error")
        # No authors to mock since exception happens before author detection
        
        result = ResumeManager.generate_user_resume("test_user")
        
        assert result is None


class TestFrameworkDetection:
    """Test framework detection from file contents."""
    
    def test_detect_frameworks_react(self):
        """Test React framework detection."""
        file_contents = [
            {'file_name': 'package.json'},
            {'file_name': 'App.jsx'},
            {'file_name': 'index.tsx'}
        ]
        
        result = ResumeManager._detect_frameworks_from_files(file_contents)
        
        assert 'React' in result
        assert 'Node.js' in result
    
    def test_detect_frameworks_django(self):
        """Test Django framework detection."""
        file_contents = [
            {'file_name': 'manage.py'},
            {'file_name': 'settings.py'}
        ]
        
        result = ResumeManager._detect_frameworks_from_files(file_contents)
        
        assert 'Django' in result
    
    def test_detect_frameworks_docker(self):
        """Test Docker detection."""
        file_contents = [
            {'file_name': 'Dockerfile'},
            {'file_name': 'docker-compose.yml'}
        ]
        
        result = ResumeManager._detect_frameworks_from_files(file_contents)
        
        assert 'Docker' in result
    
    def test_detect_frameworks_none(self):
        """Test when no frameworks detected."""
        file_contents = [
            {'file_name': 'main.py'},
            {'file_name': 'utils.py'}
        ]
        
        result = ResumeManager._detect_frameworks_from_files(file_contents)
        
        assert result == []
    
    def test_detect_frameworks_empty_input(self):
        """Test with empty file list."""
        result = ResumeManager._detect_frameworks_from_files([])
        
        assert result == []
    
    def test_detect_frameworks_multiple(self):
        """Test detecting multiple frameworks."""
        file_contents = [
            {'file_name': 'package.json'},
            {'file_name': 'Dockerfile'},
            {'file_name': 'angular.json'},
            {'file_name': 'pom.xml'}
        ]
        
        result = ResumeManager._detect_frameworks_from_files(file_contents)
        
        assert 'Node.js' in result
        assert 'Docker' in result
        assert 'Angular' in result
        assert 'Spring' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])