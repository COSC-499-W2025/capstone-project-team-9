"""
Tests for ranking storage functionality
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
import json

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from analysis.ranking_storage import (
    init_ranking_storage_table,
    save_rankings_to_db,
    get_stored_rankings,
    get_stored_ranking_by_project_id,
    update_ranking_score,
    update_ranking_summary,
    update_ranking_position,
    delete_stored_rankings,
    insert_or_update_single_ranking
)


class TestInitRankingStorageTable:
    """Test table initialization"""
    
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_init_ranking_storage_table_success(self, mock_with_db_cursor):
        """Test successful table initialization"""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        init_ranking_storage_table()
        
        # Verify table creation and index creation were called
        assert mock_cursor.execute.call_count >= 3  # Table + 2 indexes
        mock_with_db_cursor.assert_called_once()
    
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_init_ranking_storage_table_error(self, mock_with_db_cursor):
        """Test table initialization with error"""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            init_ranking_storage_table()


class TestSaveRankingsToDb:
    """Test saving rankings to database"""
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.init_ranking_storage_table')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_save_rankings_to_db_success(self, mock_with_db_cursor, mock_init_table, mock_get_user):
        """Test successful save of rankings"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []  # No existing summaries
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        ranked_projects = [
            {
                "project_id": 1,
                "score": 85.5,
                "analysis": {"key": "value"},
                "filename": "project1.zip",
                "created_at": datetime(2024, 1, 1)
            },
            {
                "project_id": 2,
                "score": 72.3,
                "analysis": {"key2": "value2"},
                "filename": "project2.zip"
            }
        ]
        
        result = save_rankings_to_db(ranked_projects)
        
        assert result is True
        mock_init_table.assert_called_once()
        # Should delete existing, then insert 2 new rankings
        assert mock_cursor.execute.call_count >= 3
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.init_ranking_storage_table')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_save_rankings_with_summaries(self, mock_with_db_cursor, mock_init_table, mock_get_user):
        """Test saving rankings with provided summaries"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        ranked_projects = [
            {"project_id": 1, "score": 85.5, "analysis": {}, "filename": "test.zip"}
        ]
        summaries = {1: "This is a test summary"}
        
        result = save_rankings_to_db(ranked_projects, summaries)
        
        assert result is True
        # Verify summary was used in insert
        insert_calls = [call for call in mock_cursor.execute.call_args_list 
                       if 'INSERT INTO project_rankings' in str(call)]
        assert len(insert_calls) > 0
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.init_ranking_storage_table')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_save_rankings_preserves_existing_summaries(self, mock_with_db_cursor, mock_init_table, mock_get_user):
        """Test that existing summaries are preserved when not provided"""
        mock_cursor = Mock()
        # Simulate existing summary in database
        mock_cursor.fetchall.return_value = [(1, "Existing summary")]
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        ranked_projects = [
            {"project_id": 1, "score": 85.5, "analysis": {}, "filename": "test.zip"}
        ]
        
        result = save_rankings_to_db(ranked_projects, summaries=None)
        
        assert result is True
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.init_ranking_storage_table')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_save_rankings_error(self, mock_with_db_cursor, mock_init_table, mock_get_user):
        """Test error handling when saving rankings"""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        ranked_projects = [{"project_id": 1, "score": 85.5}]
        result = save_rankings_to_db(ranked_projects)
        
        assert result is False


class TestGetStoredRankings:
    """Test retrieving stored rankings"""
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_get_stored_rankings_success(self, mock_with_db_cursor, mock_get_user):
        """Test successful retrieval of rankings"""
        mock_cursor = Mock()
        mock_results = [
            (1, 10, 1, 85.5, "Summary 1", {"key": "value"}, "test_user", datetime(2024, 1, 1), datetime(2024, 1, 2)),
            (2, 20, 2, 72.3, "Summary 2", {"key2": "value2"}, "test_user", datetime(2024, 1, 3), datetime(2024, 1, 4))
        ]
        mock_cursor.fetchall.return_value = mock_results
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = get_stored_rankings()
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["project_id"] == 10
        assert result[0]["rank_position"] == 1
        assert result[0]["score"] == 85.5
        assert result[0]["summary"] == "Summary 1"
        assert result[1]["rank_position"] == 2
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_get_stored_rankings_empty(self, mock_with_db_cursor, mock_get_user):
        """Test retrieval when no rankings exist"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = []
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = get_stored_rankings()
        
        assert result == []
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_get_stored_rankings_with_none_ranking_data(self, mock_with_db_cursor, mock_get_user):
        """Test retrieval when ranking_data is None"""
        mock_cursor = Mock()
        mock_results = [
            (1, 10, 1, 85.5, "Summary", None, "test_user", datetime(2024, 1, 1), datetime(2024, 1, 2))
        ]
        mock_cursor.fetchall.return_value = mock_results
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = get_stored_rankings()
        
        assert len(result) == 1
        assert result[0]["ranking_data"] == {}
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_get_stored_rankings_error(self, mock_with_db_cursor, mock_get_user):
        """Test error handling when retrieving rankings"""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = get_stored_rankings()
        
        assert result == []


