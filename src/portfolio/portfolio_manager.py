"""
Portfolio Manager Module

Generates analytical portfolio report according to Milestone 1 specifications.
Uses ONLY existing functions from the codebase - no new analysis logic.
"""

from datetime import datetime
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict
from project_manager import get_project_by_id, list_projects_chronologically
from project_summarizer import ProjectSummarizer
from analysis.project_ranking import rank_all_projects
from analysis.key_metrics import analyze_project_from_db
from analysis.ranking_storage import get_stored_rankings, get_stored_ranking_by_project_id
from project_analyzer import ProjectAnalyzer
from parsing.file_contents_manager import get_file_contents_by_upload_id, get_file_statistics
from collaborative.identify_projects import _identify_authors_from_zip, _compute_collab_score, _extract_common_names_from_filenames, _count_git_files, _detect_team_structure
from consent.consent_storage import ConsentStorage
from external_services.permission_manager import ExternalServicePermission
from analysis.analysis_router import AnalysisRouter
from resume.resume_manager import ResumeManager
import json


class PortfolioManager:
    """Manages portfolio report generation using existing analysis functions."""
    
    def __init__(self, user_id: str = None):
        """
        Initialize portfolio manager.
        
        Args:
            user_id: User identifier. If None, uses current logged-in user.
        """
        # Get current user if not specified
        if user_id is None:
            try:
                from account.user_manager import AuthManager
                user_id = AuthManager.get_current_username() or 'default_user'
            except Exception:
                user_id = 'default_user'
        
        self.user_id = user_id
        self.summarizer = ProjectSummarizer()
        self.project_analyzer = ProjectAnalyzer(user_id)
        self.consent_storage = ConsentStorage()
        self.permission_manager = ExternalServicePermission(user_id)
        self.analysis_router = AnalysisRouter(user_id)
        self.resume_manager = ResumeManager()
    
    def generate_portfolio_report(self, top_n: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate analytical portfolio report according to Milestone 1 specifications.
        Uses ONLY existing functions - no new analysis logic.
        
        Args:
            top_n: If specified, only include top N projects by rank
            
        Returns:
            Dictionary containing structured portfolio report
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # Get consent and privacy information using existing functions
            consent_status = self.consent_storage.get_consent_status(self.user_id)
            user_consent = consent_status.get('consent_given', False) if consent_status else False
            
            llm_permission = self.permission_manager.has_permission('LLM')
            analysis_strategy = self.analysis_router.get_analysis_strategy('project')
            fallback_used = (analysis_strategy == 'local')
            
            # Get ranked projects using existing ranking function
            ranked_projects = rank_all_projects()
            
            if not ranked_projects:
                return {
                    'error': 'No projects found',
                    'timestamp': timestamp
                }
            
            # Filter by top_n if specified
            if top_n:
                ranked_projects = ranked_projects[:top_n]
            
            # Process each project using existing functions
            projects_data = {}
            ordered_project_names = []
            top_summaries = []
            
            for rank_idx, ranked_project in enumerate(ranked_projects, 1):
                project_id = ranked_project['project_id']
                project_name = ranked_project['filename']
                project_score = ranked_project.get('score', 0)
                project_analysis = ranked_project.get('analysis', {})
                
                try:
                    # Get project summary using existing ProjectSummarizer
                    summary = self.summarizer.generate_project_summary(project_id)
                    
                    if 'error' in summary:
                        continue
                    
                    # Use key_metrics from ranked project if available, otherwise fetch
                    if project_analysis and 'totals' in project_analysis:
                        key_metrics = project_analysis
                    else:
                        key_metrics = analyze_project_from_db(project_id, silent=True)
                    
                    # Get file contents and statistics using existing functions
                    file_contents = get_file_contents_by_upload_id(project_id)
                    file_stats = get_file_statistics(project_id)
                    
                    # Extract metadata using existing functions
                    project_info = summary.get('project_info', {})
                    languages_data = summary.get('languages', {})
                    collab_analysis = summary.get('collaboration_analysis', {})
                    time_analysis = summary.get('time_analysis', {})
                    
                    # Determine individual_or_collaborative using existing logic
                    collab_level = collab_analysis.get('collaboration_level', 'Likely individual project')
                    is_collaborative = collab_level != 'Likely individual project'
                    
                    # Get collaborators using existing functions
                    authors = _identify_authors_from_zip(project_id)
                    common_names = _extract_common_names_from_filenames(file_contents)
                    all_collaborators = sorted(list(authors.union(common_names)))
                    
                    # Get programming languages using existing analysis
                    programming_languages = []
                    by_language = key_metrics.get('by_language', [])
                    for lang_data in by_language:
                        lang_name = lang_data.get('language', '')
                        if lang_name and lang_name != 'Unknown':
                            programming_languages.append(lang_name)
                    
                    # Get frameworks using existing ProjectAnalyzer function
                    frameworks = []
                    if file_contents:
                        frameworks = self.project_analyzer._detect_frameworks_from_files(file_contents)
                    
                    # Get file type breakdown using existing activity classifier
                    by_activity = key_metrics.get('by_activity', {})
                    file_type_breakdown = {}
                    for activity_type, data in by_activity.items():
                        file_type_breakdown[activity_type] = {
                            'count': data.get('count', 0),
                            'bytes': data.get('bytes', 0),
                            'percentage': data.get('pct_count', 0)
                        }
                    
                    # Get dates from timeline using existing key_metrics
                    timeline = key_metrics.get('timeline', {})
                    start_date = timeline.get('start')
                    end_date = timeline.get('end')
                    
                    # Get contribution metrics using existing ProjectAnalyzer
                    contribution_metrics = {}
                    if file_contents:
                        contribution_data = self.project_analyzer._calculate_contribution_metrics(file_contents)
                        contribution_metrics = {
                            'code_files': contribution_data.get('code_files', 0),
                            'test_files': contribution_data.get('test_files', 0),
                            'documentation_files': contribution_data.get('documentation_files', 0),
                            'configuration_files': contribution_data.get('configuration_files', 0),
                            'activity_distribution': contribution_data.get('activity_distribution', {})
                        }
                    
                    # Get activity frequencies from existing key_metrics
                    activity_frequencies = {}
                    for activity_type, data in by_activity.items():
                        activity_frequencies[activity_type] = {
                            'count': data.get('count', 0),
                            'pct_count': data.get('pct_count', 0),
                            'pct_bytes': data.get('pct_bytes', 0),
                            'pct_score': data.get('pct_score', 0)
                        }
                    
                    # Get project duration from existing time_analysis
                    project_duration_days = time_analysis.get('duration_days', 0)
                    intensity = time_analysis.get('intensity', 'Unknown')
                    
                    # Calculate intensity score from existing time analysis
                    intensity_score = 0
                    if intensity == "Single day":
                        intensity_score = 1
                    elif intensity == "Short-term (≤1 week)":
                        intensity_score = 2
                    elif intensity == "Medium-term (≤1 month)":
                        intensity_score = 3
                    else:
                        intensity_score = 4
                    
                    # Extract skills using existing ProjectAnalyzer function
                    extracted_skills = []
                    if file_contents:
                        base_skills = self.project_analyzer._extract_skills_from_files(file_contents)
                        extracted_skills = sorted(list(base_skills))
                    
                    # Add languages as skills
                    for lang in programming_languages:
                        if lang not in extracted_skills:
                            extracted_skills.append(lang)
                    
                    # Add frameworks as skills
                    for framework in frameworks:
                        if framework not in extracted_skills:
                            extracted_skills.append(framework)
                    
                    # Get code analysis from summary
                    code_analysis = summary.get('code_analysis', {})
                    
                    # Generate humanized project summary
                    project_summary_text = self._generate_project_summary_text(
                        summary, code_analysis, key_metrics, frameworks
                    )
                    
                    # Build project data structure
                    projects_data[project_name] = {
                        'name': project_info.get('filename', 'Unknown'),
                        'created_at': project_info.get('created_at', 'Unknown'),
                        'primary_language': languages_data.get('primary_language', 'Unknown'),
                        'languages': languages_data.get('languages', []),
                        'file_count': key_metrics.get('totals', {}).get('files', 0),
                        'lines_of_code': key_metrics.get('totals', {}).get('lines', 0),
                        'size_mb': round(file_stats.get('total_size_bytes', 0) / (1024 * 1024), 2),
                        'skills': sorted(list(extracted_skills)),
                        'summary': project_summary_text,  # Humanized summary
                        'frameworks': frameworks,
                        'has_tests': contribution_metrics.get('test_files', 0) > 0,
                        'has_docs': contribution_metrics.get('documentation_files', 0) > 0,
                        'collaboration_level': collab_analysis.get('collaboration_level', 'Unknown'),
                        'collaboration_analysis': collab_analysis.get('analysis', ''),
                        'duration_days': project_duration_days,
                        'intensity': intensity,
                        'code_quality_score': code_analysis.get('code_quality_summary', {}).get('average_quality_score', 0) if code_analysis else 0,
                        'oop_principles_count': sum(code_analysis.get('oop_principles_summary', {}).get(k, {}).get('count', 0) 
                                                   for k in ['abstraction', 'encapsulation', 'polymorphism', 'inheritance']) if code_analysis else 0,
                        'optimization_count': len(code_analysis.get('optimization_summary', [])) if code_analysis else 0,
                        'rank_score': project_score
                    }
                    
                    ordered_project_names.append(project_name)
                    
                    # Get summary for top projects using existing summarize_project function
                    if rank_idx <= 3:  # Top 3 projects
                        try:
                            from project_summarizer import summarize_project
                            summary_text = summarize_project(project_id)
                            top_summaries.append(summary_text)
                        except Exception as e:
                            top_summaries.append(f"Error generating summary: {e}")
                    
                except Exception as e:
                    print(f"Warning: Failed to process project {project_id}: {e}")
                    continue
            
            # Aggregate all skills and categorize them
            all_skills_set = set()
            all_languages_set = set()
            all_frameworks_set = set()
            total_files = 0
            total_lines = 0
            total_size_mb = 0
            
            for project_data in projects_data.values():
                all_skills_set.update(project_data.get('skills', []))
                all_languages_set.update(project_data.get('languages', []))
                all_frameworks_set.update(project_data.get('frameworks', []))
                total_files += project_data.get('file_count', 0)
                total_lines += project_data.get('lines_of_code', 0)
                total_size_mb += project_data.get('size_mb', 0)
            
            # Categorize skills using SkillMapper
            from portfolio.skill_mapper import SkillMapper
            skill_mapper = SkillMapper()
            categorized_skills = skill_mapper.categorize_skills(all_skills_set)
            
            # Build portfolio report in humanized format
            portfolio_report = {
                'user_id': self.user_id,
                'generated_at': timestamp,
                'summary': {
                    'total_projects': len(projects_data),
                    'total_files': total_files,
                    'total_lines_of_code': total_lines,
                    'total_size_mb': round(total_size_mb, 2),
                    'unique_languages': len(all_languages_set),
                    'unique_frameworks': len(all_frameworks_set),
                    'unique_skills': len(all_skills_set),
                },
                'skills': {
                    'all_skills': sorted(list(all_skills_set)),
                    'categorized': categorized_skills,
                    'languages': sorted(list(all_languages_set)),
                    'frameworks': sorted(list(all_frameworks_set)),
                },
                'projects': list(projects_data.values()),
            }
            
            return portfolio_report
            
        except Exception as e:
            print(f"Error generating portfolio report: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_project_summary_text(self, summary: Dict, code_analysis: Dict, 
                                       key_metrics: Dict, frameworks: List[str]) -> str:
        """
        Generate a humanized, narrative summary of a project.
        
        Args:
            summary: Project summary from ProjectSummarizer
            code_analysis: Deep code analysis results
            key_metrics: Key metrics from analyze_project_from_db
            frameworks: List of detected frameworks
            
        Returns:
            Human-readable project summary text
        """
        project_name = summary.get('project_info', {}).get('filename', 'this project')
        primary_lang = summary.get('languages', {}).get('primary_language', 'Unknown')
        languages = summary.get('languages', {}).get('languages', [])
        file_count = key_metrics.get('totals', {}).get('files', 0)
        lines = key_metrics.get('totals', {}).get('lines', 0)
        
        # Build narrative summary
        parts = []
        
        # Opening statement
        if primary_lang != 'Unknown':
            parts.append(f"This {primary_lang} project")
            if len(languages) > 1:
                other_langs = [l for l in languages if l != primary_lang]
                if other_langs:
                    parts.append(f" (with {', '.join(other_langs[:2])})")
            parts.append(f" demonstrates")
        else:
            parts.append("This project demonstrates")
        
        # Technical capabilities
        tech_capabilities = []
        if frameworks:
            tech_capabilities.append(f"experience with {', '.join(frameworks[:3])}")
        
        if code_analysis:
            oop_summary = code_analysis.get('oop_principles_summary', {})
            oop_count = sum(oop_summary.get(k, {}).get('count', 0) 
                           for k in ['abstraction', 'encapsulation', 'polymorphism', 'inheritance'])
            if oop_count > 0:
                tech_capabilities.append("strong object-oriented design principles")
            
            quality = code_analysis.get('code_quality_summary', {})
            if quality.get('average_quality_score', 0) > 70:
                tech_capabilities.append("high code quality standards")
            
            optimizations = code_analysis.get('optimization_summary', [])
            if optimizations:
                tech_capabilities.append("performance optimization techniques")
        
        if tech_capabilities:
            parts.append(" " + ", ".join(tech_capabilities[:2]))
        else:
            parts.append(" solid programming fundamentals")
        
        # Scale and complexity
        if lines > 0:
            if lines > 10000:
                scale_desc = "substantial"
            elif lines > 5000:
                scale_desc = "moderate-to-large"
            elif lines > 1000:
                scale_desc = "moderate"
            else:
                scale_desc = "focused"
            
            parts.append(f". With {lines:,} lines of code across {file_count} files, ")
            parts.append(f"this {scale_desc} codebase")
        else:
            parts.append(f". Comprising {file_count} files, this codebase")
        
        # Additional highlights
        highlights = []
        collab = summary.get('collaboration_analysis', {})
        if collab and collab.get('collaboration_level', '') != 'Likely individual project':
            highlights.append("collaborative development")
        
        time_analysis = summary.get('time_analysis', {})
        if time_analysis:
            duration = time_analysis.get('duration_days', 0)
            if duration > 30:
                highlights.append("long-term development")
            elif duration > 7:
                highlights.append("sustained development effort")
        
        if code_analysis:
            ds_summary = code_analysis.get('data_structure_summary', {})
            if ds_summary:
                highlights.append("sophisticated data structure usage")
        
        if highlights:
            parts.append(" showcases " + highlights[0])
        
        # Closing
        parts.append(".")
        
        return "".join(parts)
    
    def get_chronological_skills(self) -> List[Dict[str, Any]]:
        """
        Produce a chronological list of skills exercised.
        Requirement: Produce a chronological list of skills exercised.
        
        Returns:
            List of dictionaries with skill name and first_used_date,
            ordered chronologically by first appearance.
        """
        try:
            # Get projects in chronological order
            projects = list_projects_chronologically()
            
            if not projects:
                return []
            
            # Track skills and their first appearance
            skill_first_used = {}
            project_analyzer = ProjectAnalyzer(self.user_id)
            
            for project in projects:
                project_id = project['id']
                project_date = project['created_at']
                
                try:
                    # Get file contents for this project
                    file_contents = get_file_contents_by_upload_id(project_id)
                    
                    if file_contents:
                        # Extract skills from this project
                        skills = project_analyzer._extract_skills_from_files(file_contents)
                        
                        # Track first appearance of each skill
                        for skill in skills:
                            if skill not in skill_first_used:
                                skill_first_used[skill] = {
                                    'skill': skill,
                                    'first_used_date': project_date,
                                    'first_project': project['filename']
                                }
                except Exception as e:
                    # Skip projects that fail to analyze
                    continue
            
            # Convert to list and sort by date
            chronological_skills = list(skill_first_used.values())
            chronological_skills.sort(key=lambda x: x['first_used_date'])
            
            return chronological_skills
            
        except Exception as e:
            print(f"Error generating chronological skills list: {e}")
            return []