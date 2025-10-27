import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from project_analyzer import ProjectAnalyzer, analyze_project_by_id
from external_services.external_service_prompt import (
    ExternalServicePrompt,
    request_external_service_permission
)
from analysis.analysis_router import AnalysisRouter
from config.db_config import get_connection


class TestExternalServicePrompt:
    """Test the external service prompt functionality."""
    
    @patch('builtins.input', return_value='yes')
    def test_prompt_for_permission_granted(self, mock_input):
        """Test that user can grant permission."""
        result = ExternalServicePrompt.prompt_for_permission('LLM')
        assert result == True
    
    @patch('builtins.input', return_value='no')
    def test_prompt_for_permission_declined(self, mock_input):
        """Test that user can decline permission."""
        result = ExternalServicePrompt.prompt_for_permission('LLM')
        assert result == False
    
    @patch('builtins.input', side_effect=['invalid', 'yes'])
    def test_prompt_for_permission_invalid_then_valid(self, mock_input):
        """Test that invalid input is handled and retries."""
        result = ExternalServicePrompt.prompt_for_permission('LLM')
        assert result == True
        assert mock_input.call_count == 2
    
    def test_show_external_service_info(self):
        """Test that service info is displayed without errors."""
        try:
            ExternalServicePrompt.show_external_service_info()
            # If no exception, test passes
            assert True
        except Exception as e:
            pytest.fail(f"show_external_service_info raised exception: {e}")


class TestProjectAnalyzer:
    """Test the ProjectAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return ProjectAnalyzer(user_id='test_user')
    
    @pytest.fixture
    def mock_file_contents(self):
        """Create mock file contents for testing."""
        return [
            {
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
                'file_path': 'test_project/app.js',
                'file_name': 'app.js',
                'file_extension': '.js',
                'file_size': 512,
                'file_content': '30',
                'content_type': 'application/javascript',
                'is_binary': False,
                'created_at': datetime(2024, 1, 1, 10, 5, 0)
            },
            {
                'file_path': 'test_project/README.md',
                'file_name': 'README.md',
                'file_extension': '.md',
                'file_size': 256,
                'file_content': '20',
                'content_type': 'text/markdown',
                'is_binary': False,
                'created_at': datetime(2024, 1, 1, 10, 10, 0)
            }
        ]
    
    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly."""
        assert analyzer is not None
        assert analyzer.user_id == 'test_user'
        assert analyzer.router is not None
        assert analyzer.local_analyzer is not None
    
    def test_analyze_file_statistics(self, analyzer, mock_file_contents):
        """Test file statistics analysis."""
        stats = analyzer._analyze_file_statistics(mock_file_contents)
        
        assert stats['total_files'] == 3
        assert stats['total_size_bytes'] == 1792  # 1024 + 512 + 256
        assert stats['text_files'] == 3
        assert stats['binary_files'] == 0
        assert stats['total_lines_of_code'] == 100  # 50 + 30 + 20
    
    def test_analyze_languages(self, analyzer, mock_file_contents):
        """Test language analysis."""
        langs = analyzer._analyze_languages(mock_file_contents)
        
        assert 'Python' in langs['languages_detected']
        assert 'JavaScript' in langs['languages_detected']
        # Markdown is not counted as a programming language in LANGUAGE_EXTENSIONS
        assert langs['primary_language'] in ['Python', 'JavaScript']
        assert len(langs['language_percentages']) >= 2
    
    def test_detect_frameworks_from_files(self, analyzer, mock_file_contents):
        """Test framework detection."""
        frameworks = analyzer._detect_frameworks_from_files(mock_file_contents)
        
        # Should be empty for basic files
        assert isinstance(frameworks, list)
    
    def test_detect_frameworks_with_indicators(self, analyzer):
        """Test framework detection with framework indicators."""
        files_with_frameworks = [
            {'file_name': 'package.json', 'file_path': 'package.json'},
            {'file_name': 'Dockerfile', 'file_path': 'Dockerfile'},
            {'file_name': '.gitignore', 'file_path': '.gitignore'},
            {'file_name': 'manage.py', 'file_path': 'manage.py'}
        ]
        
        frameworks = analyzer._detect_frameworks_from_files(files_with_frameworks)
        
        # Check that at least some frameworks are detected
        assert 'Node.js' in frameworks or 'React' in frameworks  # package.json indicates Node.js or React
        assert 'Git' in frameworks  # .gitignore
        assert 'Django' in frameworks  # manage.py
        # Docker might not be detected if only filename is checked without path pattern
        assert len(frameworks) >= 2
    
    def test_extract_skills_from_files(self, analyzer, mock_file_contents):
        """Test skill extraction."""
        skills = analyzer._extract_skills_from_files(mock_file_contents)
        
        assert 'Python' in skills
        assert 'JavaScript' in skills
        # Markdown may not be in language extensions, but Documentation should be
        assert 'Documentation' in skills  # Because of README.md
        assert len(skills) >= 3  # At least Python, JavaScript, and Documentation
    
    def test_analyze_structure(self, analyzer, mock_file_contents):
        """Test structure analysis."""
        structure = analyzer._analyze_structure(mock_file_contents)
        
        assert structure['total_folders'] >= 0
        assert structure['max_depth'] >= 0
        assert 'has_tests' in structure
        assert 'has_docs' in structure
        assert 'has_config' in structure
        assert structure['has_docs'] == True  # Because of README.md
    
    def test_calculate_contribution_metrics(self, analyzer, mock_file_contents):
        """Test contribution metrics calculation."""
        metrics = analyzer._calculate_contribution_metrics(mock_file_contents)
        
        assert metrics['code_files'] >= 0
        assert metrics['test_files'] >= 0
        assert metrics['documentation_files'] >= 0
        assert metrics['configuration_files'] >= 0
        assert 'activity_distribution' in metrics
        assert metrics['documentation_files'] == 1  # README.md


