"""
Project Ranking Module
Ranks projects using database Key Metrics that are pulled rom uploaded files and file contents from other features
"""
from typing import Dict, List, Any, Optional
from config.db_config import get_connection
from analysis.key_metrics import analyze_project_from_db
from project_summarizer import summarize_project
from analysis.ranking_storage import save_rankings_to_db, get_stored_ranking_by_project_id, get_stored_rankings
from analysis.local_analyzer import LocalAnalyzer
from parsing.file_contents_manager import get_file_contents_by_upload_id
import os


def _perform_deep_code_analysis(project_id: int) -> Dict[str, Any]:
    """
    Perform deep code analysis on a project using file contents from database.
    
    Args:
        project_id: The project ID to analyze
        
    Returns:
        dict: Aggregated deep code analysis results
    """
    try:
        file_contents = get_file_contents_by_upload_id(project_id)
        if not file_contents:
            return {}
        
        local_analyzer = LocalAnalyzer()
        deep_analysis = local_analyzer.analyze_files_from_db(file_contents)
        return deep_analysis
    except Exception as e:
        print(f"Warning: Deep code analysis failed for project {project_id}: {e}")
        return {}


def calculate_project_score(analysis_data: Dict[str, Any], project_id: Optional[int] = None) -> float:
    """
    Calculate the score of a project based on the analysis data.
    Score is normalized to be out of 100 for easier understanding.
    
    Args:
        analysis_data: Analysis data from key_metrics or local analyzer
        project_id: Optional project ID for deep code analysis
        
    Returns:
        float: Project score out of 100
    """
    base_score = 0.0
    deep_analysis_score = 0.0
    
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
            base_score += file_count * weight * 10
            
            # Size contribution (normalized, smaller impact than count)
            base_score += total_bytes / 1000 * weight * 0.1

        # Overall size/complexity signal
        total_lines = analysis_data.get("totals", {}).get("lines", 0)
        base_score += total_lines * 0.1

        # Language diversity bonus
        by_language = analysis_data.get("by_language", [])
        base_score += len(by_language) * 10

    # Backward-compatible support if a local analyzer dict is passed
    elif "structure" in analysis_data:
        metrics = analysis_data.get("metrics", {})
        structure = analysis_data.get("structure", {})
        skills = analysis_data.get("skills", [])
        
        # Lines of code bonus
        total_loc = metrics.get("total_lines_of_code", 0)
        base_score += total_loc * 0.1
        
        # Structure bonuses
        if structure.get("has_tests"):
            base_score += 50  # Tests are important!
        if structure.get("has_docs"):
            base_score += 30  # Documentation is valuable
        if structure.get("has_config"):
            base_score += 20  # Configuration shows maturity
        
        # Skills diversity
        base_score += len(skills) * 15
        
        # Framework detection bonus
        frameworks = analysis_data.get("frameworks", [])
        base_score += len(frameworks) * 25
        
        # Code file ratio (more code = better for portfolio)
        code_files = metrics.get("code_files", 0)
        total_files = metrics.get("code_files", 0) + metrics.get("document_files", 0) + \
                      metrics.get("design_files", 0) + metrics.get("other_files", 0)
        if total_files > 0:
            code_ratio = code_files / total_files
            base_score += code_ratio * 100
    
    # Perform deep code analysis if project_id is provided
    if project_id is not None:
        deep_analysis = _perform_deep_code_analysis(project_id)
        if deep_analysis:
            # OOP Principles scoring (max 15 points)
            oop_summary = deep_analysis.get("oop_principles_summary", {})
            oop_score = 0.0
            for principle in ["abstraction", "encapsulation", "polymorphism", "inheritance"]:
                principle_data = oop_summary.get(principle, {})
                count = principle_data.get("count", 0) if isinstance(principle_data, dict) else 0
                oop_score += min(count * 1.5, 3.75)  # Cap each principle at 3.75 points
            deep_analysis_score += min(oop_score, 15.0)
            
            # Data Structures scoring (max 10 points)
            ds_summary = deep_analysis.get("data_structure_summary", {})
            if isinstance(ds_summary, dict):
                total_structures = sum(ds_summary.values())
                deep_analysis_score += min(total_structures * 0.5, 10.0)
            
            # Complexity awareness scoring (max 10 points)
            complexity_summary = deep_analysis.get("complexity_summary", {})
            complexity_score = 0.0
            if complexity_summary.get("complexity_awareness", False):
                complexity_score += 5.0
            nested_loops = complexity_summary.get("nested_loops", 0)
            recursive_functions = complexity_summary.get("recursive_functions", 0)
            complexity_score += min((nested_loops + recursive_functions) * 0.5, 5.0)
            deep_analysis_score += min(complexity_score, 10.0)
            
            # Optimization evidence scoring (max 10 points)
            optimization_summary = deep_analysis.get("optimization_summary", [])
            if optimization_summary:
                deep_analysis_score += min(len(optimization_summary) * 2.5, 10.0)
            
            # Code quality scoring (max 15 points)
            quality_summary = deep_analysis.get("code_quality_summary", {})
            avg_quality = quality_summary.get("average_quality_score", 0)
            if avg_quality > 0:
                # Normalize quality score (0-100) to 0-15 points
                deep_analysis_score += min(avg_quality * 0.15, 15.0)
            
            # Strengths bonus (max 5 points)
            strengths = quality_summary.get("strengths", [])
            deep_analysis_score += min(len(strengths) * 1.0, 5.0)
    
    # Normalize to 0-100 scale
    # Base score can vary widely, so we normalize it separately
    # Deep analysis score is already capped at ~55 points, so we treat it as a percentage
    
    # Normalize base score (typical range: 0-500 for small projects, up to 2000+ for large projects)
    # We'll use a more dynamic approach: normalize base score to 0-60 points
    max_base_score = 2000.0  # Reasonable maximum for base score normalization
    normalized_base = min(60.0, (base_score / max_base_score) * 60.0)
    
    # Deep analysis score is already in a reasonable range (0-55), normalize to 0-40 points
    # This gives deep analysis 40% weight and base metrics 60% weight
    normalized_deep = min(40.0, (deep_analysis_score / 55.0) * 40.0) if deep_analysis_score > 0 else 0.0
    
    # Combine normalized scores
    total_normalized_score = normalized_base + normalized_deep
    
    # Ensure score is between 0 and 100
    total_normalized_score = max(0.0, min(100.0, total_normalized_score))
    
    return round(total_normalized_score, 2)


