import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Make src importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import portfolio.portfolio_manager as pm  # noqa: E402


def _ranked_project(pid=1, name="proj.zip", score=9.5):
    return {"project_id": pid, "filename": name, "score": score, "analysis": {}}


def _summary(pid=1, name="proj.zip"):
    return {
        "project_info": {"filename": name, "created_at": "2024-01-01"},
        "languages": {"primary_language": "Python", "languages": ["Python", "JS"]},
        "collaboration_analysis": {"collaboration_level": "Team", "analysis": "collab"},
        "time_analysis": {"duration_days": 10, "intensity": "Medium-term (≤1 month)"},
        "code_analysis": {
            "oop_principles_summary": {"abstraction": {"count": 1}, "encapsulation": {"count": 0}, "polymorphism": {"count": 0}, "inheritance": {"count": 0}},
            "code_quality_summary": {"average_quality_score": 80},
            "optimization_summary": [{"type": "caching"}],
            "data_structure_summary": {"hash_map": 1},
            "complexity_summary": {},
        },
    }


def _key_metrics():
    return {
        "totals": {"files": 2, "lines": 120},
        "by_language": [{"language": "Python"}],
        "by_activity": {"code": {"count": 1, "bytes": 50, "pct_count": 60, "pct_bytes": 70, "pct_score": 80}},
        "timeline": {"start": "2024-01-01", "end": "2024-01-02"},
    }


@patch("portfolio.portfolio_manager.ResumeManager")
@patch("portfolio.portfolio_manager.AnalysisRouter")
@patch("portfolio.portfolio_manager.ExternalServicePermission")
@patch("portfolio.portfolio_manager.ConsentStorage")
@patch("portfolio.portfolio_manager.ProjectAnalyzer")
@patch("portfolio.portfolio_manager.ProjectSummarizer")
@patch("portfolio.portfolio_manager.rank_all_projects", return_value=[_ranked_project()])
@patch("portfolio.portfolio_manager.analyze_project_from_db", return_value=_key_metrics())
@patch("portfolio.portfolio_manager.get_file_contents_by_upload_id", return_value=["content"])
@patch("portfolio.portfolio_manager.get_file_statistics", return_value={"total_size_bytes": 2048})
@patch("portfolio.portfolio_manager._identify_authors_from_zip", return_value={"Alice"})
@patch("portfolio.portfolio_manager._extract_common_names_from_filenames", return_value={"Bob"})
@patch("project_summarizer.summarize_project", return_value="Top summary")
def test_generate_portfolio_report_success(
    mock_sum_proj,
    mock_common_names,
    mock_authors,
    mock_file_stats,
    mock_file_contents,
    mock_analyze,
    mock_rank,
    mock_summarizer_cls,
    mock_analyzer_cls,
    mock_consent_cls,
    mock_perm_cls,
    mock_router_cls,
    mock_resume_cls,
):
    """Portfolio report should aggregate project details and skills."""
    mock_summarizer = mock_summarizer_cls.return_value
    mock_summarizer.generate_project_summary.return_value = _summary()

    mock_analyzer = MagicMock()
    mock_analyzer._detect_frameworks_from_files.return_value = ["Django"]
    mock_analyzer._calculate_contribution_metrics.return_value = {
        "code_files": 1,
        "test_files": 1,
        "documentation_files": 0,
        "configuration_files": 0,
        "activity_distribution": {},
    }
    mock_analyzer._extract_skills_from_files.return_value = {"Python", "Django"}
    mock_analyzer_cls.return_value = mock_analyzer

    mock_consent = mock_consent_cls.return_value
    mock_consent.get_consent_status.return_value = {"consent_given": True}

    mock_perm_cls.return_value.has_permission.return_value = True
    mock_router_cls.return_value.get_analysis_strategy.return_value = "external"

    manager = pm.PortfolioManager(user_name="user1")
    report = manager.generate_portfolio_report(top_n=1)

    assert "error" not in report
    assert report["summary"]["total_projects"] == 1
    assert report["skills"]["languages"] == ["JS","Python"]
    assert report["skills"]["frameworks"] == ["Django"]
    assert report["projects"][0]["name"] == "proj.zip"
    assert report["projects"][0]["has_tests"] is True
    assert report["projects"][0]["rank_score"] == 9.5


@patch("portfolio.portfolio_manager.rank_all_projects", return_value=[])
def test_generate_portfolio_report_no_projects(mock_rank):
    """Return error when no projects are ranked."""
    manager = pm.PortfolioManager()
    report = manager.generate_portfolio_report()
    assert report["error"] == "No projects found"


def test_generate_project_summary_text():
    """_generate_project_summary_text should weave metrics into narrative."""
    manager = pm.PortfolioManager()
    summary = {
        "project_info": {"filename": "demo"},
        "languages": {"primary_language": "Python", "languages": ["Python", "Rust"]},
        "collaboration_analysis": {"collaboration_level": "Team"},
        "time_analysis": {"duration_days": 40},
        "code_analysis": {},
    }
    code_analysis = {
        "oop_principles_summary": {"abstraction": {"count": 1}},
        "code_quality_summary": {"average_quality_score": 90},
        "optimization_summary": [{"type": "opt"}],
        "data_structure_summary": {"tree": 1},
    }
    key_metrics = {"totals": {"files": 3, "lines": 150}}
    text = manager._generate_project_summary_text(summary, code_analysis, key_metrics, frameworks=["Flask"])
    assert "Python" in text
    assert "Flask" in text
    assert "150" in text


@patch("portfolio.portfolio_manager.list_projects_chronologically")
@patch("portfolio.portfolio_manager.get_file_contents_by_upload_id")
@patch("portfolio.portfolio_manager.ProjectAnalyzer")
def test_get_chronological_skills(mock_analyzer_cls, mock_file_contents, mock_list_projects):
    """Chronological skills should be ordered by project date."""
    mock_list_projects.return_value = [
        {"id": 1, "filename": "early", "created_at": datetime(2023, 1, 1)},
        {"id": 2, "filename": "late", "created_at": datetime(2024, 1, 1)},
    ]
    mock_file_contents.side_effect = [["content1"], ["content2"]]

    analyzer = MagicMock()
    analyzer._extract_skills_from_files.side_effect = [{"Python"}, {"React"}]
    mock_analyzer_cls.return_value = analyzer

    manager = pm.PortfolioManager()
    skills = manager.get_chronological_skills()

    assert [s["skill"] for s in skills] == ["Python", "React"]
    assert skills[0]["first_project"] == "early"
