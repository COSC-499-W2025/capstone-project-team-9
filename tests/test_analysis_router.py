"""
Unit tests for analysis routing conditional logic.
Tests Sub-issue #38: Implement conditional logic.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from analysis.analysis_router import AnalysisRouter
from external_services.permission_manager import ExternalServicePermission
from external_services.service_config import ServiceConfig


class TestAnalysisRouter:
    """Test cases for AnalysisRouter conditional logic."""
    
    @pytest.fixture
    def router(self):
        """Create a router instance for testing."""
        return AnalysisRouter(user_id='test_user')
    
    @pytest.fixture
    def clean_db(self):
        """Clean up test data before and after tests."""
       
        from config.db_config import get_connection
        from external_services.service_config import ServiceConfig
        config = ServiceConfig()
        config.initialize_table()
        
        # Clean any existing test data
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM external_service_permissions WHERE user_id = 'test_user'")
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Warning during cleanup: {e}")
            finally:
                cursor.close()
                conn.close()
        
        yield
        
        # Teardown: Clean after test
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM external_service_permissions WHERE user_id = 'test_user'")
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Warning during cleanup: {e}")
            finally:
                cursor.close()
                conn.close()
    
    def test_should_use_external_service_no_permission(self, router, clean_db):
        """Test that external service is not used when no permission exists."""
        result = router.should_use_external_service('LLM')
        assert result == False, "Should return False when no permission record exists"
    
    def test_should_use_external_service_with_permission(self, router, clean_db):
        """Test that external service is used when permission is granted."""
        # Grant permission
        config = ServiceConfig()
        config.initialize_table()
        
        from config.db_config import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO external_service_permissions (user_id, service_name, permission_granted)
            VALUES ('test_user', 'LLM', TRUE)
        """)
        conn.commit()
        conn.close()
        
        result = router.should_use_external_service('LLM')
        assert result == True, "Should return True when permission is granted"
    
    def test_should_use_external_service_permission_denied(self, router, clean_db):
        """Test that external service is not used when permission is denied."""
        # Deny permission
        config = ServiceConfig()
        config.initialize_table()
        
        from config.db_config import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO external_service_permissions (user_id, service_name, permission_granted)
            VALUES ('test_user', 'LLM', FALSE)
        """)
        conn.commit()
        conn.close()
        
        result = router.should_use_external_service('LLM')
        assert result == False, "Should return False when permission is denied"
    
    def test_get_analysis_strategy_local_only(self, router, clean_db):
        """Test that local strategy is returned when no external permission."""
        strategy = router.get_analysis_strategy('project')
        assert strategy == 'local', "Should return 'local' strategy when no external permission"
    
    def test_get_analysis_strategy_enhanced(self, router, clean_db):
        """Test that enhanced strategy is returned when external permission granted."""
        # Grant permission
        config = ServiceConfig()
        config.initialize_table()
        
        from config.db_config import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO external_service_permissions (user_id, service_name, permission_granted)
            VALUES ('test_user', 'LLM', TRUE)
        """)
        conn.commit()
        conn.close()
        
        strategy = router.get_analysis_strategy('project')
        assert strategy == 'enhanced', "Should return 'enhanced' strategy when external permission granted"
    
    def test_route_analysis_returns_correct_structure(self, router, clean_db):
        """Test that route_analysis returns correct data structure."""
        test_data = {'file': 'test.py', 'path': '/test'}
        result = router.route_analysis(test_data, 'project')
        
        assert 'strategy_used' in result, "Result should contain strategy_used"
        assert 'analysis_type' in result, "Result should contain analysis_type"
        assert 'data' in result, "Result should contain data"
        assert 'status' in result, "Result should contain status"
        assert result['analysis_type'] == 'project', "Analysis type should match input"
        assert result['data'] == test_data, "Data should match input"
    
    def test_route_analysis_uses_local_strategy(self, router, clean_db):
        """Test that routing uses local strategy when no permission."""
        test_data = {'file': 'test.py'}
        result = router.route_analysis(test_data, 'skill')
        
        assert result['strategy_used'] == 'local', "Should use local strategy"
    
    def test_route_analysis_uses_enhanced_strategy(self, router, clean_db):
        """Test that routing uses enhanced strategy when permission granted."""
        # Grant permission
        config = ServiceConfig()
        config.initialize_table()
        
        from config.db_config import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO external_service_permissions (user_id, service_name, permission_granted)
            VALUES ('test_user', 'LLM', TRUE)
        """)
        conn.commit()
        conn.close()
        
        test_data = {'file': 'test.py'}
        result = router.route_analysis(test_data, 'contribution')
        
        assert result['strategy_used'] == 'enhanced', "Should use enhanced strategy"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])