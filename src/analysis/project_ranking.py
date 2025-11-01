"""
Project Ranking Module
Ranks projects using database Key Metrics that are pulled rom uploaded files and file contents from other features
"""
from typing import Dict, List, Any
from config.db_config import get_connection
from analysis.key_metrics import analyze_project_from_db
import os


def calculate_project_score(analysis_data: Dict[str, Any]) -> float:
    """
    this is a function to calculate the score of a project based on the analysis data
    the score is calculated based on the following factors:
    - total lines of code
    - number of files
    - number of languages
    - number of frameworks
    - number of skills
    - number of tests
    - number of documentation
    - number of configuration
    - number of code files
    - number of document files
    """
    score = 0.0
    
    # Database key_metrics result
    if "by_activity" in analysis_data:
        # Calculate score based on activity types (count and bytes, not pre-calculated score)
        # Weights based on activity type importance (matching activity_classifier weights)
        activity_weights = {"code": 3, "doc": 1.5, "data": 2, "media": 1, "config": 1, "other": 1}
        
        for activity_type, data in analysis_data["by_activity"].items():
            # Use count and bytes instead of pre-calculated score
            file_count = data.get("count", 0)
            total_bytes = data.get("bytes", 0)
            weight = activity_weights.get(activity_type, 1)
            
            # File count contribution
            score += file_count * weight * 10
            
            # Size contribution (normalized, smaller impact than count)
            score += total_bytes / 1000 * weight * 0.1

        # Overall size/complexity signal
        total_lines = analysis_data.get("totals", {}).get("lines", 0)
        score += total_lines * 0.1

        # Language diversity bonus
        by_language = analysis_data.get("by_language", [])
        score += len(by_language) * 10

    # Backward-compatible support if a local analyzer dict is passed
    elif "structure" in analysis_data:
        metrics = analysis_data.get("metrics", {})
        structure = analysis_data.get("structure", {})
        skills = analysis_data.get("skills", [])
        
        # Lines of code bonus
        total_loc = metrics.get("total_lines_of_code", 0)
        score += total_loc * 0.1
        
        # Structure bonuses
        if structure.get("has_tests"):
            score += 50  # Tests are important!
        if structure.get("has_docs"):
            score += 30  # Documentation is valuable
        if structure.get("has_config"):
            score += 20  # Configuration shows maturity
        
        # Skills diversity
        score += len(skills) * 15
        
        # Framework detection bonus
        frameworks = analysis_data.get("frameworks", [])
        score += len(frameworks) * 25
        
        # Code file ratio (more code = better for portfolio)
        code_files = metrics.get("code_files", 0)
        total_files = metrics.get("code_files", 0) + metrics.get("document_files", 0) + \
                      metrics.get("design_files", 0) + metrics.get("other_files", 0)
        if total_files > 0:
            code_ratio = code_files / total_files
            score += code_ratio * 100
    
    return round(score, 2)


def rank_all_projects() -> List[Dict[str, Any]]:
    """
    Rank all uploaded projects in the database by composite score using key_metrics.
    """
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT id, filename, created_at FROM uploaded_files")
            projects = cur.fetchall()

        if not projects:
            return []

        ranked_projects: List[Dict[str, Any]] = []
        for project_id, filename, created_at in projects:
            try:
                analysis = analyze_project_from_db(project_id)
                score = calculate_project_score(analysis)
                ranked_projects.append({
                    "project_id": project_id,
                    "filename": filename,
                    "created_at": created_at,
                    "score": score,
                    "analysis": analysis,
                })
            except Exception as e:
                print(f"Error analyzing project {project_id}: {e}")
                continue

        ranked_projects.sort(key=lambda x: x["score"], reverse=True)
        return ranked_projects
    except Exception as e:
        print(f"Error ranking projects: {e}")
        return []

def rank_local_project(project_path: str) -> Dict[str, Any]:
    """Deprecated: local ranking disabled; use database key metrics instead."""
    raise NotImplementedError("Local ranking disabled; use key-metrics-based ranking from DB.")



def display_rankings(ranked_projects: List[Dict[str, Any]]):
    """
    Display ranked projects in a readable format.
    
    Args:
        ranked_projects: List of ranked project dictionaries
    """
    if not ranked_projects:
        print("\nNo projects to rank.")
        return
    
    print("\n" + "="*80)
    print("PROJECT RANKINGS")
    print("="*80)
    print(f"{'Rank':<6} {'Score':<10} {'Filename':<40} {'Project ID':<12}")
    print("-"*80)
    
    for i, project in enumerate(ranked_projects, 1):
        filename = project["filename"][:38] + ".." if len(project["filename"]) > 40 else project["filename"]
        print(f"{i:<6} {project['score']:<10} {filename:<40} {project['project_id']:<12}")
    
    print("="*80)
    
    # Show top project detailed analysis
    if len(ranked_projects) >= 1:
        print("\nTOP PROJECT ANALYSIS:")
        print("-"*80)
        top_project = ranked_projects[0]
        
        # Key-metrics summary
        if "by_activity" in top_project["analysis"]:
            print(f"Files: {top_project['analysis']['totals']['files']}")
            print(f"Lines: {top_project['analysis']['totals']['lines']}")
            print("\nBy Activity Type:")
            for activity, data in sorted(top_project["analysis"]["by_activity"].items(), 
                                        key=lambda x: x[1].get("count", 0), reverse=True):
                print(f"  {activity}: {data['count']} files, {data['bytes']} bytes")
        # Back-compat for any local dicts
        elif "structure" in top_project["analysis"]:
            metrics = top_project["analysis"].get("metrics", {})
            structure = top_project["analysis"].get("structure", {})
            print(f"Total LOC: {metrics.get('total_lines_of_code', 0)}")
            print(f"Languages: {', '.join(top_project['analysis'].get('languages', {}).get('languages_detected', [])[:5])}")
            print(f"Frameworks: {', '.join(top_project['analysis'].get('frameworks', [])[:5])}")
            print(f"Skills: {len(top_project['analysis'].get('skills', []))} detected")
            if structure.get("has_tests"):
                print("Has tests")
            if structure.get("has_docs"):
                print("Has documentation")
            if structure.get("has_config"):
                print("Has configuration")