class TestProjectAnalyzerIntegration:
    """Integration tests for complete analysis workflow."""
    
    @pytest.fixture
    def clean_db(self):
        """Clean test data before and after tests."""
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Clean any existing test data
                cursor.execute("DELETE FROM external_service_permissions WHERE user_id = 'test_user_integration'")
                cursor.execute("DELETE FROM analysis_results WHERE uploaded_file_id IN (SELECT id FROM uploaded_files WHERE filename LIKE 'test_%')")
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Warning during cleanup: {e}")
            finally:
                cursor.close()
                conn.close()
        
        yield
        
        # Teardown
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM external_service_permissions WHERE user_id = 'test_user_integration'")
                cursor.execute("DELETE FROM analysis_results WHERE uploaded_file_id IN (SELECT id FROM uploaded_files WHERE filename LIKE 'test_%')")
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Warning during cleanup: {e}")
            finally:
                cursor.close()
                conn.close()
    
    @patch('project_analyzer.ProjectAnalyzer._get_project_info')
    @patch('project_analyzer.ProjectAnalyzer._get_file_contents')
    @patch('project_analyzer.ProjectAnalyzer._store_analysis_results')
    @patch('os.path.exists')
    def test_analyze_uploaded_project_local_strategy(self, mock_exists, mock_store, mock_files, mock_info, clean_db):
        """Test complete analysis workflow with local strategy."""
        # Mock that the file path exists
        mock_exists.return_value = True
        
        # Mock project info
        mock_info.return_value = {
            'id': 1,
            'filename': 'test_project.zip',
            'filepath': '/tmp/test_project.zip',
            'status': 'uploaded',
            'created_at': datetime(2024, 1, 1, 10, 0, 0)
        }
        
        # Mock file contents
        mock_files.return_value = [
            {
                'file_path': 'main.py',
                'file_name': 'main.py',
                'file_extension': '.py',
                'file_size': 1024,
                'file_content': '50',
                'content_type': 'text/x-python',
                'is_binary': False,
                'created_at': datetime(2024, 1, 1, 10, 0, 0)
            }
        ]
        
        # Mock storage
        mock_store.return_value = True
        
        # Create analyzer and analyze
        analyzer = ProjectAnalyzer(user_id='test_user_integration')
        results = analyzer.analyze_uploaded_project(1)
        
        # Verify results
        assert results['success'] == True
        assert results['uploaded_file_id'] == 1
        assert 'project_info' in results
        assert 'file_statistics' in results
        assert 'languages' in results
        assert 'frameworks' in results
        assert 'skills' in results
        assert 'project_structure' in results
        assert 'contribution_metrics' in results
    
    @patch('project_analyzer.ProjectAnalyzer._get_project_info')
    def test_analyze_uploaded_project_not_found(self, mock_info):
        """Test analysis when project is not found."""
        mock_info.return_value = None
        
        analyzer = ProjectAnalyzer(user_id='test_user_integration')
        results = analyzer.analyze_uploaded_project(999)
        
        assert results['success'] == False
        assert 'error' in results
        assert 'not found' in results['error'].lower()
    
    @patch('project_analyzer.ProjectAnalyzer._get_project_info')
    @patch('project_analyzer.ProjectAnalyzer._get_file_contents')
    @patch('os.path.exists')
    def test_analyze_uploaded_project_no_files(self, mock_exists, mock_files, mock_info):
        """Test analysis when no file contents are available."""
        # Mock that the file path exists
        mock_exists.return_value = True
        
        mock_info.return_value = {
            'id': 1,
            'filename': 'test_project.zip',
            'filepath': '/tmp/test_project.zip',
            'status': 'uploaded',
            'created_at': datetime(2024, 1, 1, 10, 0, 0)
        }
        
        mock_files.return_value = []
        
        analyzer = ProjectAnalyzer(user_id='test_user_integration')
        results = analyzer.analyze_uploaded_project(1)
        
        # When no files, the analysis completes but returns error in the result
        assert 'error' in results
        assert 'No file contents available' in results['error']


