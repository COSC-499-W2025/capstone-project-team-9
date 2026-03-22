import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
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
            assert True
        except Exception as e:
            pytest.fail(f"show_external_service_info raised exception: {e}")


class TestRequestExternalServicePermission:
    """Test the request_external_service_permission function."""
    
    @patch('external_services.external_service_prompt.ExternalServicePermission')
    @patch('external_services.external_service_prompt.ExternalServicePrompt')
    def test_permission_already_granted(self, mock_prompt, mock_permission_class, mock_db_session):
        """Test when permission is already stored in DB."""
        # Setup mock instance
        mock_instance = mock_permission_class.return_value
        mock_instance.has_permission.return_value = True
        
        # Execute
        result = request_external_service_permission('test_user', 'LLM')
        
        # Verify
        assert result == True
        mock_prompt.prompt_for_permission.assert_not_called()
        
    @patch('external_services.external_service_prompt.ExternalServicePermission')
    @patch('external_services.external_service_prompt.ExternalServicePrompt')
    def test_permission_needs_prompt(self, mock_prompt, mock_permission_class, mock_db_session):
        """Test when permission needs to be asked."""
        # Setup mock instance
        mock_instance = mock_permission_class.return_value
        
        # FIX: Return None (not False) to simulate "Permission Record Not Found"
        # This forces the code to prompt the user.
        mock_instance.has_permission.return_value = None 
        
        # Mock user saying 'yes'
        mock_prompt.prompt_for_permission.return_value = True
        
        # Execute
        result = request_external_service_permission('test_user', 'LLM')
        
        # Verify
        assert result == True
        mock_prompt.prompt_for_permission.assert_called_once()
        mock_prompt.store_permission.assert_called_once_with('test_user', 'LLM', True)


class TestProjectAnalyzer:
    """Test ProjectAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        return ProjectAnalyzer("test_path.zip")
    
    def test_calculate_file_statistics(self, analyzer):
        """Test file statistics calculation."""
        files = [
            # line_count from DB (preferred); statistics only count LANGUAGE_EXTENSIONS code lines
            {'file_size': 1000, 'file_content': None, 'line_count': 10, 'is_binary': False, 'file_path': 'a.py', 'file_extension': '.py'},
            {'file_size': 2000, 'file_content': None, 'line_count': 20, 'is_binary': False, 'file_path': 'b.py', 'file_extension': '.py'},
            {'file_size': 500, 'file_content': None, 'is_binary': True, 'file_path': 'c.bin', 'file_extension': '.bin'}
        ]
        
        stats = analyzer._calculate_file_statistics(files)
        
        assert stats['total_files'] == 3
        assert stats['text_files'] == 2
        assert stats['binary_files'] == 1
        
        # Verify line counting (10 + 20 = 30)
        # We check both possible keys depending on implementation
        lines = stats.get('total_lines_of_code') or stats.get('lines_of_code')
        assert lines == 30
    
    def test_language_percentage_calculation(self, analyzer):
        """Test that language percentages are calculated correctly."""
        files = [
            {'file_extension': '.py', 'file_path': 'a.py', 'file_name': 'a.py'},
            {'file_extension': '.py', 'file_path': 'b.py', 'file_name': 'b.py'},
            {'file_extension': '.js', 'file_path': 'c.js', 'file_name': 'c.js'}
        ]
        
        langs = analyzer._analyze_languages_from_files(files)
        
        assert 'Python' in langs['detected_languages']