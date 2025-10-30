"""
Tests for project ranking functionality
"""
import sys
import os
import pytest

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from analysis.project_ranking import calculate_project_score


def test_calculate_score_key_metrics():
    """Test scoring with key_metrics analysis data"""
    analysis_data = {
        "by_activity": {
            "code": {"score": 100.0},
            "doc": {"score": 50.0},
            "data": {"score": 30.0}
        },
        "totals": {"files": 10, "lines": 500},
        "by_language": [
            {"language": "Python"},
            {"language": "JavaScript"}
        ]
    }
    
    score = calculate_project_score(analysis_data)
    assert score > 0
    assert isinstance(score, float)


def test_score_increases_with_tests():
    """Test that projects with tests score higher"""
    without_tests = {
        "structure": {"has_tests": False, "has_docs": False, "has_config": False},
        "metrics": {"total_lines_of_code": 100},
        "skills": [],
        "frameworks": []
    }
    
    with_tests = {
        "structure": {"has_tests": True, "has_docs": False, "has_config": False},
        "metrics": {"total_lines_of_code": 100},
        "skills": [],
        "frameworks": []
    }
    
    score_without = calculate_project_score(without_tests)
    score_with = calculate_project_score(with_tests)
    
    assert score_with > score_without


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

