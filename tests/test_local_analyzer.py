"""
Unit tests for local analysis methods.
Tests Issue #39: Set up internal analysis method.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from analysis.local_analyzer import LocalAnalyzer


class TestLocalAnalyzer:
    """Test cases for LocalAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return LocalAnalyzer()
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project structure for testing."""
        temp_dir = tempfile.mkdtemp()
        
        # Create project structure
        os.makedirs(os.path.join(temp_dir, 'src'))
        os.makedirs(os.path.join(temp_dir, 'tests'))
        os.makedirs(os.path.join(temp_dir, 'docs'))
        
        # Create Python files
        with open(os.path.join(temp_dir, 'src', 'main.py'), 'w') as f:
            f.write('# Main file\nfrom flask import Flask\n\ndef main():\n    pass\n')
        
        with open(os.path.join(temp_dir, 'src', 'utils.py'), 'w') as f:
            f.write('# Utils file\n\ndef helper():\n    return True\n')
        
        # Create test file
        with open(os.path.join(temp_dir, 'tests', 'test_main.py'), 'w') as f:
            f.write('# Test file\nimport pytest\n\ndef test_main():\n    assert True\n')
        
        # Create JavaScript file
        with open(os.path.join(temp_dir, 'src', 'app.js'), 'w') as f:
            f.write('// JavaScript file\nimport React from "react";\n\nfunction App() {}\n')
        
        # Create documentation
        with open(os.path.join(temp_dir, 'README.md'), 'w') as f:
            f.write('# Test Project\n\nThis is a test project.\n')
        
        with open(os.path.join(temp_dir, 'docs', 'guide.md'), 'w') as f:
            f.write('# Guide\n\nDocumentation here.\n')
        
        # Create config files
        with open(os.path.join(temp_dir, 'package.json'), 'w') as f:
            f.write('{"name": "test-project"}')
        
        with open(os.path.join(temp_dir, '.gitignore'), 'w') as f:
            f.write('node_modules/\n__pycache__/\n')
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly."""
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_project')
        assert hasattr(analyzer, 'analysis_cache')
    
    def test_analyze_structure(self, analyzer, temp_project):
        """Test structural analysis."""
        structure = analyzer.analyze_structure(temp_project)
        
        assert 'total_files' in structure
        assert 'total_directories' in structure
        assert 'max_depth' in structure
        assert structure['total_files'] > 0
        assert structure['total_directories'] > 0
        assert structure['has_tests'] == True
        assert structure['has_docs'] == True
    
    def test_detect_languages(self, analyzer, temp_project):
        """Test language detection."""
        languages = analyzer.detect_languages(temp_project)
        
        assert 'languages_detected' in languages
        assert 'Python' in languages['languages_detected']
        assert 'JavaScript' in languages['languages_detected']
        assert 'JSON' in languages['languages_detected']
        assert 'primary_language' in languages
        assert languages['primary_language'] is not None
    
    def test_detect_frameworks(self, analyzer, temp_project):
        """Test framework detection."""
        frameworks = analyzer.detect_frameworks(temp_project)
        
        assert isinstance(frameworks, list)
        assert 'Flask' in frameworks
        assert 'React' in frameworks
        assert 'Node.js' in frameworks
    
    def test_calculate_metrics(self, analyzer, temp_project):
        """Test metrics calculation."""
        metrics = analyzer.calculate_metrics(temp_project)
        
        assert 'total_lines_of_code' in metrics
        assert 'total_file_size_bytes' in metrics
        assert 'code_files' in metrics
        assert 'document_files' in metrics
        assert metrics['total_lines_of_code'] > 0
        assert metrics['code_files'] > 0
        assert metrics['document_files'] > 0
    
    def test_extract_skills(self, analyzer, temp_project):
        """Test skill extraction."""
        skills = analyzer.extract_skills(temp_project)
        
        assert isinstance(skills, list)
        assert 'Python' in skills
        assert 'JavaScript' in skills
        assert 'Flask' in skills
        assert 'React' in skills
        assert 'Git' in skills
        assert 'Documentation' in skills
        assert 'Unit Testing' in skills
    
    def test_get_file_breakdown(self, analyzer, temp_project):
        """Test file breakdown analysis."""
        breakdown = analyzer.get_file_breakdown(temp_project)
        
        assert 'by_extension' in breakdown
        assert 'by_category' in breakdown
        assert '.py' in breakdown['by_extension']
        assert '.js' in breakdown['by_extension']
        assert '.md' in breakdown['by_extension']
        assert breakdown['by_category']['code'] > 0
        assert breakdown['by_category']['documents'] > 0
    
    def test_analyze_project_complete(self, analyzer, temp_project):
        """Test complete project analysis."""
        result = analyzer.analyze_project(temp_project)
    
        assert 'project_path' in result
        assert 'project_name' in result
        assert 'analyzed_at' in result
        assert 'structure' in result
        assert 'languages' in result
        assert 'frameworks' in result
        assert 'metrics' in result
        assert 'skills' in result
        assert 'file_breakdown' in result
    
    # Verify nested data
        assert result['structure']['has_tests'] == True
        assert 'Python' in result['languages']['languages_detected']
        assert 'Flask' in result['frameworks']
        assert result['metrics']['code_files'] > 0
        assert result['metrics']['document_files'] > 0
        assert len(result['skills']) > 0
    
    def test_analyze_nonexistent_path(self, analyzer):
        """Test analysis of nonexistent path raises error."""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_project('/nonexistent/path')
    
    def test_language_detection_empty_project(self, analyzer):
        """Test language detection on empty project."""
        temp_dir = tempfile.mkdtemp()
        
        languages = analyzer.detect_languages(temp_dir)
        
        assert languages['languages_detected'] == []
        assert languages['primary_language'] is None
        
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])