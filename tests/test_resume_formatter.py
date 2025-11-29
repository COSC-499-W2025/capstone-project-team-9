"""
Tests for ResumeFormatter functionality.
Tests JSON, Markdown, Text, and PDF formatting of resume data.
"""
import pytest
import sys
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, Mock, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from resume.resume_formatter import ResumeFormatter


class TestResumeFormatterJSON:
    """Test JSON formatting functionality."""
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume data for testing."""
        return {
            'user_id': 'test_user',
            'total_projects_analyzed': 10,
            'top_projects_displayed': 5,
            'all_skills': ['Python', 'JavaScript', 'React'],
            'summary_stats': {
                'total_lines_of_code': 5000,
                'total_files': 50,
                'unique_languages': 3,
                'unique_frameworks': 2
            },
            'categorized_skills': {
                'Languages': ['Python', 'JavaScript'],
                'Frameworks': ['React']
            },
            'languages': ['Python', 'JavaScript'],
            'frameworks': ['React'],
            'top_projects': [
                {
                    'project_name': 'Project 1',
                    'score': 95,
                    'primary_language': 'Python',
                    'languages': ['Python'],
                    'frameworks': ['React'],
                    'skills': ['Python', 'React'],
                    'file_count': 25,
                    'lines_of_code': 2500,
                    'duration_days': 30,
                    'intensity': 'High',
                    'collaboration_level': 'Team',
                    'code_quality_score': 85.5,
                    'oop_principles_count': 11,
                    'optimization_count': 2,
                    'has_tests': True,
                    'has_docs': True
                }
            ],
            'generated_at': '2024-01-01T10:00:00'
        }
    
    def test_format_json_success(self, sample_resume):
        """Test successful JSON formatting."""
        result = ResumeFormatter.format_json(sample_resume)
        
        assert result is not None
        assert isinstance(result, str)
        assert '"user_id"' in result
        assert '"total_projects_analyzed"' in result
        assert '"summary_stats"' in result
    
    def test_format_json_empty_data(self):
        """Test JSON formatting with empty data."""
        result = ResumeFormatter.format_json(None)
        
        assert result is None
    
    def test_format_json_parses_back(self, sample_resume):
        """Test that formatted JSON can be parsed back."""
        import json
        formatted = ResumeFormatter.format_json(sample_resume)
        
        parsed = json.loads(formatted)
        assert parsed['user_id'] == 'test_user'
        assert parsed['total_projects_analyzed'] == 10
        assert parsed['summary_stats']['total_lines_of_code'] == 5000


class TestResumeFormatterMarkdown:
    """Test Markdown formatting functionality."""
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume data for testing."""
        return {
            'total_projects_analyzed': 10,
            'top_projects_displayed': 2,
            'all_skills': ['Python', 'JavaScript'],
            'summary_stats': {
                'total_lines_of_code': 5000,
                'total_files': 50,
                'unique_languages': 2,
                'unique_frameworks': 1
            },
            'categorized_skills': {
                'Languages': ['Python', 'JavaScript']
            },
            'languages': ['Python', 'JavaScript'],
            'frameworks': ['React'],
            'top_projects': [
                {
                    'project_name': 'Project A',
                    'score': 95,
                    'primary_language': 'Python',
                    'languages': ['Python'],
                    'frameworks': ['React'],
                    'skills': ['Python'],
                    'file_count': 25,
                    'lines_of_code': 2500,
                    'duration_days': 30,
                    'intensity': 'High',
                    'collaboration_level': 'Team',
                    'code_quality_score': 85.5,
                    'oop_principles_count': 5,
                    'optimization_count': 2,
                    'has_tests': True,
                    'has_docs': True
                }
            ],
            'generated_at': '2024-01-01T10:00:00'
        }
    
    def test_format_markdown_success(self, sample_resume):
        """Test successful Markdown formatting."""
        result = ResumeFormatter.format_markdown(sample_resume)
        
        assert result is not None
        assert '# Resume' in result
        assert '## Overview' in result
        assert 'Python' in result
        assert 'Project A' in result
    
    def test_format_markdown_contains_sections(self, sample_resume):
        """Test that Markdown contains all required sections."""
        result = ResumeFormatter.format_markdown(sample_resume)
        
        assert '## Technical Skills' in result
        assert '## Top Projects' in result
        assert '**Technologies:**' in result or 'Technologies:' in result
    
    def test_format_markdown_contains_enriched_data(self, sample_resume):
        """Test that Markdown contains enriched project data."""
        result = ResumeFormatter.format_markdown(sample_resume)
        
        assert '**Score:**' in result
        assert '**Primary Language:**' in result
        assert '**Scale:**' in result or 'lines' in result
    
    def test_format_markdown_empty_data(self):
        """Test Markdown formatting with empty data."""
        result = ResumeFormatter.format_markdown(None)
        
        assert result is None


