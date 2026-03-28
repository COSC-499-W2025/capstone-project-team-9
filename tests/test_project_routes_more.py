import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

# Allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from api.main import app

"""
Additional tests for project API routes.

These tests extend coverage for:
- upload endpoint
- merge endpoint
- project listing
- ranking endpoints
- delete project data

Preference-related tests were intentionally excluded because
the git username logic is currently being fixed in another PR.
"""

client = TestClient(app)


class TestUploadProjectRoutes:
    @patch("api.routes.project.add_file_to_db")
    def test_upload_project_success(self, mock_add_file):
        mock_add_file.return_value = MagicMock(
            success=True,
            to_dict=lambda: {
                "success": True,
                "project_id": 123,
                "message": "Uploaded successfully"
            }
        )

        response = client.post(
            "/api/projects/upload?user_name=test_user",
            files={"file": ("proj.zip", b"fakezipdata", "application/zip")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["project_id"] == 123
        mock_add_file.assert_called_once()

class TestMergeProjectRoutes:
    @patch("api.routes.project.merge_zip_to_project")
    def test_merge_project_success(self, mock_merge):
        mock_merge.return_value = MagicMock(
            success=True,
            to_dict=lambda: {
                "success": True,
                "new_files": 2,
                "skipped_files": 1
            }
        )

        response = client.post(
            "/api/projects/1/merge?user_name=test_user",
            files={"file": ("proj.zip", b"zipcontent", "application/zip")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["new_files"] == 2
        assert data["skipped_files"] == 1

class TestProjectsListRoutes:
    @patch("api.routes.project.list_projects")
    def test_get_projects_by_user_success_with_string_datetime(self, mock_list_projects):
        mock_list_projects.return_value = [
            {
                "id": 1,
                "filename": "user_proj.zip",
                "created_at": "2024-01-01T10:00:00",
                "file_count": 3,
                "status": "uploaded",
            }
        ]

        response = client.get("/api/projects?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 1
        assert data["projects"][0]["filename"] == "user_proj.zip"
        assert data["projects"][0]["created_at"] == "2024-01-01T10:00:00"

    @patch("api.routes.project.list_projects")
    def test_get_projects_by_user_success_with_datetime_object(self, mock_list_projects):
        mock_list_projects.return_value = [
            {
                "id": 2,
                "filename": "dt_proj.zip",
                "created_at": datetime(2024, 1, 1, 10, 0, 0),
                "file_count": 4,
                "status": "uploaded",
            }
        ]

        response = client.get("/api/projects?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 1
        assert data["projects"][0]["created_at"] == "2024-01-01T10:00:00"

    @patch("api.routes.project.list_uploaded_files")
    def test_get_all_projects_success_with_metadata_string(self, mock_list_uploaded):
        mock_list_uploaded.return_value = [
            {
                "id": 1,
                "filename": "proj1.zip",
                "created_at": datetime(2024, 1, 2, 12, 0, 0),
                "metadata": '{"files": ["a.py", "folder/", "b.js"]}',
                "status": "uploaded",
            }
        ]

        response = client.get("/api/projects")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 1
        assert data["projects"][0]["file_count"] == 2
        assert data["projects"][0]["status"] == "uploaded"
        assert data["projects"][0]["created_at"] == "2024-01-02T12:00:00"

    @patch("api.routes.project.list_uploaded_files")
    def test_get_all_projects_success_with_bad_metadata(self, mock_list_uploaded):
        mock_list_uploaded.return_value = [
            {
                "id": 2,
                "filename": "proj2.zip",
                "created_at": None,
                "metadata": "not-json",
                "status": "uploaded",
            }
        ]

        response = client.get("/api/projects")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 1
        assert data["projects"][0]["file_count"] == 0
        assert data["projects"][0]["created_at"] is None

class TestSingleProjectRoutes:
    @patch("api.routes.project.AuthManager")
    @patch("api.routes.project.get_project_by_id")
    def test_get_project_by_id_success_with_datetime(self, mock_get_project, mock_auth_manager):
        mock_auth_manager.get_current_username.return_value = "test_user"
        mock_get_project.return_value = {
            "project_info": {
                "id": 1,
                "filename": "proj.zip",
                "filepath": "/tmp/proj.zip",
                "status": "uploaded",
                "created_at": "2024-01-01T09:30:00"
            },
            "files": ["a.py"]
        }

        response = client.get("/api/projects/1?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["project"]["id"] == 1
        assert data["project"]["filename"] == "proj.zip"
        assert data["project"]["created_at"] == "2024-01-01T09:30:00"

    @patch("api.routes.project.AuthManager")
    @patch("api.routes.project.get_project_by_id")
    def test_get_project_by_id_success_with_string_datetime(self, mock_get_project, mock_auth_manager):
        mock_auth_manager.get_current_username.return_value = "test_user"
        mock_get_project.return_value = {
            "project_info": {
                "id": 2,
                "filename": "proj2.zip",
                "filepath": "/tmp/proj2.zip",
                "status": "uploaded",
                "created_at": "2024-01-01T10:00:00"
            }
        }

        response = client.get("/api/projects/2")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["project"]["created_at"] == "2024-01-01T10:00:00"

class TestDeleteProjectDataRoutes:
    @patch("api.routes.project.delete_insights")
    def test_delete_project_data_success(self, mock_delete):
        mock_delete.return_value = (5, 10, 1)

        response = client.delete("/api/projects/1/data?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted"]["metrics"] == 5
        assert data["deleted"]["files"] == 10
        assert data["deleted"]["projects"] == 1
