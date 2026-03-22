import os
import sys
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from api.main import app


client = TestClient(app)


class TestAuthEndpoints:
    @patch("api.routes.auth.get_user_by_username")
    @patch("api.routes.auth.AuthManager.login")
    def test_login_success(self, mock_auth_login, mock_get_user):
        mock_auth_login.return_value = {
            "success": True,
            "message": "Login successful",
            "user_info": {
                "user_id": 999,
                "user_name": "test_user",
                "create_time": None,
                "last_login_time": None,
                "is_login": True,
            },
        }

        mock_get_user.return_value = {
            "user_id": 1,
            "user_name": "test_user",
            "create_time": None,
            "last_login_time": None,
            "is_login": True,
        }

        response = client.post(
            "/api/auth/login",
            json={"username": "test_user", "password": "secret"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Login successful"
        assert data["user"]["user_id"] == 1
        assert data["user"]["user_name"] == "test_user"
        assert data["user"]["is_login"] is True

    def test_login_missing_username(self):
        response = client.post("/api/auth/login", json={"username": "", "password": "secret"})

        assert response.status_code == 422

    @patch('api.routes.auth.AuthManager.register')
    def test_register_success(self, mock_register):
        mock_register.return_value = {"success": True, "message": "ok", "user_id": 10}

        response = client.post("/api/auth/register", json={"username": "new_user", "password": "secret1"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user_id"] == 10

    def test_register_invalid_password(self):
        response = client.post("/api/auth/register", json={"username": "new_user", "password": "123"})

        assert response.status_code == 422

    @patch('api.routes.auth.logout_user')
    @patch('api.routes.auth.get_user_by_username')
    def test_logout_success(self, mock_get_user, mock_logout):
        mock_get_user.return_value = {"user_name": "test_user", "is_login": True}
        mock_logout.return_value = True

        response = client.post("/api/auth/logout", json={"username": "test_user"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch('api.routes.auth.get_user_by_username')
    def test_get_current_user_success(self, mock_get_user):
        mock_get_user.return_value = {"user_id": 1, "user_name": "test_user", "is_login": True}

        response = client.get("/api/auth/me?username=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user"]["user_name"] == "test_user"


class TestConsentEndpoint:
    @patch('api.routes.consent.ConsentStorage.get_consent_status')
    @patch('api.routes.consent.ConsentStorage.store_consent')
    def test_privacy_consent_success(self, mock_store, mock_get_status):
        mock_store.return_value = True
        mock_get_status.return_value = {"consent_given": True}

        response = client.post("/api/privacy-consent", json={"consent_given": True, "user_name": "test_user"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user_name"] == "test_user"

class TestSettingsRootAndAccount:
    @patch('api.dependencies.get_user_by_username')
    @patch('api.routes.settings.ConsentStorage.get_consent_status')
    @patch('api.routes.settings.get_user_git_username')
    def test_get_all_settings(self, mock_get_git, mock_get_consent, mock_get_user):
        mock_get_user.return_value = {
            "user_id": 1,
            "user_name": "test_user",
            "is_login": True,
        }
        mock_get_consent.return_value = {"consent_given": True}
        mock_get_git.return_value = "git_user"

        response = client.get("/api/settings?username=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["account"]["user_name"] == "test_user"
        assert data["general"]["git_username"] == "git_user"

    @patch('api.dependencies.get_user_by_username')
    def test_post_account_settings_placeholder(self, mock_get_user):
        mock_get_user.return_value = {
            "user_id": 1,
            "user_name": "test_user",
            "is_login": True,
        }

        response = client.post("/api/settings/account?username=test_user", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "coming soon" in data["message"].lower()


class TestPreferencesEndpoint:
    @patch('api.routes.project.update_user_git_username')
    @patch('api.routes.project.get_user_git_username')
    def test_update_preferences(self, mock_get_git, mock_update_git):
        mock_get_git.return_value = "new_git"

        response = client.post("/api/preferences?user_name=test_user", json={"git_username": "new_git"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["git_username"] == "new_git"
        mock_update_git.assert_called_once_with("test_user", "new_git")