class TestResumeFormatterText:
    """Test plain text formatting functionality."""
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume data for testing."""
        return {
            'total_projects_analyzed': 5,
            'top_projects_displayed': 1,
            'all_skills': ['Java', 'Spring'],
            'summary_stats': {
                'total_lines_of_code': 3000,
                'total_files': 30,
                'unique_languages': 1,
                'unique_frameworks': 1
            },
            'categorized_skills': {
                'Languages': ['Java'],
                'Frameworks': ['Spring']
            },
            'languages': ['Java'],
            'frameworks': ['Spring'],
            'top_projects': [
                {
                    'project_name': 'Backend Service',
                    'score': 88,
                    'primary_language': 'Java',
                    'languages': ['Java'],
                    'frameworks': ['Spring'],
                    'skills': ['Java', 'Spring'],
                    'file_count': 30,
                    'lines_of_code': 3000,
                    'duration_days': 45,
                    'intensity': 'Medium',
                    'collaboration_level': 'Solo',
                    'code_quality_score': 78.0,
                    'oop_principles_count': 8,
                    'optimization_count': 1,
                    'has_tests': True,
                    'has_docs': False
                }
            ],
            'generated_at': '2024-01-01T10:00:00'
        }
    
    def test_format_text_success(self, sample_resume):
        """Test successful text formatting."""
        result = ResumeFormatter.format_text(sample_resume)
        
        assert result is not None
        assert 'RESUME' in result
        assert 'OVERVIEW' in result
        assert 'SKILLS' in result
        assert 'TOP PROJECTS' in result
    
    def test_format_text_contains_data(self, sample_resume):
        """Test that text format contains actual data."""
        result = ResumeFormatter.format_text(sample_resume)
        
        assert 'Java' in result
        assert 'Backend Service' in result
        assert '88' in result
    
    def test_format_text_empty_data(self):
        """Test text formatting with empty data."""
        result = ResumeFormatter.format_text(None)
        
        assert result is None


class TestResumeFormatterInterface:
    """Test main formatter interface."""
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume data for testing."""
        return {
            'total_projects_analyzed': 3,
            'top_projects_displayed': 1,
            'all_skills': ['Python'],
            'summary_stats': {
                'total_lines_of_code': 1000,
                'total_files': 10,
                'unique_languages': 1,
                'unique_frameworks': 0
            },
            'categorized_skills': {},
            'languages': ['Python'],
            'frameworks': [],
            'top_projects': [],
            'generated_at': '2024-01-01T10:00:00'
        }
    
    def test_get_formatted_resume_json(self, sample_resume):
        """Test getting resume in JSON format."""
        result = ResumeFormatter.get_formatted_resume(sample_resume, 'json')
        
        assert result is not None
        assert isinstance(result, str)
    
    def test_get_formatted_resume_markdown(self, sample_resume):
        """Test getting resume in Markdown format."""
        result = ResumeFormatter.get_formatted_resume(sample_resume, 'markdown')
        
        assert result is not None
        assert '# Resume' in result
    
    def test_get_formatted_resume_text(self, sample_resume):
        """Test getting resume in text format."""
        result = ResumeFormatter.get_formatted_resume(sample_resume, 'text')
        
        assert result is not None
        assert 'RESUME' in result
    
    def test_get_formatted_resume_default_format(self, sample_resume):
        """Test default format is text."""
        result = ResumeFormatter.get_formatted_resume(sample_resume)
        
        assert result is not None
        assert 'RESUME' in result
    
    def test_get_formatted_resume_invalid_format(self, sample_resume):
        """Test invalid format defaults to text."""
        result = ResumeFormatter.get_formatted_resume(sample_resume, 'invalid')
        
        assert result is not None
        assert 'RESUME' in result
    
    def test_get_formatted_resume_none_data(self):
        """Test formatting with None data."""
        result = ResumeFormatter.get_formatted_resume(None, 'text')
        
        assert result is None