def rank_all_projects() -> List[Dict[str, Any]]:
    """
    Rank all uploaded projects in the database by composite score using key_metrics.

    NOTE: This function intentionally uses ONLY key_metrics-based analysis and does
    NOT trigger deep LocalAnalyzer analysis or LLM summaries to keep the CLI fast.
    """
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT id, filename, created_at FROM uploaded_files")
            projects = cur.fetchall()

        if not projects:
            return []

        # Get all stored rankings to check for existing scores
        stored_rankings = get_stored_rankings()
        stored_scores = {r['project_id']: r['score'] for r in stored_rankings}

        ranked_projects: List[Dict[str, Any]] = []
        for project_id, filename, created_at in projects:
            try:
                # Use stored score if available, otherwise calculate
                if project_id in stored_scores:
                    score = stored_scores[project_id]
                    # Still need analysis data for other purposes, but use stored score
                    # analysis = analyze_project_from_db(project_id, silent=True)
                    analysis = None
                else:
                    analysis = analyze_project_from_db(project_id, silent=True)
                    # score = calculate_project_score(analysis, project_id=project_id)
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
    Display ranked projects in a simple format showing only project names and scores.
    
    Args:
        ranked_projects: List of ranked project dictionaries
    """
    if not ranked_projects:
        print("\nNo projects to rank.")
        return
    
    print("\n" + "="*80)
    print("PROJECT RANKINGS")
    print("="*80)
    print(f"{'Rank':<6} {'Score':<10} {'Project Name':<60}")
    print("-"*80)
    
    for i, project in enumerate(ranked_projects, 1):
        filename = project["filename"][:58] + ".." if len(project["filename"]) > 60 else project["filename"]
        print(f"{i:<6} {project['score']:<10} {filename:<60}")
    
    print("="*80)


def rank_and_summarize_top_projects() -> None:
    """
    Rank all projects and summarize the top 3 projects (without displaying rankings).
    """
    print("\nRanking all projects...")
    ranked_projects = rank_all_projects()
    
    if not ranked_projects:
        print("\nNo projects to rank.")
        return
    
    # Summarize top 3 projects
    top_count = min(3, len(ranked_projects))
    if top_count > 0:
        print(f"\n{'='*80}")
        print(f"SUMMARIZING TOP {top_count} PROJECTS")
        print("="*80)
        
        for i in range(top_count):
            project = ranked_projects[i]
            project_id = project['project_id']
            print(f"\n{'='*80}")
            print(f"TOP {i+1} PROJECT: {project['filename']} (Score: {project['score']})")
            print("="*80)
            
            # Check if summary exists in database
            stored_ranking = get_stored_ranking_by_project_id(project_id)
            if stored_ranking and stored_ranking.get('summary'):
                print("\nUsing stored summary from database...")
                print(stored_ranking['summary'])
            else:
                print("\nNo stored summary found in database.")
                print("(On-the-fly summary generation is disabled in the CLI to keep it responsive.)")
            
            if i < top_count - 1:
                print("\n" + "-"*80)


def save_rankings_with_summaries(ranked_projects: List[Dict[str, Any]], generate_summaries: bool = True) -> bool:
    """
    Save ranked projects and their summaries to the database.

    """
    if not ranked_projects:
        print("\nNo projects to save.")
        return False
    
    summaries = {}
    
    if generate_summaries:
        print("\nProcessing summaries for all projects (using stored summaries only)...")
        for i, project in enumerate(ranked_projects, 1):
            project_id = project['project_id']
            filename = project['filename']
            
            # Check if summary exists in database first
            stored_ranking = get_stored_ranking_by_project_id(project_id)
            if stored_ranking and stored_ranking.get('summary'):
                print(f"  [{i}/{len(ranked_projects)}] Using stored summary for: {filename}")
                summaries[project_id] = stored_ranking['summary']
            else:
                print(f"  [{i}/{len(ranked_projects)}] No stored summary for: {filename}")
    
    print("\nSaving rankings and summaries to database...")
    success = save_rankings_to_db(ranked_projects, summaries if summaries else None)
    
    if success:
        print(f"\nSuccessfully saved {len(ranked_projects)} project rankings to database.")
        if summaries:
            print(f"Successfully saved {len(summaries)} project summaries to database.")
    else:
        print("\nFailed to save rankings to database.")
    
    return success

