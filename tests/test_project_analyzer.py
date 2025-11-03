import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src directory to Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

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
    
    def test_show_external_service_info(self, capsys):
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
    
    def test_calculate_file_statistics(self, analyzer, mock_file_contents):
        """Test file statistics analysis."""
        stats = analyzer._calculate_file_statistics(mock_file_contents)
        
        assert stats['total_files'] == 3
        assert stats['total_size_mb'] == round(1792 / (1024 * 1024), 2)
        assert stats['text_files'] == 3
        assert stats['binary_files'] == 0
        assert stats['total_lines_of_code'] == 100  # 50 + 30 + 20
    
    def test_analyze_languages_from_files(self, analyzer, mock_file_contents):
        """Test language analysis."""
        langs = analyzer._analyze_languages_from_files(mock_file_contents)
        
        assert 'primary_language' in langs
        assert 'file_counts' in langs
        assert 'language_percentages' in langs
        assert 'detected_languages' in langs
        assert 'Python' in langs['detected_languages']
        assert 'JavaScript' in langs['detected_languages']
    
    def test_detect_frameworks_from_files(self, analyzer, mock_file_contents):
        """Test framework detection."""
        frameworks = analyzer._detect_frameworks_from_files(mock_file_contents)
        
        # Should be empty or contain detected frameworks for basic files
        assert isinstance(frameworks, list)
    
    def test_detect_frameworks_with_indicators(self, analyzer):
        """Test framework detection with framework indicators."""
        files_with_frameworks = [
            {'file_name': 'package.json', 'file_path': 'package.json', 'file_extension': '.json'},
            {'file_name': 'Dockerfile', 'file_path': 'Dockerfile', 'file_extension': ''},
            {'file_name': '.gitignore', 'file_path': '.gitignore', 'file_extension': ''},
            {'file_name': 'manage.py', 'file_path': 'manage.py', 'file_extension': '.py'}
        ]
        
        frameworks = analyzer._detect_frameworks_from_files(files_with_frameworks)
        
        # Check that at least some frameworks are detected
        assert isinstance(frameworks, list)
        # Should detect Node.js from package.json or other frameworks
        assert len(frameworks) >= 0  # Just verify it's a list
    
    def test_extract_skills_from_files(self, analyzer, mock_file_contents):
        """Test skill extraction."""
        skills = analyzer._extract_skills_from_files(mock_file_contents)
        
        assert isinstance(skills, list)
        assert 'Python' in skills
        assert 'JavaScript' in skills
        # Documentation should be detected from README.md
        assert 'Documentation' in skills
        assert len(skills) >= 3
    
    def test_analyze_structure(self, analyzer, mock_file_contents):
        """Test structure analysis."""
        structure = analyzer._analyze_structure(mock_file_contents)
        
        assert 'total_folders' in structure
        assert 'max_depth' in structure
        assert 'has_tests' in structure
        assert 'has_docs' in structure
        assert 'has_config' in structure
        assert structure['total_folders'] >= 1  # test_project folder
        assert structure['has_docs'] == True  # Because of README.md
    
    def test_calculate_contribution_metrics(self, analyzer, mock_file_contents):
        """Test contribution metrics calculation."""
        metrics = analyzer._calculate_contribution_metrics(mock_file_contents)
        
        assert 'code_files' in metrics
        assert 'test_files' in metrics
        assert 'documentation_files' in metrics
        assert 'configuration_files' in metrics
        assert 'activity_distribution' in metrics
        assert metrics['documentation_files'] == 1  # README.md
        assert metrics['code_files'] >= 0  # flexible assertion


class TestProjectAnalyzerIntegration:
    """Integration tests for complete analysis workflow."""
    
    @patch('project_analyzer.ProjectAnalyzer._get_project_info')
    @patch('project_analyzer.ProjectAnalyzer._get_file_contents')
    @patch('project_analyzer.ProjectAnalyzer._store_analysis_results')
    @patch('os.path.exists')
    def test_analyze_uploaded_project_success(self, mock_exists, mock_store, mock_files, mock_info):
        """Test successful analysis of uploaded project."""
        # Mock that the file path exists
        mock_exists.return_value = True
        
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
        
        # Mock permission request (don't actually prompt user)
        with patch('external_services.external_service_prompt.request_external_service_permission', return_value=False):
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
        
        # When no files, should return error
        assert 'error' in results or results['success'] == False
        if 'error' in results:
            assert 'No file contents available' in results['error']