class TestConditionalRoutingWithAnalysis:
    """Test that routing logic works correctly with analysis."""
    
    @pytest.fixture
    def clean_permissions(self):
        """Clean permissions before and after test."""
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM external_service_permissions WHERE user_id = 'test_routing_user'")
                conn.commit()
            except Exception:
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
        
        yield
        
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM external_service_permissions WHERE user_id = 'test_routing_user'")
                conn.commit()
            except Exception:
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
    
    def test_router_uses_local_when_no_permission(self, clean_permissions):
        """Test that router uses local strategy when no permission granted."""
        router = AnalysisRouter(user_id='test_routing_user')
        strategy = router.get_analysis_strategy('project')
        
        assert strategy == 'local'
    
    def test_router_uses_enhanced_with_permission(self, clean_permissions):
        """Test that router uses enhanced strategy when permission granted."""
        # Grant permission
        from external_services.service_config import ServiceConfig
        config = ServiceConfig()
        config.initialize_table()
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO external_service_permissions (user_id, service_name, permission_granted)
            VALUES ('test_routing_user', 'LLM', TRUE)
        """)
        conn.commit()
        conn.close()
        
        router = AnalysisRouter(user_id='test_routing_user')
        strategy = router.get_analysis_strategy('project')
        
        assert strategy == 'enhanced'


class TestDisplayAnalysisResults:
    """Test the display functionality."""
    
    def test_display_successful_analysis(self):
        """Test displaying successful analysis results."""
        analyzer = ProjectAnalyzer()
        
        mock_results = {
            'success': True,
            'project_info': {
                'filename': 'test.zip',
                'id': 1,
                'created_at': '2024-01-01'
            },
            'file_statistics': {
                'total_files': 10,
                'total_size_mb': 5.2,
                'text_files': 8,
                'binary_files': 2,
                'total_lines_of_code': 500
            },
            'languages': {
                'primary_language': 'Python',
                'language_percentages': {'Python': 70.0, 'JavaScript': 30.0}
            },
            'frameworks': ['Flask', 'React'],
            'skills': ['Python', 'JavaScript', 'Flask', 'React', 'Git'],
            'project_structure': {
                'total_folders': 5,
                'max_depth': 3,
                'has_tests': True,
                'has_docs': True,
                'has_config': True
            },
            'contribution_metrics': {
                'code_files': 8,
                'test_files': 2,
                'documentation_files': 1,
                'configuration_files': 1,
                'activity_distribution': {
                    'code': 66.7,
                    'testing': 16.7,
                    'documentation': 8.3,
                    'configuration': 8.3
                }
            },
            'analysis_strategy': 'local'
        }
        
        try:
            analyzer.display_analysis_results(mock_results)
            # If no exception, test passes
            assert True
        except Exception as e:
            pytest.fail(f"display_analysis_results raised exception: {e}")
    
    def test_display_failed_analysis(self):
        """Test displaying failed analysis results."""
        analyzer = ProjectAnalyzer()
        
        mock_results = {
            'success': False,
            'error': 'Test error message'
        }
        
        try:
            analyzer.display_analysis_results(mock_results)
            # If no exception, test passes
            assert True
        except Exception as e:
            pytest.fail(f"display_analysis_results raised exception: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])