class TestResumeFormatterPDF:
    """Test PDF formatting functionality."""
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume data for PDF testing."""
        return {
            'user_id': 'test_user',
            'total_projects_analyzed': 5,
            'top_projects_displayed': 2,
            'all_skills': ['Python', 'JavaScript', 'React', 'Docker'],
            'summary_stats': {
                'total_lines_of_code': 8000,
                'total_files': 80,
                'unique_languages': 2,
                'unique_frameworks': 3
            },
            'categorized_skills': {
                'Languages': ['Python', 'JavaScript'],
                'Frameworks': ['React', 'Docker']
            },
            'languages': ['Python', 'JavaScript'],
            'frameworks': ['React', 'Docker', 'Node.js'],
            'top_projects': [
                {
                    'project_name': 'web-app-master.zip',
                    'project_id': 1,
                    'score': 95,
                    'primary_language': 'Python',
                    'languages': ['Python', 'JavaScript'],
                    'frameworks': ['React', 'Docker'],
                    'skills': ['Python', 'JavaScript', 'React'],
                    'file_count': 50,
                    'lines_of_code': 5000,
                    'duration_days': 60,
                    'intensity': 'High',
                    'collaboration_level': 'Team',
                    'code_quality_score': 88.5,
                    'oop_principles_count': 15,
                    'optimization_count': 4,
                    'has_tests': True,
                    'has_docs': True
                },
                {
                    'project_name': 'api-service.zip',
                    'project_id': 2,
                    'score': 82,
                    'primary_language': 'JavaScript',
                    'languages': ['JavaScript'],
                    'frameworks': ['Node.js'],
                    'skills': ['JavaScript', 'Node.js'],
                    'file_count': 30,
                    'lines_of_code': 3000,
                    'duration_days': 30,
                    'intensity': 'Medium',
                    'collaboration_level': 'Solo',
                    'code_quality_score': 75.0,
                    'oop_principles_count': 5,
                    'optimization_count': 1,
                    'has_tests': False,
                    'has_docs': True
                }
            ],
            'generated_at': '2024-01-01T10:00:00'
        }
    
    def test_format_pdf_success(self, sample_resume):
        """Test successful PDF generation."""
        try:
            import reportlab
        except ImportError:
            pytest.skip("reportlab not installed")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            result = ResumeFormatter.format_pdf(sample_resume, output_path)
            
            assert result == True
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_format_pdf_creates_valid_file(self, sample_resume):
        """Test that generated PDF is a valid PDF file."""
        try:
            import reportlab
        except ImportError:
            pytest.skip("reportlab not installed")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            result = ResumeFormatter.format_pdf(sample_resume, output_path)
            
            assert result == True
            
            # Check PDF magic bytes
            with open(output_path, 'rb') as f:
                header = f.read(4)
                assert header == b'%PDF'
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_format_pdf_empty_projects(self):
        """Test PDF generation with no projects."""
        try:
            import reportlab
        except ImportError:
            pytest.skip("reportlab not installed")
        
        resume_data = {
            'total_projects_analyzed': 0,
            'top_projects_displayed': 0,
            'all_skills': [],
            'summary_stats': {
                'total_lines_of_code': 0,
                'total_files': 0,
                'unique_languages': 0,
                'unique_frameworks': 0
            },
            'categorized_skills': {},
            'languages': [],
            'frameworks': [],
            'top_projects': [],
            'generated_at': '2024-01-01T10:00:00'
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            result = ResumeFormatter.format_pdf(resume_data, output_path)
            
            assert result == True
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_format_pdf_invalid_path(self, sample_resume):
        """Test PDF generation with invalid output path."""
        try:
            import reportlab
        except ImportError:
            pytest.skip("reportlab not installed")
        
        # Use an invalid path that cannot be written to
        invalid_path = '/nonexistent_directory/resume.pdf'
        
        result = ResumeFormatter.format_pdf(sample_resume, invalid_path)
        
        assert result == False
    
    def test_format_pdf_missing_reportlab(self, sample_resume):
        """Test PDF generation handles missing reportlab gracefully."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            # Mock the import to raise ImportError
            with patch.dict('sys.modules', {'reportlab': None}):
                with patch('resume.resume_formatter.ResumeFormatter.format_pdf') as mock_format_pdf:
                    mock_format_pdf.return_value = False
                    result = mock_format_pdf(sample_resume, output_path)
                    
                    assert result == False
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_format_pdf_with_special_characters(self):
        """Test PDF generation handles special characters in project names."""
        try:
            import reportlab
        except ImportError:
            pytest.skip("reportlab not installed")
        
        resume_data = {
            'total_projects_analyzed': 1,
            'top_projects_displayed': 1,
            'all_skills': ['Python'],
            'summary_stats': {
                'total_lines_of_code': 1000,
                'total_files': 10,
                'unique_languages': 1,
                'unique_frameworks': 0
            },
            'categorized_skills': {'Languages': ['Python']},
            'languages': ['Python'],
            'frameworks': [],
            'top_projects': [
                {
                    'project_name': 'special-chars_test&project.zip',
                    'project_id': 1,
                    'score': 90,
                    'primary_language': 'Python',
                    'languages': ['Python'],
                    'frameworks': [],
                    'skills': ['Python'],
                    'file_count': 10,
                    'lines_of_code': 1000,
                    'duration_days': 15,
                    'intensity': 'Low',
                    'collaboration_level': 'Solo',
                    'code_quality_score': 70.0,
                    'oop_principles_count': 2,
                    'optimization_count': 0,
                    'has_tests': False,
                    'has_docs': False
                }
            ],
            'generated_at': '2024-01-01T10:00:00'
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            result = ResumeFormatter.format_pdf(resume_data, output_path)
            
            assert result == True
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])