class TestGetStoredRankingByProjectId:
    """Test retrieving ranking by project ID"""
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_get_stored_ranking_by_project_id_success(self, mock_with_db_cursor, mock_get_user):
        """Test successful retrieval by project ID"""
        mock_cursor = Mock()
        mock_row = (1, 10, 1, 85.5, "Summary", {"key": "value"}, datetime(2024, 1, 1), datetime(2024, 1, 2))
        mock_cursor.fetchone.return_value = mock_row
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = get_stored_ranking_by_project_id(10)
        
        assert result is not None
        assert result["project_id"] == 10
        assert result["score"] == 85.5
        assert result["summary"] == "Summary"
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_get_stored_ranking_by_project_id_not_found(self, mock_with_db_cursor, mock_get_user):
        """Test retrieval when project ID doesn't exist"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = get_stored_ranking_by_project_id(999)
        
        assert result is None
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_get_stored_ranking_by_project_id_error(self, mock_with_db_cursor, mock_get_user):
        """Test error handling when retrieving by project ID"""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = get_stored_ranking_by_project_id(10)
        
        assert result is None


class TestUpdateRankingScore:
    """Test updating ranking score"""
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_update_ranking_score_success(self, mock_with_db_cursor, mock_get_user):
        """Test successful score update"""
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = update_ranking_score(10, 95.0)
        
        assert result is True
        assert mock_cursor.execute.call_count == 2
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_update_ranking_score_not_found(self, mock_with_db_cursor, mock_get_user):
        """Test score update when project doesn't exist"""
        mock_cursor = Mock()
        mock_cursor.rowcount = 0
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = update_ranking_score(999, 95.0)
        
        assert result is False
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_update_ranking_score_error(self, mock_with_db_cursor, mock_get_user):
        """Test error handling when updating score"""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = update_ranking_score(10, 95.0)
        
        assert result is False


class TestUpdateRankingSummary:
    """Test updating ranking summary"""
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_update_ranking_summary_success(self, mock_with_db_cursor, mock_get_user):
        """Test successful summary update"""
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = update_ranking_summary(10, "New summary text")
        
        assert result is True
        mock_cursor.execute.assert_called_once()
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_update_ranking_summary_not_found(self, mock_with_db_cursor, mock_get_user):
        """Test summary update when project doesn't exist"""
        mock_cursor = Mock()
        mock_cursor.rowcount = 0
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = update_ranking_summary(999, "New summary")
        
        assert result is False
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_update_ranking_summary_error(self, mock_with_db_cursor, mock_get_user):
        """Test error handling when updating summary"""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = update_ranking_summary(10, "New summary")
        
        assert result is False


class TestUpdateRankingPosition:
    """Test updating ranking position"""
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_update_ranking_position_success_no_swap(self, mock_with_db_cursor, mock_get_user):
        """Test successful position update when position is free"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None  # Position not taken
        mock_cursor.rowcount = 1
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = update_ranking_position(10, 3)
        
        assert result is True
        # Should check for existing, then update
        assert mock_cursor.execute.call_count >= 2
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_update_ranking_position_with_swap(self, mock_with_db_cursor, mock_get_user):
        """Test position update with position swap"""
        mock_cursor = Mock()
        # First call: position is taken by another project
        # Second call: get current position
        mock_cursor.fetchone.side_effect = [
            (20,),  # Another project has position 3
            (1,)    # Current project is at position 1
        ]
        mock_cursor.rowcount = 1
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = update_ranking_position(10, 3)
        
        assert result is True
        # Should check, get current, swap, then update
        assert mock_cursor.execute.call_count >= 3
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_update_ranking_position_not_found(self, mock_with_db_cursor, mock_get_user):
        """Test position update when project doesn't exist"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_cursor.rowcount = 0
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = update_ranking_position(999, 3)
        
        assert result is False
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_update_ranking_position_error(self, mock_with_db_cursor, mock_get_user):
        """Test error handling when updating position"""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = update_ranking_position(10, 3)
        
        assert result is False


