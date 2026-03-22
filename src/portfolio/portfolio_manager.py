"""
Portfolio Manager Module

Generates analytical portfolio report according to Milestone 1 specifications.
Uses ONLY existing functions from the codebase - no new analysis logic.
"""

from datetime import datetime, timezone
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict
from project_manager import get_project_by_id, get_project_with_analysis, list_projects_chronologically
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
from account.user_manager import AuthManager
import json


class PortfolioManager:
    """Manages portfolio report generation using existing analysis functions."""
    
    def __init__(self, user_name: str = None):
        """
        Initialize portfolio manager.
        
        Args:
            user_name: Username (string) to filter projects and data.
                      If None, uses the currently logged-in user.
        """
        # Get current logged-in user if user_name not provided
        if user_name is None:
            user_name = AuthManager.get_current_username()
            if not user_name:
                user_name = 'default_user'  # Fallback for non-logged-in scenarios
        
        self.user_name = user_name
        self.summarizer = ProjectSummarizer()
        self.project_analyzer = ProjectAnalyzer(user_name)
        self.consent_storage = ConsentStorage()
        self.permission_manager = ExternalServicePermission(user_name)
        self.analysis_router = AnalysisRouter(user_name)
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
            consent_status = self.consent_storage.get_consent_status(self.user_name)
            user_consent = consent_status.get('consent_given', False) if consent_status else False
            
            llm_permission = self.permission_manager.has_permission('LLM')
            analysis_strategy = self.analysis_router.get_analysis_strategy('project')
            fallback_used = (analysis_strategy == 'local')
            
            # Data Isolation: Get ranked projects for current user only
            ranked_projects = rank_all_projects(user_name=self.user_name)
            
            if not ranked_projects:
                return {
                    'error': 'No projects found',
                    'timestamp': timestamp
                }
            
            # Filter by top_n if specified
            if top_n:
                ranked_projects = ranked_projects[:top_n]
            
            # Load portfolio customizations for this user
            portfolio_customizations = {}
            try:
                customized_project_ids = ResumeManager.list_customized_portfolio_projects(self.user_name)
                for proj_id in customized_project_ids:
                    customization = ResumeManager.get_portfolio_customization(self.user_name, proj_id)
                    if customization:
                        portfolio_customizations[proj_id] = customization
            except Exception as e:
                print(f"[WARNING] Could not load portfolio customizations: {e}")
                portfolio_customizations = {}
            
            # Process each project using existing functions
            projects_data = {}
            top_summaries = []
            
            for rank_idx, ranked_project in enumerate(ranked_projects, 1):
                project_id = ranked_project['project_id']
                project_name = ranked_project['filename']
                project_score = ranked_project.get('score', 0)
                project_analysis = ranked_project.get('analysis', {})
                
                try:
                    # Data Isolation: Pass username to ensure project belongs to user
                    # Get project summary using existing ProjectSummarizer
                    summary = self.summarizer.generate_project_summary(project_id, user_name=self.user_name)
                    
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

                    # Derive evaluation insights from code analysis where possible
                    evaluation_insights = []
                    quality_summary = (code_analysis or {}).get('code_quality_summary', {})
                    avg_quality = quality_summary.get('average_quality_score', 0)
                    strengths = quality_summary.get('strengths', []) or []
                    weaknesses = quality_summary.get('weaknesses', []) or []
                    if avg_quality:
                        evaluation_insights.append(f"Average code quality score: {int(avg_quality)}")
                    if strengths:
                        evaluation_insights.append(f"Strengths: {', '.join(strengths[:2])}")
                    if weaknesses:
                        evaluation_insights.append(f"Improvements: {', '.join(weaknesses[:2])}")
                    
                    # Generate humanized project summary
                    project_summary_text = self._generate_project_summary_text(
                        summary, code_analysis, key_metrics, frameworks
                    )

                    # Derive a coarse-grained score tier from the normalized score
                    score_tier = "developing"
                    if project_score >= 80:
                        score_tier = "top"
                    elif project_score >= 60:
                        score_tier = "strong"
                    
                    # Lines of code: prefer key_metrics.totals.lines; fallback to file_statistics when 0
                    loc = key_metrics.get('totals', {}).get('lines', 0)
                    if loc == 0 and file_contents:
                        file_stats_loc = self.project_analyzer._calculate_file_statistics(file_contents)
                        loc = file_stats_loc.get('total_lines_of_code', 0)

                    # Build project data structure
                    project_entry = {
                        # Stable identifiers
                        'project_id': project_id,
                        'name': project_info.get('filename', 'Unknown'),
                        'created_at': project_info.get('created_at', 'Unknown'),
                        # Verified technical data
                        'primary_language': languages_data.get('primary_language', 'Unknown'),
                        'languages': languages_data.get('languages', []),
                        'file_count': key_metrics.get('totals', {}).get('files', 0),
                        'lines_of_code': loc,
                        'size_mb': round(file_stats.get('total_size_bytes', 0) / (1024 * 1024), 2),
                        'skills': sorted(list(extracted_skills)),
                        'frameworks': frameworks,
                        'has_tests': contribution_metrics.get('test_files', 0) > 0,
                        'has_docs': contribution_metrics.get('documentation_files', 0) > 0,
                        'collaboration_level': collab_analysis.get('collaboration_level', 'Unknown'),
                        'collaboration_analysis': collab_analysis.get('analysis', ''),
                        'duration_days': project_duration_days,
                        'intensity': intensity,
                        'code_quality_score': code_analysis.get('code_quality_summary', {}).get('average_quality_score', 0) if code_analysis else 0,
                        'oop_principles_count': sum(
                            (code_analysis.get('oop_principles_summary', {}) or {}).get(k, {}).get('count', 0)
                            for k in ['abstraction', 'encapsulation', 'polymorphism', 'inheritance']
                        ) if code_analysis else 0,
                        'optimization_count': len(code_analysis.get('optimization_summary', [])) if code_analysis else 0,
                        # Ranking / evaluation
                        'rank_score': project_score,
                        'score_tier': score_tier,
                        'evaluation_insights': evaluation_insights,
                        # Narrative summary (user can customize via portfolio customizations)
                        'summary': project_summary_text,
                        # Layout / presentation defaults (can be customized per user)
                        'display_order': rank_idx,
                        'highlight': False,
                        # Role/title separate from underlying collaboration metrics
                        'role_title': 'Individual contributor' if not is_collaborative else 'Collaborator',
                    }

                    # Apply portfolio customizations if they exist (custom data takes priority for narrative/layout only)
                    if project_id in portfolio_customizations:
                        customization = portfolio_customizations[project_id]
                        if customization.get('custom_title'):
                            project_entry['name'] = customization['custom_title']
                        if customization.get('custom_description'):
                            project_entry['summary'] = customization['custom_description']
                        if customization.get('custom_role'):
                            # Map custom role into role_title, keep collaboration_level as verified data
                            project_entry['role_title'] = customization['custom_role']
                        if customization.get('display_order') is not None:
                            project_entry['display_order'] = customization['display_order']
                        if customization.get('highlight') is not None:
                            project_entry['highlight'] = bool(customization['highlight'])

                    projects_data[project_name] = project_entry
                    
                    # Get summary for top projects using existing summarize_project function
                    if rank_idx <= 3:  # Top 3 projects
                        try:
                            from project_summarizer import summarize_project
                            # Data Isolation: Pass username to verify project ownership
                            summary_text = summarize_project(project_id, user_name=self.user_name)
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
            projects_list = list(projects_data.values())
            # Respect user-defined display order when present; fall back to rank order
            projects_list.sort(key=lambda p: (p.get('display_order') if p.get('display_order') is not None else 10**9))

            portfolio_report = {
                'user_name': self.user_name,
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
                'projects': projects_list,
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
    
    def get_skills_timeline(self) -> Dict[str, Any]:
        """
        Build a skills timeline showing learning progression and depth.
        Uses file_contents directly (file extensions and names) to extract
        skills per project chronologically. No expensive analysis calls.
        """
        try:
            projects = list_projects_chronologically(user_name=self.user_name)
            if not projects:
                return {'timeline': [], 'skill_summary': [], 'total_skills': 0}

            project_analyzer = ProjectAnalyzer(self.user_name)
            skill_tracker = {}
            timeline_entries = []

            for project in projects:
                project_id = project['id']
                project_date = project['created_at']
                project_name = project['filename']

                try:
                    file_contents = get_file_contents_by_upload_id(project_id)
                    if not file_contents:
                        continue

                    all_skills = set()
                    all_skills.update(project_analyzer._extract_skills_from_files(file_contents))

                    if not all_skills:
                        continue

                    new_skills = []
                    growing_skills = []

                    for skill in all_skills:
                        if skill not in skill_tracker:
                            skill_tracker[skill] = {
                                'count': 1,
                                'first_date': project_date,
                                'first_project': project_name
                            }
                            new_skills.append(skill)
                        else:
                            skill_tracker[skill]['count'] += 1
                            growing_skills.append({
                                'skill': skill,
                                'depth': skill_tracker[skill]['count']
                            })

                    if new_skills or growing_skills:
                        date_str = project_date.isoformat() if hasattr(project_date, 'isoformat') else str(project_date)

                        timeline_entries.append({
                            'date': date_str,
                            'project': project_name,
                            'project_id': project_id,
                            'new_skills': sorted(new_skills),
                            'growing_skills': sorted(growing_skills, key=lambda x: x['skill']),
                            'total_skills_at_point': len(skill_tracker)
                        })
                except Exception as e:
                    print(f"[TIMELINE] Skipping project {project_id}: {e}")
                    continue

            skill_summary = []
            for skill, data in skill_tracker.items():
                count = data['count']
                if count >= 4:
                    level = 'Expert'
                elif count >= 3:
                    level = 'Advanced'
                elif count >= 2:
                    level = 'Intermediate'
                else:
                    level = 'Beginner'
                skill_summary.append({
                    'skill': skill,
                    'proficiency': level,
                    'project_count': count,
                    'first_used': data['first_date'].isoformat() if hasattr(data['first_date'], 'isoformat') else str(data['first_date']),
                    'first_project': data['first_project']
                })

            skill_summary.sort(key=lambda x: x['project_count'], reverse=True)

            try:
                overrides = ResumeManager.get_timeline_overrides(self.user_name)
            except Exception:
                overrides = {}

            if overrides:
                for entry in timeline_entries:
                    pid = entry.get('project_id')
                    ov = overrides.get(pid)
                    if not ov:
                        continue

                    hidden = set(ov.get('hidden_skills', []))
                    added = ov.get('added_skills', [])
                    custom_date = ov.get('custom_date')

                    if hidden:
                        entry['new_skills'] = [s for s in entry['new_skills'] if s not in hidden]
                        entry['growing_skills'] = [gs for gs in entry['growing_skills'] if gs['skill'] not in hidden]

                    if added:
                        existing = set(entry['new_skills'])
                        existing.update(gs['skill'] for gs in entry['growing_skills'])
                        for s in added:
                            if s not in existing:
                                entry['new_skills'].append(s)

                    if custom_date:
                        entry['date'] = custom_date

            return {
                'timeline': timeline_entries,
                'skill_summary': skill_summary,
                'total_skills': len(skill_tracker)
            }
        except Exception as e:
            print(f"Error generating skills timeline: {e}")
            return {'timeline': [], 'skill_summary': [], 'total_skills': 0}

    def get_activity_heatmap(self) -> Dict[str, Any]:
        """
        Generate activity heatmap data from uploaded_files and file_contents.
        Uses a single bulk SQL query for file counts per project instead
        of calling analyze_project_from_db per project.
        """
        try:
            from config.db_config import with_db_cursor

            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT uf.id, uf.filename, uf.created_at,
                           COUNT(fc.id) AS file_count,
                           COALESCE(SUM(fc.file_size), 0) AS total_size
                    FROM uploaded_files uf
                    LEFT JOIN file_contents fc ON fc.uploaded_file_id = uf.id
                    WHERE uf.user_name = %s
                    GROUP BY uf.id, uf.filename, uf.created_at
                    ORDER BY uf.created_at ASC
                """, (self.user_name,))
                rows = cursor.fetchall()

            if not rows:
                return {'activity_data': {}, 'max_activity': 0, 'total_days': 0, 'total_projects': 0}

            activity_by_date = defaultdict(lambda: {'count': 0, 'files': 0, 'lines': 0, 'projects': []})

            for row in rows:
                project_id, filename, created_at, file_count, total_size = row
                date_key = created_at.strftime('%Y-%m-%d') if hasattr(created_at, 'strftime') else str(created_at)[:10]

                activity_by_date[date_key]['count'] += 1
                activity_by_date[date_key]['files'] += file_count
                activity_by_date[date_key]['lines'] += int(total_size // 100)
                if filename not in activity_by_date[date_key]['projects']:
                    activity_by_date[date_key]['projects'].append(filename)

            serializable = {}
            max_activity = 0
            for date, data in activity_by_date.items():
                activity_score = data['count'] + (data['files'] // 5)
                if activity_score < 1:
                    activity_score = 1
                if activity_score > max_activity:
                    max_activity = activity_score
                serializable[date] = {
                    'count': data['count'],
                    'files': data['files'],
                    'lines': data['lines'],
                    'projects': data['projects'],
                    'score': activity_score
                }

            return {
                'activity_data': serializable,
                'max_activity': max_activity,
                'total_days': len(serializable),
                'total_projects': len(rows)
            }
        except Exception as e:
            print(f"Error generating activity heatmap: {e}")
            return {'activity_data': {}, 'max_activity': 0, 'total_days': 0, 'total_projects': 0}

    def _ensure_rankings_exist(self):
        """Rank and score all user projects if any are missing from project_rankings."""
        try:
            from config.db_config import with_db_cursor
            from analysis.ranking_storage import save_rankings_to_db

            with with_db_cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM uploaded_files WHERE user_name = %s",
                    (self.user_name,)
                )
                all_project_ids = {row[0] for row in cursor.fetchall()}

            if not all_project_ids:
                return

            stored = get_stored_rankings(user_name=self.user_name)
            ranked_ids = {r['project_id'] for r in stored}

            if all_project_ids - ranked_ids:
                ranked_projects = rank_all_projects(user_name=self.user_name)
                if ranked_projects:
                    save_rankings_to_db(ranked_projects, user_name=self.user_name)
        except Exception as e:
            print(f"[PORTFOLIO] Auto-ranking failed: {e}")

    def get_top3_showcase(self) -> List[Dict[str, Any]]:
        """
        Get top 3 projects with showcase data. Uses stored rankings if
        available, otherwise ranks all projects first, then reads them.
        Builds data directly from file_contents without requiring
        the full portfolio report generation.
        """
        try:
            from config.db_config import with_db_cursor
            from common.constants import LANGUAGE_EXTENSIONS

            self._ensure_rankings_exist()

            ranked = []
            try:
                with with_db_cursor() as cursor:
                    cursor.execute("""
                        SELECT pr.project_id, uf.filename, pr.score
                        FROM project_rankings pr
                        JOIN uploaded_files uf ON uf.id = pr.project_id
                        WHERE pr.user_name = %s
                        ORDER BY pr.rank_position ASC
                        LIMIT 3
                    """, (self.user_name,))
                    for row in cursor.fetchall():
                        ranked.append({
                            'project_id': row[0],
                            'filename': row[1],
                            'score': float(row[2]) if row[2] else 0
                        })
            except Exception:
                pass

            if not ranked:
                with with_db_cursor() as cursor:
                    cursor.execute("""
                        SELECT uf.id, uf.filename, uf.created_at,
                               COUNT(fc.id) AS file_count,
                               COALESCE(SUM(fc.file_size), 0) AS total_size
                        FROM uploaded_files uf
                        LEFT JOIN file_contents fc ON fc.uploaded_file_id = uf.id
                        WHERE uf.user_name = %s
                        GROUP BY uf.id, uf.filename, uf.created_at
                        ORDER BY file_count DESC, total_size DESC
                        LIMIT 3
                    """, (self.user_name,))
                    rows = cursor.fetchall()

                if not rows:
                    return []

                for idx, row in enumerate(rows):
                    ranked.append({
                        'project_id': row[0],
                        'filename': row[1],
                        'score': 0
                    })

            showcase = []
            for rank_idx, rp in enumerate(ranked, 1):
                project_id = rp['project_id']
                project_name = rp['filename']
                project_score = rp.get('score', 0)

                try:
                    # Metadata only (no BYTEA) for speed; line_count used for LOC
                    file_contents = get_file_contents_by_upload_id(project_id, include_content=False)
                    file_stats = get_file_statistics(project_id)

                    if not file_contents:
                        file_contents = []

                    lang_counts = defaultdict(int)
                    for fc in file_contents:
                        ext = (fc.get('file_extension', '') or '').lower()
                        if ext in LANGUAGE_EXTENSIONS:
                            lang_counts[LANGUAGE_EXTENSIONS[ext]] += 1

                    total_lang_files = sum(lang_counts.values())
                    primary_language = 'Unknown'
                    if lang_counts:
                        primary_language = max(lang_counts, key=lang_counts.get)

                    lang_breakdown = []
                    for lang, cnt in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
                        pct = round((cnt / total_lang_files) * 100, 1) if total_lang_files > 0 else 0
                        lang_breakdown.append({
                            'language': lang,
                            'files': cnt,
                            'lines': 0,
                            'percentage': pct
                        })

                    frameworks = self.project_analyzer._detect_frameworks_from_files(file_contents)

                    has_tests = any(
                        'test' in fc.get('file_path', '').lower() or
                        'test' in fc.get('file_name', '').lower()
                        for fc in file_contents
                    )
                    has_docs = any(
                        (fc.get('file_extension', '') or '').lower() in ['.md', '.rst', '.txt']
                        for fc in file_contents
                    )

                    total_files = file_stats.get('total_files', len(file_contents))
                    total_size = file_stats.get('total_size_bytes', 0)
                    size_mb = round(total_size / (1024 * 1024), 2)
                    file_stats_for_loc = self.project_analyzer._calculate_file_statistics(file_contents)
                    lines_of_code = file_stats_for_loc.get('total_lines_of_code', 0)

                    with with_db_cursor() as cursor:
                        cursor.execute("""
                            SELECT uf.created_at,
                                   (SELECT MIN(fc.source_created_at) FROM file_contents fc
                                    WHERE fc.uploaded_file_id = %s AND fc.source_created_at IS NOT NULL)
                            FROM uploaded_files uf WHERE uf.id = %s
                        """, (project_id, project_id))
                        row = cursor.fetchone()
                    created_at = row[0].isoformat() if row and row[0] else 'Unknown'
                    # Earliest date: from zip file entries (source_created_at) or fallback to upload time
                    earliest_ts = row[1] if row and len(row) > 1 and row[1] else (row[0] if row and row[0] else None)
                    if earliest_ts:
                        now = datetime.now(timezone.utc)
                        if getattr(earliest_ts, 'tzinfo', None) is None:
                            if isinstance(earliest_ts, datetime):
                                earliest_ts = earliest_ts.replace(tzinfo=timezone.utc)
                            else:
                                earliest_ts = datetime.combine(earliest_ts, datetime.min.time(), tzinfo=timezone.utc)
                        duration_days = (now - earliest_ts).days
                    else:
                        duration_days = 0

                    description = f"A {primary_language} project with {total_files} files"
                    if frameworks:
                        description += f" using {', '.join(frameworks[:3])}"
                    description += f", totalling {size_mb} MB."

                    customization = None
                    try:
                        customization = ResumeManager.get_portfolio_customization(self.user_name, project_id)
                    except Exception:
                        pass

                    showcase.append({
                        'rank': rank_idx,
                        'project_id': project_id,
                        'name': (customization.get('custom_title') or project_name) if customization else project_name,
                        'description': (customization.get('custom_description') or description) if customization else description,
                        'role': (customization.get('custom_role') or 'Developer') if customization else 'Developer',
                        'score': project_score,
                        'primary_language': primary_language,
                        'languages': lang_breakdown,
                        'frameworks': frameworks,
                        'file_count': total_files,
                        'lines_of_code': lines_of_code,
                        'size_mb': size_mb,
                        'quality_score': min(100, int(project_score)) if project_score else 0,
                        'oop_principles': 0,
                        'has_tests': has_tests,
                        'has_docs': has_docs,
                        'duration_days': duration_days,
                        'intensity': 'Unknown',
                        'file_type_breakdown': {},
                        'created_at': created_at
                    })
                except Exception as e:
                    print(f"[TOP3] Skipping project {project_id}: {e}")
                    continue

            return showcase
        except Exception as e:
            print(f"Error generating top 3 showcase: {e}")
            return []

    def get_chronological_skills(self) -> List[Dict[str, Any]]:
        """
        Produce a chronological list of skills exercised.
        Requirement: Produce a chronological list of skills exercised.
        
        Returns:
            List of dictionaries with skill name and first_used_date,
            ordered chronologically by first appearance.
        """
        try:
            # Get projects in chronological order for this user
            projects = list_projects_chronologically(user_name=self.user_name)
            
            if not projects:
                return []
            
            # Track skills and their first appearance
            skill_first_used = {}
            project_analyzer = ProjectAnalyzer(self.user_name)
            
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