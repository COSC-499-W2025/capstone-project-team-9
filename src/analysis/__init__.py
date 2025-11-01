from .analysis_router import AnalysisRouter

__all__ = ['AnalysisRouter']

# Lazy imports for ranking functionality
def rank_all_projects():
    from . import project_ranking
    return project_ranking.rank_all_projects()

def display_rankings(ranked_projects):
    from . import project_ranking
    return project_ranking.display_rankings(ranked_projects)

def calculate_project_score(analysis_data):
    from . import project_ranking
    return project_ranking.calculate_project_score(analysis_data)

def rank_local_project(project_path):
    from . import project_ranking
    return project_ranking.rank_local_project(project_path)