class TestDeleteStoredRankings:
    """Test deleting stored rankings"""
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_delete_stored_rankings_success(self, mock_with_db_cursor, mock_get_user):
        """Test successful deletion of all rankings"""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        result = delete_stored_rankings()
        
        assert result is True
        mock_cursor.execute.assert_called_once()
        assert "DELETE FROM project_rankings" in str(mock_cursor.execute.call_args)
    
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_delete_stored_rankings_error(self, mock_with_db_cursor, mock_get_user):
        """Test error handling when deleting rankings"""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = delete_stored_rankings()
        
        assert result is False


class TestInsertOrUpdateSingleRanking:
    """Test inserting or updating single ranking entries"""
    
    @patch('analysis.ranking_storage.init_ranking_storage_table')
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_insert_new_ranking(self, mock_with_db_cursor, mock_get_user, mock_init):
        """Test inserting a new ranking entry without affecting others"""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        # Simulate no existing record for this project
        mock_cursor.fetchone.side_effect = [None, (5,)]  # First: no existing, Second: max rank + 1
        
        result = insert_or_update_single_ranking(
            project_id=123,
            summary="Test summary",
            score=85.5
        )
        
        assert result is True
        # Should query for existing, then get max rank position, then insert
        assert mock_cursor.execute.call_count >= 2
        
        # Verify INSERT was called
        insert_call = [call for call in mock_cursor.execute.call_args_list if 'INSERT' in str(call)]
        assert len(insert_call) > 0
    
    @patch('analysis.ranking_storage.init_ranking_storage_table')
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_update_existing_ranking(self, mock_with_db_cursor, mock_get_user, mock_init):
        """Test updating an existing ranking entry"""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        # Simulate existing record
        mock_cursor.fetchone.return_value = (3, 75.0)  # existing rank_position=3, score=75.0
        
        result = insert_or_update_single_ranking(
            project_id=123,
            summary="Updated summary",
            score=90.0
        )
        
        assert result is True
        # Should query for existing, then update
        assert mock_cursor.execute.call_count >= 2
        
        # Verify UPDATE was called
        update_call = [call for call in mock_cursor.execute.call_args_list if 'UPDATE' in str(call)]
        assert len(update_call) > 0
    
    @patch('analysis.ranking_storage.init_ranking_storage_table')
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_multiple_projects_not_affected(self, mock_with_db_cursor, mock_get_user, mock_init):
        """Test that inserting one project doesn't affect others"""
        mock_cursor = Mock()
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        mock_with_db_cursor.return_value = mock_context
        
        # Simulate no existing record
        mock_cursor.fetchone.side_effect = [None, (3,)]  # No existing, max rank is 2 (so 3 is returned)
        
        result = insert_or_update_single_ranking(
            project_id=456,
            summary="Another project summary"
        )
        
        assert result is True
        
        # Verify NO DELETE was called (the key fix)
        delete_calls = [call for call in mock_cursor.execute.call_args_list if 'DELETE' in str(call)]
        assert len(delete_calls) == 0, "Should not delete any existing rankings"
    
    @patch('analysis.ranking_storage.init_ranking_storage_table')
    @patch('analysis.ranking_storage.AuthManager.get_current_username', return_value='test_user')
    @patch('analysis.ranking_storage.with_db_cursor')
    def test_insert_or_update_error(self, mock_with_db_cursor, mock_get_user, mock_init):
        """Test error handling"""
        mock_with_db_cursor.side_effect = Exception("Database error")
        
        result = insert_or_update_single_ranking(
            project_id=789,
            summary="Test summary"
        )
        
        assert result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
