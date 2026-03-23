import base64
import os
import sys
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from api.main import app


client = TestClient(app)


class TestProjectThumbnailEndpoints:
    @patch('api.routes.project.get_project_by_id')
    @patch('api.routes.project.add_thumbnail_bytes_to_project')
    def test_upload_thumbnail_success(self, mock_add_thumbnail, mock_get_project):
        mock_get_project.return_value = {"id": 123}
        mock_add_thumbnail.return_value = MagicMock(success=True, to_dict=lambda: {"success": True})

        png_bytes = b"\x89PNG\r\n\x1a\n" + b"0" * 10
        response = client.post(
            "/api/projects/123/thumbnail",
            files={"file": ("thumb.png", png_bytes, "image/png")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch('api.routes.project.get_project_by_id')
    def test_get_thumbnail_not_found(self, mock_get_project):
        mock_get_project.return_value = None

        response = client.get("/api/projects/123/thumbnail")

        assert response.status_code == 404

    @patch('api.routes.project.get_project_by_id')
    @patch('api.routes.project.with_db_cursor')
    def test_get_thumbnail_none(self, mock_with_cursor, mock_get_project):
        mock_get_project.return_value = {"id": 123}

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (None,)
        mock_with_cursor.return_value.__enter__.return_value = mock_cursor

        response = client.get("/api/projects/123/thumbnail")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["has_thumbnail"] is False

    @patch('api.routes.project.get_project_by_id')
    @patch('api.routes.project.with_db_cursor')
    def test_get_thumbnail_success(self, mock_with_cursor, mock_get_project):
        mock_get_project.return_value = {"id": 123}

        png_bytes = b"\x89PNG\r\n\x1a\n" + b"0" * 10
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (png_bytes,)
        mock_with_cursor.return_value.__enter__.return_value = mock_cursor

        response = client.get("/api/projects/123/thumbnail")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["has_thumbnail"] is True
        assert data["thumbnail_data"].startswith("data:image/png;base64,")


class TestProjectAnalysisEndpoints:
    @patch('project_analyzer.ProjectAnalyzer')
    def test_analyze_project_success(self, mock_analyzer_cls):
        mock_instance = mock_analyzer_cls.return_value
        mock_instance.analyze_uploaded_project.return_value = {"success": True, "metrics": {"loc": 10}}

        response = client.post("/api/projects/123/analyze?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["analysis"]["success"] is True

    @patch("api.routes.project._ensure_llm_allowed")
    @patch('project_manager.get_project_by_id')
    def test_analyze_gemini_project_not_found(self, mock_get_project, mock_llm_guard):
        mock_get_project.return_value = None
        mock_llm_guard.return_value = "test_user"

        response = client.post("/api/projects/123/analyze-gemini")

        assert response.status_code == 404

    @patch("api.routes.project._ensure_llm_allowed")
    @patch('analysis.gemini_analyzer.GeminiAnalyzer')
    @patch('project_analyzer.ProjectAnalyzer')
    @patch('config.db_config.with_db_cursor')
    @patch('project_manager.get_project_by_id')
    def test_analyze_gemini_success(self, mock_get_project, mock_with_cursor, mock_pa_cls, mock_ga_cls, mock_llm_guard):
        mock_get_project.return_value = {"project_info": {"filename": "proj.zip"}}

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("file.py", "file.py", ".py", 10, "print('x')", "text/plain", False)
        ]
        mock_with_cursor.return_value.__enter__.return_value = mock_cursor

        pa_instance = mock_pa_cls.return_value
        pa_instance._analyze_languages_from_files.return_value = {"primary_language": "Python", "detected_languages": ["Python"]}
        pa_instance._detect_frameworks_from_files.return_value = ["FastAPI"]

        ga_instance = mock_ga_cls.return_value
        ga_instance.analyze_project.return_value = {"success": True, "summary": "ok"}
        mock_llm_guard.return_value = "test_user"

        response = client.post("/api/projects/123/analyze-gemini?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["analysis"]["success"] is True


class TestProjectQuickSummaryEndpoint:
    @patch("api.routes.project._ensure_llm_allowed")
    @patch('analysis.gemini_analyzer.GeminiAnalyzer')
    @patch('config.db_config.with_db_cursor')
    @patch('project_manager.get_project_by_id')
    def test_quick_summary_success(self, mock_get_project, mock_with_cursor, mock_ga_cls, mock_llm_guard):
        mock_get_project.return_value = {"project_info": {"filename": "proj.zip"}}
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("file.py", "file.py", ".py", 10, "print('x')", "text/plain", False)
        ]
        mock_with_cursor.return_value.__enter__.return_value = mock_cursor

        ga_instance = mock_ga_cls.return_value
        ga_instance.get_quick_summary.return_value = "summary"
        mock_llm_guard.return_value = "test_user"

        response = client.post("/api/projects/123/quick-summary?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["summary"] == "summary"

    @patch("api.routes.project._ensure_llm_allowed")
    @patch('project_manager.get_project_by_id')
    def test_quick_summary_project_not_found(self, mock_get_project, mock_llm_guard):
        mock_get_project.return_value = None
        mock_llm_guard.return_value = "test_user"

        response = client.post("/api/projects/123/quick-summary?user_name=test_user")

        assert response.status_code == 404


class TestProjectRankingEndpoints:
    @patch('api.routes.project.save_rankings_with_summaries')
    @patch('api.routes.project.rank_all_projects')
    def test_rank_projects(self, mock_rank_all, mock_save):
        mock_rank_all.return_value = [
            {"project_id": 1, "score": 0.9},
            {"project_id": 2, "score": 0.8},
        ]

        response = client.post("/api/projects/rank?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestProjectReplayEndpoint:
    @patch("api.routes.project.AuthManager")
    @patch("api.routes.project.get_project_by_id")
    @patch("api.routes.project.with_db_cursor")
    def test_project_replay_success(self, mock_with_cursor, mock_get_project, mock_auth):
        mock_auth.get_current_username.return_value = "test_user"
        mock_get_project.return_value = {"project_info": {"id": 123}}

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("src/main.py", ".py", 200, "2026-02-01 00:00:00", "2026-02-01 00:00:00"),
            ("tests/test_main.py", ".py", 100, "2026-02-02 00:00:00", "2026-02-02 00:00:00"),
            ("README.md", ".md", 80, "2026-02-03 00:00:00", "2026-02-03 00:00:00"),
        ]
        mock_with_cursor.return_value.__enter__.return_value = mock_cursor

        response = client.get("/api/projects/123/replay?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["project_id"] == 123
        assert len(data["events"]) >= 1
        assert "project_narrative" in data
        assert "interview_mode" in data
        assert isinstance(data["interview_mode"]["talking_points"], list)
        assert len(data["interview_mode"]["talking_points"]) >= 1
        tp = data["interview_mode"]["talking_points"][0]
        assert "question" in tp or "insight" in tp

    @patch("api.routes.project.AuthManager")
    def test_project_replay_requires_auth(self, mock_auth):
        mock_auth.get_current_username.return_value = None

        response = client.get("/api/projects/123/replay?user_name=test_user")
        assert response.status_code == 401

    @patch("api.routes.project.AuthManager")
    def test_project_replay_user_mismatch(self, mock_auth):
        mock_auth.get_current_username.return_value = "alice"

        response = client.get("/api/projects/123/replay?user_name=bob")
        assert response.status_code == 403

    @patch("api.routes.project.enrich_replay_with_ai")
    @patch("api.routes.project._ensure_llm_allowed")
    @patch("api.routes.project.AuthManager")
    @patch("api.routes.project.get_project_by_id")
    @patch("api.routes.project.with_db_cursor")
    def test_project_replay_use_ai(
        self, mock_with_cursor, mock_get_project, mock_auth, mock_llm, mock_enrich
    ):
        mock_auth.get_current_username.return_value = "test_user"
        mock_get_project.return_value = {"project_info": {"id": 123, "filename": "myapp.zip"}}
        mock_llm.return_value = "test_user"

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("src/main.py", ".py", 200, "2026-02-01 00:00:00", "2026-02-01 00:00:00"),
            ("tests/test_main.py", ".py", 100, "2026-02-02 00:00:00", "2026-02-02 00:00:00"),
        ]
        mock_with_cursor.return_value.__enter__.return_value = mock_cursor

        base_replay = {"events": [{}], "project_narrative": "Foo", "interview_mode": {"talking_points": []}}
        mock_enrich.return_value = {**base_replay, "ai_enriched": True}

        response = client.get("/api/projects/123/replay?user_name=test_user&use_ai=true")

        assert response.status_code == 200
        mock_llm.assert_called_once()
        mock_enrich.assert_called_once()
        data = response.json()
        assert data.get("ai_enriched") is True


class TestProjectRankingMoreEndpoints:
    @patch('api.routes.project.summarize_project')
    @patch('api.routes.project.rank_all_projects')
    def test_rank_top3(self, mock_rank_all, mock_summarize):
        mock_rank_all.return_value = [
            {"project_id": 1, "filename": "p1.zip", "score": 0.9},
            {"project_id": 2, "filename": "p2.zip", "score": 0.8},
            {"project_id": 3, "filename": "p3.zip", "score": 0.7},
        ]
        mock_summarize.return_value = "Generated summary text"

        response = client.post("/api/projects/rank-top3?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["top3"]) == 3
        for item in data["top3"]:
            assert "project_id" in item
            assert "filename" in item
            assert "score" in item
            assert "summary" in item
            assert item["summary"] == "Generated summary text"
        assert mock_summarize.call_count == 3

    @patch('api.routes.project.AuthManager')
    @patch('api.routes.project.get_stored_rankings')
    def test_get_rankings(self, mock_get_rankings, mock_auth_manager):
        mock_auth_manager.get_current_username.return_value = "test_user"
        mock_get_rankings.return_value = [{"project_id": 1, "rank": 1}]

        response = client.get("/api/projects/rankings")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["rankings"] == [{"project_id": 1, "rank": 1}]

    @patch("api.routes.project._ensure_llm_allowed")
    @patch('api.routes.project.rank_projects_with_gemini')
    def test_rank_projects_gemini(self, mock_rank_gemini, mock_llm_guard):
        mock_rank_gemini.return_value = {"success": True, "ranked": [1, 2, 3]}
        mock_llm_guard.return_value = "test_user"

        response = client.post("/api/projects/rank-gemini?user_name=test_user")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
