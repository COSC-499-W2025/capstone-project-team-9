"""
Tests for project ranking functionality
"""
import sys
import os
import pytest
from unittest.mock import patch, call
from datetime import datetime

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from analysis.project_ranking import (
    calculate_project_score,
    display_rankings,
    rank_and_summarize_top_projects,
    rank_all_projects
)


def test_calculate_score_key_metrics():
    """Test scoring with key_metrics analysis data"""
    analysis_data = {
        "by_activity": {
            "code": {"count": 10, "bytes": 5000},
            "doc": {"count": 5, "bytes": 2000},
            "data": {"count": 3, "bytes": 1000}
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
    # Score should be normalized to 0-100
    assert 0 <= score <= 100


def test_score_normalized_to_100():
    """Test that scores are normalized to 0-100 range"""
    analysis_data = {
        "by_activity": {
            "code": {"count": 100, "bytes": 50000},
            "doc": {"count": 20, "bytes": 10000}
        },
        "totals": {"files": 120, "lines": 5000},
        "by_language": [
            {"language": "Python"},
            {"language": "JavaScript"},
            {"language": "Java"}
        ]
    }
    
    score = calculate_project_score(analysis_data)
    # Score should be between 0 and 100
    assert 0 <= score <= 100
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


class TestDisplayRankings:
    def test_display_rankings_empty_list(self):
        display_rankings([])
    
    def test_display_rankings_with_projects(self):
        ranked_projects = [
            {
                "project_id": 1,
                "filename": "project1.zip",
                "score": 85.5,  # Normalized score (0-100)
                "created_at": datetime(2024, 1, 1)
            },
            {
                "project_id": 2,
                "filename": "project2.zip",
                "score": 72.3,  # Normalized score (0-100)
                "created_at": datetime(2024, 1, 2)
            }
        ]
        
        # Should process without error
        display_rankings(ranked_projects)


class TestRankAndSummarizeTopProjects:

    @patch('analysis.project_ranking.get_stored_ranking_by_project_id')
    @patch('analysis.project_ranking.summarize_project')
    @patch('analysis.project_ranking.rank_all_projects')
    def test_rank_and_summarize_top_projects_success(self, mock_rank_all, mock_summarize, mock_get_stored):
        mock_ranked = [
            {
                "project_id": 1,
                "filename": "top_project.zip",
                "score": 200.0,
                "created_at": datetime(2024, 1, 1),
                "analysis": {}
            },
            {
                "project_id": 2,
                "filename": "second_project.zip",
                "score": 150.0,
                "created_at": datetime(2024, 1, 2),
                "analysis": {}
            },
            {
                "project_id": 3,
                "filename": "third_project.zip",
                "score": 100.0,
                "created_at": datetime(2024, 1, 3),
                "analysis": {}
            }
        ]
        mock_rank_all.return_value = mock_ranked
        mock_summarize.return_value = "Summary text"
        # Mock get_stored_ranking_by_project_id to return None (no stored summaries)
        mock_get_stored.return_value = None
        
        rank_and_summarize_top_projects()
        
        # Verify rank_all_projects was called
        mock_rank_all.assert_called_once()
        
        # Verify get_stored_ranking_by_project_id was called for each project
        assert mock_get_stored.call_count == 3
        
        # On-the-fly summarization is disabled in CLI mode, so summarize_project should NOT be called
        assert mock_summarize.call_count == 0
    
    @patch('analysis.project_ranking.rank_all_projects')
    def test_rank_and_summarize_no_projects(self, mock_rank_all):
        mock_rank_all.return_value = []
        
        # Should not raise an exception
        rank_and_summarize_top_projects()
        
        mock_rank_all.assert_called_once()
    
    @patch('analysis.project_ranking.get_stored_ranking_by_project_id')
    @patch('analysis.project_ranking.summarize_project')
    @patch('analysis.project_ranking.rank_all_projects')
    def test_rank_and_summarize_less_than_3_projects(self, mock_rank_all, mock_summarize, mock_get_stored):
        mock_ranked = [
            {
                "project_id": 1,
                "filename": "only_project.zip",
                "score": 100.0,
                "created_at": datetime(2024, 1, 1),
                "analysis": {}
            }
        ]
        mock_rank_all.return_value = mock_ranked
        mock_summarize.return_value = "Summary text"
        # Mock get_stored_ranking_by_project_id to return None (no stored summaries)
        mock_get_stored.return_value = None
        
        rank_and_summarize_top_projects()
        
         # On-the-fly summarization is disabled; summarize_project should NOT be called
        assert mock_summarize.call_count == 0
        # We still query stored summary once (for the single project)
        assert mock_get_stored.call_count == 1
    
    @patch('analysis.project_ranking.get_stored_ranking_by_project_id')
    @patch('analysis.project_ranking.summarize_project')
    @patch('analysis.project_ranking.rank_all_projects')
    def test_rank_and_summarize_more_than_3_projects(self, mock_rank_all, mock_summarize, mock_get_stored):
        mock_ranked = [
            {"project_id": 1, "filename": "p1.zip", "score": 100.0, "created_at": datetime(2024, 1, 1), "analysis": {}},
            {"project_id": 2, "filename": "p2.zip", "score": 90.0, "created_at": datetime(2024, 1, 2), "analysis": {}},
            {"project_id": 3, "filename": "p3.zip", "score": 80.0, "created_at": datetime(2024, 1, 3), "analysis": {}},
            {"project_id": 4, "filename": "p4.zip", "score": 70.0, "created_at": datetime(2024, 1, 4), "analysis": {}},
            {"project_id": 5, "filename": "p5.zip", "score": 60.0, "created_at": datetime(2024, 1, 5), "analysis": {}}
        ]
        mock_rank_all.return_value = mock_ranked
        mock_summarize.return_value = "Summary text"
        # Mock get_stored_ranking_by_project_id to return None (no stored summaries)
        mock_get_stored.return_value = None
        
        rank_and_summarize_top_projects()
        
        # On-the-fly summarization is disabled; summarize_project should never be called
        assert mock_summarize.call_count == 0

        # We still query stored summaries for the top 3 projects
        assert mock_get_stored.call_count == 3
    
    @patch('analysis.project_ranking.get_stored_ranking_by_project_id')
    @patch('analysis.project_ranking.summarize_project')
    @patch('analysis.project_ranking.rank_all_projects')
    def test_rank_and_summarize_summary_error_handling(self, mock_rank_all, mock_summarize, mock_get_stored):
        mock_ranked = [
            {
                "project_id": 1,
                "filename": "project.zip",
                "score": 100.0,
                "created_at": datetime(2024, 1, 1),
                "analysis": {}
            }
        ]
        mock_rank_all.return_value = mock_ranked
        mock_summarize.side_effect = Exception("Summary error")
        mock_get_stored.return_value = None

        rank_and_summarize_top_projects()

        mock_rank_all.assert_called_once()
        mock_get_stored.assert_called_once_with(1)
        # On-the-fly summarization is disabled, so summarize_project should never be called
        mock_summarize.assert_not_called()
    
    @patch('analysis.project_ranking.get_stored_ranking_by_project_id')
    @patch('analysis.project_ranking.summarize_project')
    @patch('analysis.project_ranking.rank_all_projects')
    def test_rank_and_summarize_uses_stored_summary(self, mock_rank_all, mock_summarize, mock_get_stored):
        """Test that stored summaries are used when available"""
        mock_ranked = [
            {
                "project_id": 1,
                "filename": "project.zip",
                "score": 100.0,
                "created_at": datetime(2024, 1, 1),
                "analysis": {}
            }
        ]
        mock_rank_all.return_value = mock_ranked
        
        # Mock stored ranking with a summary
        mock_get_stored.return_value = {
            "project_id": 1,
            "summary": "This is a stored summary"
        }
        
        rank_and_summarize_top_projects()
        
        # Verify get_stored_ranking_by_project_id was called
        mock_get_stored.assert_called_once_with(1)
        # Verify summarize_project was NOT called (stored summary used instead)
        mock_summarize.assert_not_called()


class TestRankingStorage:
    """Tests for ranking storage functionality - all database operations are mocked"""
    
    @patch('analysis.ranking_storage.init_ranking_storage_table')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_save_rankings_to_database(self, mock_cursor, mock_init):
        """Test that rankings can be saved to the database (mocked, no DB changes)"""
        from analysis.ranking_storage import save_rankings_to_db
        
        # Mock database cursor context manager
        mock_cursor_obj = mock_cursor.return_value.__enter__.return_value
        mock_cursor_obj.fetchall.return_value = []  # No existing rankings
        
        ranked_projects = [
            {
                "project_id": 1,
                "filename": "project1.zip",
                "score": 150.5,
                "created_at": datetime(2024, 1, 1),
                "analysis": {}
            },
            {
                "project_id": 2,
                "filename": "project2.zip",
                "score": 120.3,
                "created_at": datetime(2024, 1, 2),
                "analysis": {}
            }
        ]
        
        summaries = {1: "Summary for project 1", 2: "Summary for project 2"}
        
        result = save_rankings_to_db(ranked_projects, summaries)
        
        # Verify save was attempted (but no actual DB changes)
        assert result is True
        # Verify init was called
        mock_init.assert_called_once()
        # Verify DELETE was called to clear existing rankings
        delete_calls = [str(call) for call in mock_cursor_obj.execute.call_args_list if "DELETE" in str(call[0])]
        assert len(delete_calls) > 0
        # Verify INSERT was called for each project
        insert_calls = [str(call) for call in mock_cursor_obj.execute.call_args_list if "INSERT" in str(call[0])]
        assert len(insert_calls) == 2
    
    @patch('analysis.project_ranking.get_stored_rankings')
    @patch('analysis.project_ranking.analyze_project_from_db')
    @patch('analysis.project_ranking.get_connection')
    def test_rank_all_projects_uses_stored_scores(self, mock_conn, mock_analyze, mock_get_stored):
        """Test that stored scores are used when available (mocked, no DB changes)"""
        # Mock stored rankings with edited scores
        mock_get_stored.return_value = [
            {
                "project_id": 1,
                "score": 85.5,  # Edited score (normalized to 0-100)
                "rank_position": 1
            }
        ]
        
        # Mock database connection with nested context manager pattern
        # The code uses: with get_connection() as conn, conn.cursor() as cur:
        mock_connection = mock_conn.return_value.__enter__.return_value
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [
            (1, "project1.zip", datetime(2024, 1, 1))
        ]
        
        # Mock analysis (should still be called for analysis data)
        mock_analyze.return_value = {
            "by_activity": {"code": {"count": 10, "bytes": 1000}},
            "totals": {"lines": 500},
            "by_language": []
        }
        
        ranked = rank_all_projects()
        
        # Verify stored score was used
        assert len(ranked) == 1
        assert ranked[0]["score"] == 85.5  # Should use stored score, not calculated
        # Verify score is in valid range
        assert 0 <= ranked[0]["score"] <= 100
        # Verify analysis was still called (needed for other data)
        mock_analyze.assert_not_called()
        # Verify get_stored_rankings was called to check for stored scores
        mock_get_stored.assert_called_once()
    
    @patch('analysis.project_ranking.get_stored_rankings')
    @patch('analysis.project_ranking.calculate_project_score')
    @patch('analysis.project_ranking.analyze_project_from_db')
    @patch('analysis.project_ranking.get_connection')
    def test_rank_all_projects_calls_deep_analysis(self, mock_conn, mock_analyze, mock_calculate, mock_get_stored):
        """Test that rank_all_projects passes project_id to calculate_project_score for deep analysis"""
        # Mock no stored rankings (so calculate_project_score will be called)
        mock_get_stored.return_value = []
        
        # Mock database connection
        mock_connection = mock_conn.return_value.__enter__.return_value
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [
            (1, "project1.zip", datetime(2024, 1, 1))
        ]
        
        # Mock analysis
        mock_analyze.return_value = {
            "by_activity": {"code": {"count": 10, "bytes": 1000}},
            "totals": {"lines": 500},
            "by_language": []
        }
        
        # Mock calculate_project_score to return normalized score
        mock_calculate.return_value = 75.5
        
        ranked = rank_all_projects()
        
        # Verify calculate_project_score was called with project_id
        mock_calculate.assert_called_once()
        args, kwargs = mock_calculate.call_args
        # Lightweight mode: we no longer pass project_id from rank_all_projects
        assert len(args) == 1
        assert isinstance(args[0], dict)
        assert kwargs == {}

        # Verify score is normalized
        assert len(ranked) == 1
        assert 0 <= ranked[0]["score"] <= 100


class TestDeepCodeAnalysisIntegration:
    """Tests for deep code analysis integration in ranking system"""
    
    @patch('analysis.project_ranking.get_file_contents_by_upload_id')
    @patch('analysis.project_ranking.LocalAnalyzer')
    def test_deep_code_analysis_integration(self, mock_local_analyzer_class, mock_get_files):
        """Test that deep code analysis is integrated into scoring"""
        # Mock file contents
        mock_get_files.return_value = [
            {
                "file_path": "main.py",
                "file_name": "main.py",
                "file_extension": ".py",
                "file_content": "class Test:\n    def method(self):\n        pass",
                "content_type": "Python",
                "is_binary": False
            }
        ]
        
        # Mock LocalAnalyzer
        mock_analyzer = mock_local_analyzer_class.return_value
        mock_analyzer.analyze_files_from_db.return_value = {
            "oop_principles_summary": {
                "abstraction": {"count": 2, "examples": []},
                "encapsulation": {"count": 1, "examples": []},
                "polymorphism": {"count": 1, "examples": []},
                "inheritance": {"count": 0, "examples": []}
            },
            "data_structure_summary": {"hash_map": 5, "list": 3},
            "complexity_summary": {
                "nested_loops": 2,
                "recursive_functions": 1,
                "complexity_awareness": True
            },
            "optimization_summary": [
                {"type": "Caching/Memoization", "evidence": "Uses caching"}
            ],
            "code_quality_summary": {
                "average_quality_score": 75.0,
                "strengths": ["Uses abstraction", "Demonstrates encapsulation"]
            }
        }
        
        analysis_data = {
            "by_activity": {
                "code": {"count": 10, "bytes": 5000}
            },
            "totals": {"files": 10, "lines": 500},
            "by_language": [{"language": "Python"}]
        }
        
        # Test with project_id (should trigger deep analysis)
        score_with_deep = calculate_project_score(analysis_data, project_id=1)
        
        # Test without project_id (no deep analysis)
        score_without_deep = calculate_project_score(analysis_data)
        
        # Score with deep analysis should be higher
        assert score_with_deep > score_without_deep
        # Both should be normalized to 0-100
        assert 0 <= score_with_deep <= 100
        assert 0 <= score_without_deep <= 100
        # Verify deep analysis was called
        mock_get_files.assert_called_once_with(1)
        mock_analyzer.analyze_files_from_db.assert_called_once()
    
    @patch('analysis.project_ranking.get_file_contents_by_upload_id')
    @patch('analysis.project_ranking.LocalAnalyzer')
    def test_all_deep_analysis_components_scoring(self, mock_local_analyzer_class, mock_get_files):
        """Test that all deep analysis components (OOP, data structures, complexity, optimizations, code quality) contribute to score"""
        # Return a non-empty list so _perform_deep_code_analysis doesn't return early
        mock_get_files.return_value = [{"file_path": "test.py", "file_content": "code", "is_binary": False}]
        
        mock_analyzer = mock_local_analyzer_class.return_value
        # Test with comprehensive deep analysis results covering all components
        mock_analyzer.analyze_files_from_db.return_value = {
            "oop_principles_summary": {
                "abstraction": {"count": 5, "examples": []},
                "encapsulation": {"count": 4, "examples": []},
                "polymorphism": {"count": 3, "examples": []},
                "inheritance": {"count": 2, "examples": []}
            },
            "data_structure_summary": {"hash_map": 10, "list": 8, "set": 5},
            "complexity_summary": {
                "nested_loops": 5,
                "recursive_functions": 3,
                "complexity_awareness": True
            },
            "optimization_summary": [
                {"type": "Caching/Memoization"},
                {"type": "Lazy Loading/Async"},
                {"type": "Early Returns"},
                {"type": "String Optimization"}
            ],
            "code_quality_summary": {
                "average_quality_score": 90.0,
                "strengths": ["Uses abstraction", "Demonstrates encapsulation", "Shows complexity awareness", "Implements optimizations"]
            }
        }
        
        # Use a larger base score so the difference is more noticeable
        analysis_data = {
            "by_activity": {
                "code": {"count": 20, "bytes": 50000},
                "doc": {"count": 5, "bytes": 10000}
            },
            "totals": {"files": 25, "lines": 2000},
            "by_language": [
                {"language": "Python"},
                {"language": "JavaScript"}
            ]
        }
        
        # Test with deep analysis
        score_with_deep = calculate_project_score(analysis_data, project_id=1)
        # Test without deep analysis for comparison
        score_without_deep = calculate_project_score(analysis_data)
        
        # Both should be normalized to 0-100
        assert 0 <= score_with_deep <= 100
        assert 0 <= score_without_deep <= 100
        assert isinstance(score_with_deep, float)
        # Score with deep analysis should be higher (with larger base score, difference should be noticeable)
        assert score_with_deep > score_without_deep
        # Verify deep analysis was called
        mock_get_files.assert_called_once_with(1)
        mock_analyzer.analyze_files_from_db.assert_called_once()
    
    @patch('analysis.project_ranking.get_file_contents_by_upload_id')
    @patch('analysis.project_ranking.LocalAnalyzer')
    def test_deep_analysis_edge_cases_and_capping(self, mock_local_analyzer_class, mock_get_files):
        """Test edge cases: empty results, no files, exceptions, and score capping"""
        analysis_data = {
            "by_activity": {"code": {"count": 5, "bytes": 1000}},
            "totals": {"files": 5, "lines": 100},
            "by_language": []
        }
        
        # Test 1: Empty deep analysis results
        mock_get_files.return_value = []
        mock_analyzer = mock_local_analyzer_class.return_value
        mock_analyzer.analyze_files_from_db.return_value = {}
        score_empty = calculate_project_score(analysis_data, project_id=1)
        assert 0 <= score_empty <= 100
        assert isinstance(score_empty, float)
        
        # Test 2: No files returned
        mock_get_files.return_value = []
        score_no_files = calculate_project_score(analysis_data, project_id=1)
        assert 0 <= score_no_files <= 100
        assert isinstance(score_no_files, float)
        
        # Test 3: Exception handling
        mock_get_files.side_effect = Exception("Database error")
        score_exception = calculate_project_score(analysis_data, project_id=1)
        assert 0 <= score_exception <= 100
        assert isinstance(score_exception, float)
        
        # Test 4: Maximum scores (should be properly capped)
        mock_get_files.side_effect = None
        mock_get_files.return_value = []
        mock_analyzer.analyze_files_from_db.return_value = {
            "oop_principles_summary": {
                "abstraction": {"count": 100, "examples": []},  # Should cap at 3.75 per principle
                "encapsulation": {"count": 100, "examples": []},
                "polymorphism": {"count": 100, "examples": []},
                "inheritance": {"count": 100, "examples": []}
            },
            "data_structure_summary": {"hash_map": 100, "list": 100},  # Should cap at 10
            "complexity_summary": {
                "nested_loops": 100,
                "recursive_functions": 100,
                "complexity_awareness": True
            },
            "optimization_summary": [
                {"type": "Caching"}, {"type": "Lazy"}, {"type": "Early"}, {"type": "String"}, {"type": "Extra"}
            ],
            "code_quality_summary": {
                "average_quality_score": 100.0,
                "strengths": ["Strength1", "Strength2", "Strength3", "Strength4", "Strength5", "Strength6"]
            }
        }
        score_max = calculate_project_score(analysis_data, project_id=1)
        # Score should still be normalized to 0-100 even with maximum values
        assert 0 <= score_max <= 100
    
    def test_score_without_project_id(self):
        """Test that scoring works without project_id (no deep analysis)"""
        analysis_data = {
            "by_activity": {
                "code": {"count": 10, "bytes": 5000},
                "doc": {"count": 5, "bytes": 2000}
            },
            "totals": {"files": 15, "lines": 1000},
            "by_language": [
                {"language": "Python"},
                {"language": "JavaScript"}
            ]
        }
        
        # Should work without project_id
        score = calculate_project_score(analysis_data)
        assert 0 <= score <= 100
        assert isinstance(score, float)
        assert score > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