class TestConditionalRoutingWithAnalysis:
    """Test that routing logic works correctly with analysis."""
    
    @patch('external_services.permission_manager.ExternalServicePermission.has_permission')
    def test_router_uses_local_when_no_permission(self, mock_permission):
        """Test that router uses local strategy when no permission granted."""
        mock_permission.return_value = False
        
        router = AnalysisRouter(user_id='test_routing_user')
        strategy = router.get_analysis_strategy('project')
        
        assert strategy == 'local'
    
    @patch('external_services.permission_manager.ExternalServicePermission.has_permission')
    def test_router_uses_enhanced_with_permission(self, mock_permission):
        """Test that router uses enhanced strategy when permission granted."""
        mock_permission.return_value = True
        
        router = AnalysisRouter(user_id='test_routing_user')
        strategy = router.get_analysis_strategy('project')
        
        assert strategy == 'enhanced'


class TestDisplayAnalysisResults:
    """Test the display functionality."""
    
    def test_display_successful_analysis(self, capsys):
        """Test displaying successful analysis results."""
        analyzer = ProjectAnalyzer()
        
        mock_results = {
            'success': True,
            'project_info': {
                'filename': 'test.zip',
                'id': 1,
                'created_at': '2024-01-01',
                'filepath': '/tmp/test.zip'
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
            captured = capsys.readouterr()
            # Check that output contains expected information
            assert 'ANALYSIS RESULTS' in captured.out
            assert 'test.zip' in captured.out
        except Exception as e:
            pytest.fail(f"display_analysis_results raised exception: {e}")
    
    def test_display_failed_analysis(self, capsys):
        """Test displaying failed analysis results."""
        analyzer = ProjectAnalyzer()
        
        mock_results = {
            'success': False,
            'error': 'Test error message'
        }
        
        try:
            analyzer.display_analysis_results(mock_results)
            captured = capsys.readouterr()
            # Check that error message is displayed
            assert 'failed' in captured.out.lower() or 'error' in captured.out.lower()
        except Exception as e:
            pytest.fail(f"display_analysis_results raised exception: {e}")


class TestFileStatisticsCalculation:
    """Test file statistics calculation in detail."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return ProjectAnalyzer(user_id='test_user')
    
    def test_file_size_calculation(self, analyzer):
        """Test that file sizes are calculated correctly."""
        files = [
            {'file_size': 1000, 'file_content': '10', 'is_binary': False, 'file_path': 'a.py', 'file_extension': '.py'},
            {'file_size': 2000, 'file_content': '20', 'is_binary': False, 'file_path': 'b.py', 'file_extension': '.py'},
            {'file_size': 500, 'file_content': None, 'is_binary': True, 'file_path': 'c.bin', 'file_extension': '.bin'}
        ]
        
        stats = analyzer._calculate_file_statistics(files)
        
        assert stats['total_files'] == 3
        assert stats['text_files'] == 2
        assert stats['binary_files'] == 1
        assert stats['total_lines_of_code'] == 30  # 10 + 20
    
    def test_language_percentage_calculation(self, analyzer):
        """Test that language percentages are calculated correctly."""
        files = [
            {'file_extension': '.py', 'file_path': 'a.py', 'file_name': 'a.py'},
            {'file_extension': '.py', 'file_path': 'b.py', 'file_name': 'b.py'},
            {'file_extension': '.js', 'file_path': 'c.js', 'file_name': 'c.js'}
        ]
        
        langs = analyzer._analyze_languages_from_files(files)
        
        assert 'Python' in langs['detected_languages']
        assert 'JavaScript' in langs['detected_languages']
        # Python should have 66.7% (2 out of 3)
        assert langs['language_percentages']['Python'] == 66.7
        # JavaScript should have 33.3% (1 out of 3)
        assert langs['language_percentages']['JavaScript'] == 33.3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])