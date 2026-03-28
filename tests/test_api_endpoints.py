"""
Tests for the main API endpoints: upload, consent, and project retrieval.
"""
import sys
import os
import pytest
import zipfile
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Adjust the path to import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from api.main import app


class TestProjectUploadEndpoint:
    """Test POST /api/projects/upload endpoint."""

    @patch('api.routes.project.add_file_to_db')
    def test_upload_valid_zip(self, mock_add_file):
        """Test uploading a valid ZIP file."""
        # Mock successful upload
        from upload_file import UploadResult
        mock_add_file.return_value = UploadResult(
            success=True,
            message="File 'test.zip' uploaded successfully!",
            error_type=None,
            data={
                "file_id": 123,
                "filename": "test.zip",
                "filepath": "/tmp/test.zip",
                "file_count": 5,
                "files": ["file1.txt", "file2.py"]
            }
        )

        # Create a temporary ZIP file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            with zipfile.ZipFile(f.name, 'w') as zf:
                zf.writestr("test.txt", "test content")
            temp_path = f.name

        try:
            client = TestClient(app)
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/api/projects/upload",
                    files={"file": ("test.zip", file, "application/zip")},
                    params={"user_name": "test_user"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "test.zip" in data["message"]
            assert data["data"]["file_id"] == 123
            mock_add_file.assert_called_once()
        finally:
            os.unlink(temp_path)

class TestPrivacyConsentEndpoint:
    """Test POST /api/settings/privacy endpoint (unified settings)."""

    @patch('api.routes.settings.ConsentStorage.store_consent')
    @patch('api.routes.settings.ConsentStorage.get_consent_status')
    @patch('api.dependencies.get_user_by_username')
    def test_post_consent_granted(self, mock_get_user, mock_get_status, mock_store):
        """Test storing consent when granted via settings endpoint."""
        mock_get_user.return_value = {
            'user_id': 1,
            'user_name': 'test_user',
            'is_login': True
        }
        mock_store.return_value = True
        mock_get_status.return_value = {
            'consent_given': True,
            'consent_date': '2024-01-01T00:00:00',
            'withdrawn_date': None,
            'consent_version': '1.0'
        }

        client = TestClient(app)
        response = client.post(
            "/api/settings/privacy?username=test_user",
            json={"consent_given": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["consent_given"] is True
        assert data["user_name"] == "test_user"  # Uses authenticated user's username
        assert "privacy" in data
        mock_store.assert_called_once_with(consent_given=True, user_name="test_user")
    
    @patch('api.routes.settings.ConsentStorage.store_consent')
    @patch('api.routes.settings.ConsentStorage.get_consent_status')
    @patch('api.dependencies.get_user_by_username')
    def test_post_consent_denied(self, mock_get_user, mock_get_status, mock_store):
        """Test storing consent when denied via settings endpoint."""
        mock_get_user.return_value = {
            'user_id': 1,
            'user_name': 'test_user',
            'is_login': True
        }
        mock_store.return_value = True
        mock_get_status.return_value = {
            'consent_given': False,
            'consent_date': '2024-01-01T00:00:00',
            'withdrawn_date': None,
            'consent_version': '1.0'
        }

        client = TestClient(app)
        response = client.post(
            "/api/settings/privacy?username=test_user",
            json={"consent_given": False}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["consent_given"] is False
        assert data["user_name"] == "test_user"  # Uses authenticated user's username
        assert "privacy" in data

class TestSettingsEndpoints:
    """Test unified settings endpoints."""

    @patch('api.dependencies.get_user_by_username')
    def test_get_account_settings(self, mock_get_user):
        """Test GET /api/settings/account endpoint."""
        from datetime import datetime
        mock_get_user.return_value = {
            'user_id': 1,
            'user_name': 'test_user',
            'create_time': datetime(2024, 1, 1, 0, 0, 0),
            'last_login_time': datetime(2024, 1, 2, 0, 0, 0),
            'is_login': True
        }

        client = TestClient(app)
        response = client.get("/api/settings/account?username=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["account"]["user_name"] == "test_user"
        assert data["account"]["is_login"] is True

    @patch('api.routes.settings.get_user_git_username')
    @patch('api.dependencies.get_user_by_username')
    def test_get_general_settings(self, mock_get_user, mock_get_git):
        """Test GET /api/settings/general endpoint."""
        mock_get_user.return_value = {
            'user_id': 1,
            'user_name': 'test_user',
            'is_login': True
        }
        mock_get_git.return_value = "test_github_user"

        client = TestClient(app)
        response = client.get("/api/settings/general?username=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["general"]["git_username"] == "test_github_user"

    @patch('api.routes.settings.update_user_git_username')
    @patch('api.routes.settings.get_user_git_username')
    @patch('api.dependencies.get_user_by_username')
    def test_update_general_settings(self, mock_get_user, mock_get_git, mock_update_git):
        """Test POST /api/settings/general endpoint."""
        mock_get_user.return_value = {
            'user_id': 1,
            'user_name': 'test_user',
            'is_login': True
        }
        mock_get_git.return_value = "new_github_user"

        client = TestClient(app)
        response = client.post(
            "/api/settings/general?username=test_user",
            json={"git_username": "new_github_user"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["general"]["git_username"] == "new_github_user"
        mock_update_git.assert_called_once_with("test_user", "new_github_user")

    @patch('api.routes.settings.ConsentStorage.get_consent_status')
    @patch('api.dependencies.get_user_by_username')
    def test_get_privacy_settings(self, mock_get_user, mock_get_status):
        """Test GET /api/settings/privacy endpoint."""
        mock_get_user.return_value = {
            'user_id': 1,
            'user_name': 'test_user',
            'is_login': True
        }
        mock_get_status.return_value = {
            'consent_given': True,
            'consent_date': '2024-01-01T00:00:00'
        }

        client = TestClient(app)
        response = client.get("/api/settings/privacy?username=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "privacy" in data


class TestDeleteProjectDataEndpoint:
    """Test DELETE /api/projects/{id}/data endpoint (renamed from /insights)."""

    @patch('api.routes.project.delete_insights')
    def test_delete_project_data_success(self, mock_delete):
        """Test successfully deleting project data."""
        mock_delete.return_value = (3, 5, 1)  # metrics, files, projects

        client = TestClient(app)
        response = client.delete("/api/projects/123/data?user_name=testuser")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted"]["metrics"] == 3
        assert data["deleted"]["files"] == 5
        assert data["deleted"]["projects"] == 1
        mock_delete.assert_called_once_with(123, user_name='testuser')

class TestGetProjectsEndpoint:
    """Test GET /api/projects endpoint."""

    @patch('api.routes.project.list_projects')
    def test_get_projects_with_user(self, mock_list):
        """Test getting projects for a specific user."""
        mock_list.return_value = [
            {
                'id': 1,
                'filename': 'project1.zip',
                'created_at': '2024-01-01',
                'file_count': 10,
                'has_thumbnail': True
            },
            {
                'id': 2,
                'filename': 'project2.zip',
                'created_at': '2024-01-02',
                'file_count': 5,
                'has_thumbnail': False
            }
        ]

        client = TestClient(app)
        response = client.get("/api/projects?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 2
        assert len(data["projects"]) == 2
        assert data["projects"][0]["filename"] == "project1.zip"
        mock_list.assert_called_once_with(user_name="test_user")

    @patch('api.routes.project.list_uploaded_files')
    def test_get_all_projects(self, mock_list):
        """Test getting all projects when no user specified."""
        from datetime import datetime
        mock_list.return_value = [
            {
                'id': 1,
                'filename': 'project1.zip',
                'status': 'uploaded',
                'metadata': '{"files": ["file1.txt"]}',
                'created_at': datetime(2024, 1, 1, 10, 0, 0),
                'user_name': 'user1'
            }
        ]

        client = TestClient(app)
        response = client.get("/api/projects")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 1
        assert data["projects"][0]["id"] == 1


class TestGetProjectByIdEndpoint:
    """Test GET /api/projects/{id} endpoint."""

    @patch('api.routes.project.AuthManager')
    @patch('api.routes.project.get_project_by_id')
    def test_get_project_by_id_success(self, mock_get, mock_auth_manager):
        """Test successfully retrieving a project by ID."""
        from datetime import datetime
        mock_auth_manager.get_current_username.return_value = "test_user"
        # Mock should return nested structure with project_info
        mock_get.return_value = {
            'project_info': {
                'id': 123,
                'filename': 'test_project.zip',
                'filepath': '/uploads/test_project.zip',
                'status': 'uploaded',
                'created_at': datetime(2024, 1, 1, 0, 0, 0).isoformat()
            },
            'files': ['file1.txt', 'file2.py']
        }

        client = TestClient(app)
        response = client.get("/api/projects/123?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["project"]["id"] == 123
        assert data["project"]["filename"] == "test_project.zip"
        mock_get.assert_called_once_with(123, user_name="test_user")

    @patch('api.routes.project.get_project_by_id')
    def test_get_project_by_id_without_user(self, mock_get):
        """Test retrieving a project without user verification."""
        from datetime import datetime
        # Mock should return nested structure with project_info
        mock_get.return_value = {
            'project_info': {
                'id': 456,
                'filename': 'another_project.zip',
                'filepath': '/uploads/another_project.zip',
                'status': 'uploaded',
                'created_at': datetime(2024, 1, 2, 0, 0, 0).isoformat()
            }
        }

        client = TestClient(app)
        response = client.get("/api/projects/456")

        assert response.status_code == 200
        data = response.json()
        assert data["project"]["id"] == 456
        # Without AuthManager, API uses the user_name parameter (None if not provided)
        mock_get.assert_called_once_with(456, user_name=None)


class TestMergeProjectEndpoint:
    """Test POST /api/projects/{id}/merge endpoint."""

    @patch('api.routes.project.merge_zip_to_project')
    def test_merge_valid_zip_success(self, mock_merge):
        """Test successfully merging a valid ZIP file into a project."""
        from upload_file import UploadResult
        mock_merge.return_value = UploadResult(
            success=True,
            message="Successfully merged 5 new files into project 'test.zip'.",
            error_type=None,
            data={
                "project_id": 123,
                "new_files_count": 5,
                "skipped_duplicates": 2,
                "new_files": [
                    {"file_path": "new_file1.py", "file_name": "new_file1.py", "file_size": 100},
                    {"file_path": "new_file2.py", "file_name": "new_file2.py", "file_size": 200}
                ],
                "skipped_files": ["existing.py", "duplicate.py"],
                "errors": []
            }
        )

        # Create a temporary ZIP file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            with zipfile.ZipFile(f.name, 'w') as zf:
                zf.writestr("new_file.txt", "new content")
            temp_path = f.name

        try:
            client = TestClient(app)
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/api/projects/123/merge?user_name=test_user",
                    files={"file": ("additional.zip", file, "application/zip")}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "merged" in data["message"].lower()
            assert data["data"]["new_files_count"] == 5
            assert data["data"]["skipped_duplicates"] == 2
            mock_merge.assert_called_once()
        finally:
            os.unlink(temp_path)

    @patch('api.routes.project.merge_zip_to_project')
    def test_merge_with_duplicates_skipped(self, mock_merge):
        """Test that duplicate files are properly reported as skipped."""
        from upload_file import UploadResult
        mock_merge.return_value = UploadResult(
            success=True,
            message="Successfully merged 0 new files into project 'test.zip'.",
            error_type=None,
            data={
                "project_id": 123,
                "new_files_count": 0,
                "skipped_duplicates": 3,
                "new_files": [],
                "skipped_files": ["file1.py", "file2.py", "file3.py"],
                "errors": []
            }
        )

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            with zipfile.ZipFile(f.name, 'w') as zf:
                zf.writestr("file1.py", "content")
            temp_path = f.name

        try:
            client = TestClient(app)
            with open(temp_path, 'rb') as file:
                response = client.post(
                    "/api/projects/123/merge?user_name=test_user",
                    files={"file": ("duplicates.zip", file, "application/zip")}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["new_files_count"] == 0
            assert data["data"]["skipped_duplicates"] == 3
        finally:
            os.unlink(temp_path)


class TestResumePortfolioEndpoints:
    """Tests for the new Resume Item and Portfolio Card preview endpoints."""

    @patch('api.routes.resume_portfolio.get_project_with_analysis')
    def test_get_resume_preview_success(self, mock_get_db):
        """
        Test that the endpoint correctly converts raw data into a Resume Item.
        """
        # 1. Setup Mock Data
        mock_get_db.return_value = {
            'project_info': {
                'id': 101,
                'filename': 'stock_trader_v2.zip',
                'created_at': '2025-01-20T10:00:00'
            },
            'file_statistics': {
                'total_lines_of_code': 1200,
                'total_files': 15
            },
            'languages': {
                'detected_languages': ['Python', 'JavaScript']
            },
            'frameworks': ['React', 'FastAPI'],
            'project_structure': {
                'has_tests': True,
                'has_docs': False
            },
            'collaboration_analysis': {
                'contributors': ['Kevin', 'Sami']
            }
        }

        # 2. Call API (Added /api prefix)
        client = TestClient(app)
        response = client.get("/api/resume/preview/101")

        # 3. Assertions
        assert response.status_code == 200
        data = response.json()

        # Check transformation logic
        assert data['project_title'] == "Stock Trader V2"
        assert data['role'] == "Software Developer"
        assert len(data['description_bullets']) > 0

        # Verify tech stack merging
        assert "Python" in data['technologies']
        assert "React" in data['technologies']

    @patch('api.routes.resume_portfolio.get_project_with_analysis')
    def test_get_portfolio_card_success(self, mock_get_db):
        """
        Test that the endpoint correctly returns a rich Portfolio Card.
        """
        # 1. Setup Mock Data
        mock_get_db.return_value = {
            'project_info': {
                'id': 101,
                'filename': 'stock_trader_v2.zip',
                'created_at': '2025-01-20T10:00:00'
            },
            'file_statistics': {
                'total_lines_of_code': 1200,
                'total_files': 25
            },
            'languages': {
                'detected_languages': ['Python']
            },
            'project_structure': {
                'has_tests': True
            }
        }

        # 2. Call API (Added /api prefix)
        client = TestClient(app)
        response = client.get("/api/portfolio/card/101")

        # 3. Assertions
        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert data['title'] == "Stock Trader V2"
        assert "1200+ lines" in data['short_description']

        # Check evidence
        evidence_text = str(data['success_metrics'])
        assert "LOC" in evidence_text or "lines" in evidence_text
        assert "test" in evidence_text.lower()

    @patch('api.routes.resume_portfolio.get_project_with_analysis')
    def test_get_portfolio_card_not_found(self, mock_get_db):
        """Test 404 error for portfolio card."""
        mock_get_db.return_value = None

        client = TestClient(app)
        response = client.get("/api/portfolio/card/999")

        assert response.status_code == 404


class TestGetSkillsEndpoint:
    """Test GET /api/skills endpoint."""

    @patch('api.routes.resume_portfolio.ResumeManager.get_user_resume')
    def test_get_skills_with_resume_data(self, mock_get_resume):
        """Test GET /api/skills returns skills when user has a generated resume."""
        mock_get_resume.return_value = {
            'resume_data': {
                'all_skills': ['Python', 'JavaScript', 'React'],
                'categorized_skills': {'Languages': ['Python', 'JavaScript'], 'Frameworks': ['React']},
                'languages': ['Python', 'JavaScript'],
                'frameworks': ['React']
            }
        }

        client = TestClient(app)
        response = client.get("/api/skills?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["skills"] == ['Python', 'JavaScript', 'React']
        assert "categorized_skills" in data
        assert data["languages"] == ['Python', 'JavaScript']
        assert data["frameworks"] == ['React']

    @patch('api.routes.resume_portfolio.ResumeManager.get_user_resume')
    def test_get_skills_no_resume(self, mock_get_resume):
        """Test GET /api/skills returns empty structures when user has no resume."""
        mock_get_resume.return_value = None

        client = TestClient(app)
        response = client.get("/api/skills?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["skills"] == []
        assert data["categorized_skills"] == {}
        assert data["languages"] == []
        assert data["frameworks"] == []


class TestGetPortfolioEndpoint:
    """Test GET /api/portfolio/{user_id} endpoint."""

    @patch('api.routes.resume_portfolio.PortfolioManager')
    def test_get_portfolio_success(self, mock_pm_class):
        """Test GET /api/portfolio/{user_id} returns portfolio report."""
        mock_instance = MagicMock()
        mock_instance.generate_portfolio_report.return_value = {
            'user_name': 'test_user',
            'summary': {'total_projects': 2, 'total_files': 50},
            'projects': [],
            'skills': {'all_skills': ['Python']}
        }
        mock_pm_class.return_value = mock_instance

        client = TestClient(app)
        response = client.get("/api/portfolio/test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "portfolio" in data
        assert data["portfolio"]["user_name"] == "test_user"
        assert data["portfolio"]["summary"]["total_projects"] == 2
        mock_instance.generate_portfolio_report.assert_called_once_with(top_n=None)

class TestPostPortfolioGenerateEndpoint:
    """Test POST /api/portfolio/generate endpoint."""

    @patch('api.routes.resume_portfolio.PortfolioManager')
    def test_portfolio_generate_success(self, mock_pm_class):
        """Test POST /api/portfolio/generate returns generated portfolio."""
        mock_instance = MagicMock()
        mock_instance.generate_portfolio_report.return_value = {
            'user_name': 'test_user',
            'summary': {'total_projects': 3},
            'projects': [],
            'skills': {}
        }
        mock_pm_class.return_value = mock_instance

        client = TestClient(app)
        response = client.post(
            "/api/portfolio/generate?user_name=test_user",
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "portfolio" in data
        mock_instance.generate_portfolio_report.assert_called_once_with(top_n=None)

class TestPostPortfolioEditEndpoint:
    """Test POST /api/portfolio/{user_id}/edit endpoint."""

    def test_portfolio_edit_returns_coming_soon(self):
        """Test POST /api/portfolio/{user_id}/edit returns success (placeholder)."""
        client = TestClient(app)
        response = client.post(
            "/api/portfolio/test_user/edit",
            json={"project_id": 1, "custom_data": {"title": "My Title"}}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
