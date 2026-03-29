import pytest
from src.common.utils import clean_project_title

class TestCleanProjectTitle:
    """Test suite for the clean_project_title utility function."""

    def test_clean_project_title_empty_string(self):
        """Test that an empty string returns the default 'Unknown Project'."""
        assert clean_project_title("") == "Unknown Project"

    def test_clean_project_title_none(self):
        """Test that passing None returns the default 'Unknown Project'."""
        assert clean_project_title(None) == "Unknown Project"

    def test_clean_project_title_standard_repo_names(self):
        """Test standard repository names get properly title-cased and hyphens removed."""
        # Assuming the utility replaces hyphens/underscores with spaces and applies title casing
        assert clean_project_title("capstone-project") == "Capstone Project"
        assert clean_project_title("machine_learning_course") == "Machine Learning Course"

    def test_clean_project_title_removes_suffixes(self):
        """Test that common repository suffixes (-main, -master) are stripped."""
        assert clean_project_title("particle-astronaut-main") == "Particle Astronaut"
        assert clean_project_title("flask-api-master") == "Flask Api"

    def test_clean_project_title_removes_file_extensions(self):
        assert clean_project_title("data-analysis.zip") == "Data Analysis"

    def test_clean_project_title_combined_noise(self):
        """Test names with both extensions and branch suffixes."""
        assert clean_project_title("capstone-project-team-9-main.zip") == "Capstone Project Team 9"
