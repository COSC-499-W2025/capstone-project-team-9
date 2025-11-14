"""
Project Summarizer Module

This module provides functionality to generate comprehensive summaries of uploaded projects,
including language detection, project description, collaboration analysis, and time tracking.
"""

import os
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from config.db_config import with_db_cursor
from project_manager import get_project_by_id
from parsing.file_contents_manager import get_file_contents_by_upload_id, get_file_statistics, get_zip_file
from collaborative.identify_projects import _identify_authors_from_zip, _count_git_files, _compute_collab_score, _extract_common_names_from_filenames, _detect_team_structure
from common.constants import LANGUAGE_EXTENSIONS, PROJECT_TYPE_INDICATORS
from typing import Dict, List, Set, Tuple, Any

def _collab_level_from_score(score: int) -> str:
    """Map score to high-level label."""
    if score >= 100:
        return "Definitely collaborative"
    if score >= 70:
        return "Likely team project"
    if score >= 40:
        return "Possibly collaborative"
    return "Likely individual project"

def _build_analysis_text(level: str, authors: Set[str]) -> str:
    base = f"Based on file names and/or Git presence, this appears to be a {level.lower()}."
    if authors:
        base += " The likely contributors are: " + ", ".join(sorted(authors))
    return base


class ProjectSummarizer:
    """Main class for generating project summaries."""
    
    def __init__(self):
        self.language_extensions = LANGUAGE_EXTENSIONS
        self.project_type_indicators = PROJECT_TYPE_INDICATORS
    
    def generate_project_summary(self, project_id):
        """
        Generate a comprehensive summary for a project.
        
        Args:
            project_id (int): The ID of the project to summarize
            
        Returns:
            dict: Complete project summary
        """
        # Get project basic info
        project_info = get_project_by_id(project_id)
        if not project_info:
            return {"error": "Project not found"}
        
        # Get file contents and statistics
        file_contents = get_file_contents_by_upload_id(project_id)
        file_stats = get_file_statistics(project_id)
        
        if not file_contents:
            return {"error": "No file contents found for this project"}
        
        # Generate summary components
        summary = {
            "project_info": {
                "id": project_info['id'],
                "filename": project_info['filename'],
                "created_at": project_info['created_at'].strftime("%Y-%m-%d %H:%M:%S") if project_info['created_at'] else "Unknown"
            },
            "languages": self._detect_languages(file_contents),
            "project_description": self._generate_project_description(file_contents, file_stats),
            "collaboration_analysis": self._analyze_collaboration(project_id),
            "time_analysis": self._analyze_time_patterns(file_contents),
            "file_statistics": file_stats,
            "summary_generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add deep code analysis
        try:
            from analysis.local_analyzer import LocalAnalyzer
            local_analyzer = LocalAnalyzer()
            deep_analysis = local_analyzer.analyze_files_from_db(file_contents)
            if deep_analysis:
                summary["deep_analysis"] = deep_analysis
        except Exception as e:
            print(f"Warning: Deep analysis failed: {e}")
            summary["deep_analysis"] = {}
        
        return summary
    
    def _detect_languages(self, file_contents):
        """
        Detect programming languages used in the project.
        
        Args:
            file_contents (list): List of file content records
            
        Returns:
            dict: Language analysis results
        """
        language_counts = Counter()
        language_files = defaultdict(list)
        
        for file_info in file_contents:
            extension = file_info.get('file_extension', '').lower()
            if extension in self.language_extensions:
                language = self.language_extensions[extension]
                language_counts[language] += 1
                language_files[language].append(file_info['file_name'])
        
        # Sort languages by file count
        sorted_languages = language_counts.most_common()
        
        return {
            "primary_language": sorted_languages[0][0] if sorted_languages else "Unknown",
            "all_languages": [{"language": lang, "file_count": count} for lang, count in sorted_languages],
            "language_files": dict(language_files),
            "total_programming_files": sum(language_counts.values())
        }
    
    def _generate_project_description(self, file_contents, file_stats):
        """
        Generate a brief description of what the project does.
        
        Args:
            file_contents (list): List of file content records
            file_stats (dict): File statistics
            
        Returns:
            dict: Project description analysis
        """
        # Analyze project type based on file extensions
        project_types = []
        for file_info in file_contents:
            extension = file_info.get('file_extension', '').lower()
            for project_type, indicators in self.project_type_indicators.items():
                if extension in indicators:
                    project_types.append(project_type)
        
        # Count project type occurrences
        type_counts = Counter(project_types)
        primary_type = type_counts.most_common(1)[0][0] if type_counts else "general"
        
        # Generate description based on project type and structure
        description = self._create_description_text(primary_type, file_stats, file_contents)
        
        return {
            "project_type": primary_type,
            "detected_types": [{"type": t, "confidence": count} for t, count in type_counts.most_common()],
            "description": description,
            "key_files": self._identify_key_files(file_contents)
        }
    
    def _create_description_text(self, project_type, file_stats, file_contents):
        """Create a human-readable description of the project."""
        total_files = file_stats.get('total_files', 0)
        total_size = file_stats.get('total_size_bytes', 0)
        
        # Convert size to human readable format
        size_mb = total_size / (1024 * 1024)
        
        descriptions = {
            'web': f"A web application project with {total_files} files ({size_mb:.1f} MB). Contains frontend components, styling, and client-side logic.",
            'backend': f"A backend/server application with {total_files} files ({size_mb:.1f} MB). Implements server-side logic and API endpoints.",
            'mobile': f"A mobile application project with {total_files} files ({size_mb:.1f} MB). Contains mobile app components and platform-specific code.",
            'data_science': f"A data science/analysis project with {total_files} files ({size_mb:.1f} MB). Contains data processing scripts and analysis notebooks.",
            'devops': f"A DevOps/infrastructure project with {total_files} files ({size_mb:.1f} MB). Contains deployment scripts and configuration files.",
            'documentation': f"A documentation project with {total_files} files ({size_mb:.1f} MB). Contains written documentation and guides.",
            'database': f"A database project with {total_files} files ({size_mb:.1f} MB). Contains database schemas and queries.",
            'general': f"A software project with {total_files} files ({size_mb:.1f} MB). Contains various programming files and resources."
        }
        
        return descriptions.get(project_type, descriptions['general'])
    
    def _identify_key_files(self, file_contents):
        """Identify key files in the project (README, main files, config files)."""
        key_files = []
        
        for file_info in file_contents:
            filename = file_info['file_name'].lower()
            
            # Check for common key files
            if any(keyword in filename for keyword in ['readme', 'main', 'index', 'app', 'server']):
                key_files.append({
                    "filename": file_info['file_name'],
                    "path": file_info['file_path'],
                    "type": "main/documentation"
                })
            elif any(keyword in filename for keyword in ['config', 'settings', 'package', 'requirements']):
                key_files.append({
                    "filename": file_info['file_name'],
                    "path": file_info['file_path'],
                    "type": "configuration"
                })
        
        return key_files[:10]  # Limit to top 10 key files
    def _analyze_collaboration(self, project_id: int) -> Dict[str, Any]:
        """
        Analyze if this was worked on by a single user or with others.

        Returns:
            dict: Collaboration analysis
        """
        file_contents = get_file_contents_by_upload_id(project_id)

        indicators = {
            'git_files': _count_git_files(file_contents),
            'multiple_authors': False,   # (kept for compatibility; not directly used below)
            'team_structure': _detect_team_structure(file_contents),
            'has_common_names': False,
            'collaboration_score': 0
        }

        common_names_found = _extract_common_names_from_filenames(file_contents)
        if common_names_found:
            indicators['has_common_names'] = True

        authors = _identify_authors_from_zip(project_id)
        authors.update(common_names_found)

        score = _compute_collab_score(indicators, authors)
        indicators['collaboration_score'] = score

        level = _collab_level_from_score(score)
        analysis = _build_analysis_text(level, authors)

        return {
            "collaboration_level": level,
            "indicators": indicators,
            "analysis": analysis,
        }

    def _analyze_time_patterns(self, file_contents):
        """
        Analyze time patterns in the project.
        
        Args:
            file_contents (list): List of file content records
            
        Returns:
            dict: Time analysis results
        """
        if not file_contents:
            return {"error": "No file data available for time analysis"}
        
        # Extract creation times
        creation_times = []
        for file_info in file_contents:
            if file_info.get('created_at'):
                creation_times.append(file_info['created_at'])
        
        if not creation_times:
            return {"error": "No timestamp data available"}
        
        # Sort times
        creation_times.sort()
        
        # Calculate time span
        earliest = creation_times[0]
        latest = creation_times[-1]
        time_span = latest - earliest
        
        # Analyze development patterns
        time_analysis = {
            "earliest_file": earliest.strftime("%Y-%m-%d %H:%M:%S"),
            "latest_file": latest.strftime("%Y-%m-%d %H:%M:%S"),
            "development_span_days": time_span.days,
            "development_span_hours": time_span.total_seconds() / 3600,
            "total_files": len(creation_times)
        }
        
        # Determine development intensity
        if time_span.days == 0:
            intensity = "Single day development"
        elif time_span.days <= 7:
            intensity = "Short-term project (1 week or less)"
        elif time_span.days <= 30:
            intensity = "Medium-term project (1 month or less)"
        else:
            intensity = "Long-term project (over 1 month)"
        
        time_analysis["development_intensity"] = intensity
        
        # Calculate files per day
        if time_span.days > 0:
            files_per_day = len(creation_times) / time_span.days
            time_analysis["files_per_day"] = round(files_per_day, 2)
        else:
            time_analysis["files_per_day"] = len(creation_times)
        
        return time_analysis
    
    def format_summary_for_display(self, summary):
        """
        Format the summary for nice display in the console.
        
        Args:
            summary (dict): The project summary
            
        Returns:
            str: Formatted summary text
        """
        if "error" in summary:
            return f"Error: {summary['error']}"
        
        output = []
        output.append("=" * 80)
        output.append(f"PROJECT SUMMARY: {summary['project_info']['filename']}")
        output.append("=" * 80)
        
        # Project Info
        output.append(f"\nProject Information:")
        output.append(f"   ID: {summary['project_info']['id']}")
        output.append(f"   Created: {summary['project_info']['created_at']}")
        
        # Languages
        output.append(f"\nProgramming Languages:")
        output.append(f"   Primary Language: {summary['languages']['primary_language']}")
        output.append(f"   Total Programming Files: {summary['languages']['total_programming_files']}")
        output.append(f"   All Languages:")
        for lang_info in summary['languages']['all_languages']:
            output.append(f"     - {lang_info['language']}: {lang_info['file_count']} files")
        
        # Project Description
        output.append(f"\nProject Description:")
        output.append(f"   Type: {summary['project_description']['project_type'].title()}")
        output.append(f"   Description: {summary['project_description']['description']}")
        
        # Key Files
        if summary['project_description']['key_files']:
            output.append(f"\nKey Files:")
            for key_file in summary['project_description']['key_files'][:5]:
                output.append(f"   - {key_file['filename']} ({key_file['type']})")
        
        # Collaboration Analysis
        output.append(f"\nCollaboration Analysis:")
        output.append(f"   {summary['collaboration_analysis']['collaboration_level']}")
        output.append(f"   Score: {summary['collaboration_analysis']['indicators']['collaboration_score']}/100")
        output.append(f"   Analysis: {summary['collaboration_analysis']['analysis']}")
        
        # Time Analysis
        if "error" not in summary['time_analysis']:
            output.append(f"\nTime Analysis:")
            output.append(f"   Development Period: {summary['time_analysis']['development_intensity']}")
            output.append(f"   Time Span: {summary['time_analysis']['development_span_days']} days")
            output.append(f"   Files per Day: {summary['time_analysis']['files_per_day']}")
            output.append(f"   First File: {summary['time_analysis']['earliest_file']}")
            output.append(f"   Last File: {summary['time_analysis']['latest_file']}")
        
        # File Statistics
        output.append(f"\nFile Statistics:")
        output.append(f"   Total Files: {summary['file_statistics']['total_files']}")
        output.append(f"   Text Files: {summary['file_statistics']['text_files']}")
        output.append(f"   Binary Files: {summary['file_statistics']['binary_files']}")
        output.append(f"   Total Size: {summary['file_statistics']['total_size_bytes'] / (1024*1024):.1f} MB")
        
        # Deep Analysis Insights
        if 'deep_analysis' in summary and summary['deep_analysis']:
            output.append(f"\n{'='*80}")
            output.append("DEEP CODE ANALYSIS INSIGHTS")
            output.append("="*80)
            
            deep = summary['deep_analysis']
            
            # OOP Principles
            oop = deep.get('oop_principles_summary', {})
            if any(oop.get(k, {}).get('count', 0) > 0 for k in ['abstraction', 'encapsulation', 'polymorphism', 'inheritance']):
                output.append(f"\nObject-Oriented Programming Principles:")
                for principle in ['abstraction', 'encapsulation', 'polymorphism', 'inheritance']:
                    principle_data = oop.get(principle, {})
                    count = principle_data.get('count', 0)
                    if count > 0:
                        output.append(f"   {principle.title()}: {count} instance(s)")
                        examples = principle_data.get('examples', [])[:1]
                        if examples:
                            example = examples[0]
                            evidence = example.get('evidence', '')
                            if evidence:
                                output.append(f"      → {evidence}")
            
            # Data Structures
            ds = deep.get('data_structure_summary', {})
            if ds:
                output.append(f"\nData Structure Usage & Performance:")
                for struct_name, count in sorted(ds.items(), key=lambda x: -x[1])[:5]:
                    struct_display = struct_name.replace('_', ' ').title()
                    output.append(f"   {struct_display}: {count} usage(s)")
                    # Add performance note
                    perf_notes = {
                        'hash_map': 'O(1) average lookup - efficient for key-value operations',
                        'set': 'O(1) membership test - optimal for unique collections',
                        'list': 'O(n) search, O(1) append - good for sequential access',
                        'tree': 'O(log n) search - balanced for hierarchical data',
                        'array': 'O(1) access, O(n) search - fast random access'
                    }
                    if struct_name in perf_notes:
                        output.append(f"      → {perf_notes[struct_name]}")
            
            # Complexity Analysis
            complexity = deep.get('complexity_summary', {})
            if complexity:
                output.append(f"\nAlgorithm Complexity Awareness:")
                nested = complexity.get('nested_loops', 0)
                recursive = complexity.get('recursive_functions', 0)
                awareness = complexity.get('complexity_awareness', False)
                
                if nested > 0:
                    output.append(f"   Nested Loops: {nested} instance(s) - potential O(n²) or higher")
                if recursive > 0:
                    output.append(f"   Recursive Functions: {recursive} - demonstrates recursive thinking")
                if awareness:
                    output.append(f"   Complexity Annotations: Present - shows awareness of Big-O notation")
            
            # Optimizations
            optimizations = deep.get('optimization_summary', [])
            if optimizations:
                output.append(f"\nOptimization Evidence:")
                unique_opt_types = {}
                for opt in optimizations[:5]:
                    opt_type = opt.get('type', 'Unknown')
                    if opt_type not in unique_opt_types:
                        unique_opt_types[opt_type] = opt.get('evidence', '')
                        skill = opt.get('skill_indicator', '')
                        output.append(f"   {opt_type}: {opt.get('evidence', '')}")
                        if skill:
                            output.append(f"      → {skill}")
            
            # Code Quality
            quality = deep.get('code_quality_summary', {})
            if quality:
                score = quality.get('average_quality_score', 0)
                strengths = quality.get('strengths', [])
                
                output.append(f"\nCode Quality Assessment:")
                output.append(f"   Overall Quality Score: {score:.1f}/100")
                if strengths:
                    output.append(f"   Strengths:")
                    for strength in strengths[:5]:
                        output.append(f"      • {strength}")
        
        output.append(f"\nSummary Generated: {summary['summary_generated_at']}")
        output.append("=" * 80)
        
        return "\n".join(output)


def summarize_project(project_id):
    """
    Convenience function to generate and display a project summary.
    
    Args:
        project_id (int): The ID of the project to summarize
        
    Returns:
        str: Formatted summary text
    """
    summarizer = ProjectSummarizer()
    summary = summarizer.generate_project_summary(project_id)
    return summarizer.format_summary_for_display(summary)


def get_available_projects():
    """
    Get a list of available projects for summarization.
    
    Returns:
        list: List of project information
    """
    try:
        with with_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, filename, created_at
                FROM uploaded_files
                ORDER BY filename ASC
            """)
            
            projects = cursor.fetchall()
        return [{"id": row[0], "filename": row[1], "created_at": row[2]} for row in projects]
        
    except ConnectionError:
        print("Could not connect to database.")
        return []
    except Exception as e:
        print(f"Error retrieving projects: {e}")
        return []
