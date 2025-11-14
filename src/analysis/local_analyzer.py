import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from common.constants import LANGUAGE_EXTENSIONS, DOCUMENT_EXTENSIONS, DESIGN_EXTENSIONS
from analysis.deep_code_analyzer import DeepCodeAnalyzer


class LocalAnalyzer:
    """
    Provides local, API-independent analysis methods.
    All analysis happens on the local machine without external service calls.
    """
    
    # Language detection patterns
    LANGUAGE_EXTENSIONS = LANGUAGE_EXTENSIONS
    DOCUMENT_EXTENSIONS = DOCUMENT_EXTENSIONS
    DESIGN_EXTENSIONS = DESIGN_EXTENSIONS
    
    # Framework detection patterns (in file content or names)
    FRAMEWORK_PATTERNS = {
        'React': [r'import.*react', r'from [\'"]react[\'"]', 'package.json'],
        'Vue': [r'import.*vue', r'from [\'"]vue[\'"]', 'vue.config.js'],
        'Angular': [r'@angular/', r'angular.json'],
        'Django': [r'from django', r'import django', 'settings.py', 'manage.py'],
        'Flask': [r'from flask', r'import Flask'],
        'Express': [r'express\(\)', r'require\([\'"]express[\'"]\)'],
        'Spring': [r'@SpringBootApplication', r'springframework'],
        'Node.js': ['package.json', 'node_modules'],
        'Docker': ['Dockerfile', 'docker-compose.yml'],
        'PostgreSQL': [r'psycopg2', r'postgresql://'],
        'MongoDB': [r'mongoose', r'mongodb://'],
    }
    
    def __init__(self):
        """Initialize the local analyzer."""
        pass
    
    def analyze_project(self, project_path: str) -> Dict:
        """
        Perform comprehensive local analysis on a project.
        Issue #39: Main analysis method.
        
        Args:
            project_path (str): Path to the project directory
        
        Returns:
            dict: Complete analysis results
        """
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        
        analysis_results = {
            'project_path': project_path,
            'project_name': os.path.basename(project_path),
            'analyzed_at': datetime.now().isoformat(),
            'structure': self.analyze_structure(project_path),
            'languages': self.detect_languages(project_path),
            'frameworks': self.detect_frameworks(project_path),
            'metrics': self.calculate_metrics(project_path),
            'skills': self.extract_skills(project_path),
            'file_breakdown': self.get_file_breakdown(project_path),
        }
        
        # Perform deep code analysis
        try:
            analysis_results['deep_analysis'] = self.perform_deep_analysis(project_path)
        except Exception as e:
            print(f"Warning: Deep analysis failed: {e}")
            analysis_results['deep_analysis'] = {}
        
        return analysis_results
    
    def analyze_structure(self, project_path: str) -> Dict:
        """
        Analyze the structural organization of the project.
        Issue #39: Structural assessment.
        
        Args:
            project_path (str): Path to analyze
        
        Returns:
            dict: Structural analysis
        """
        structure = {
            'total_files': 0,
            'total_directories': 0,
            'max_depth': 0,
            'has_tests': False,
            'has_docs': False,
            'has_config': False,
            'directory_structure': []
        }
        
        for root, dirs, files in os.walk(project_path):
            depth = root[len(project_path):].count(os.sep)
            structure['max_depth'] = max(structure['max_depth'], depth)
            structure['total_directories'] += len(dirs)
            structure['total_files'] += len(files)
            
            # Check for common directories
            if any(d in ['test', 'tests', '__tests__'] for d in dirs):
                structure['has_tests'] = True
            if any(d in ['docs', 'doc', 'documentation'] for d in dirs):
                structure['has_docs'] = True
            if any(d in ['config', 'conf', 'cfg'] for d in dirs):
                structure['has_config'] = True
            
            # Record directory structure
            rel_path = os.path.relpath(root, project_path)
            if rel_path != '.':
                structure['directory_structure'].append(rel_path)
        
        return structure
    
    def detect_languages(self, project_path: str) -> Dict:
        """
        Detect programming languages used in the project.
        Issue #39: Language detection (API-independent).
        
        Args:
            project_path (str): Path to analyze
        
        Returns:
            dict: Language statistics
        """
        language_counts = {}
        language_files = {}
        
        for root, _, files in os.walk(project_path):
            for file in files:
                ext = Path(file).suffix.lower()
                
                if ext in self.LANGUAGE_EXTENSIONS:
                    lang = self.LANGUAGE_EXTENSIONS[ext]
                    language_counts[lang] = language_counts.get(lang, 0) + 1
                    
                    if lang not in language_files:
                        language_files[lang] = []
                    language_files[lang].append(os.path.join(root, file))
        
        # Calculate percentages
        total_files = sum(language_counts.values())
        language_percentages = {}
        if total_files > 0:
            for lang, count in language_counts.items():
                language_percentages[lang] = round((count / total_files) * 100, 2)
        
        return {
            'languages_detected': list(language_counts.keys()),
            'file_counts': language_counts,
            'percentages': language_percentages,
            'primary_language': max(language_counts, key=language_counts.get) if language_counts else None
        }
    
    def detect_frameworks(self, project_path: str) -> List[str]:
        """
        Detect frameworks and technologies used.
        Issue #39: Framework detection (API-independent).
        
        Args:
            project_path (str): Path to analyze
        
        Returns:
            list: Detected frameworks
        """
        detected_frameworks = set()
        
        for root, _, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check filename patterns
                for framework, patterns in self.FRAMEWORK_PATTERNS.items():
                    for pattern in patterns:
                        # Check if pattern is a filename
                        if '.' in pattern and file == pattern:
                            detected_frameworks.add(framework)
                            continue
                        
                        # Check file content for regex patterns
                        if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.json')):
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if re.search(pattern, content, re.IGNORECASE):
                                        detected_frameworks.add(framework)
                            except Exception:
                                continue
        
        return sorted(list(detected_frameworks))
    
    def calculate_metrics(self, project_path: str) -> Dict:
        """
        Calculate basic project metrics.
        Issue #39: Metrics collection (API-independent).
        
        Args:
            project_path (str): Path to analyze
        
        Returns:
            dict: Project metrics
        """
        metrics = {
            'total_lines_of_code': 0,
            'total_file_size_bytes': 0,
            'code_files': 0,
            'document_files': 0,
            'design_files': 0,
            'other_files': 0,
            'average_file_size': 0
        }
        
        file_sizes = []
        
        for root, _, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = Path(file).suffix.lower()
                
                try:
                    file_size = os.path.getsize(file_path)
                    metrics['total_file_size_bytes'] += file_size
                    file_sizes.append(file_size)
                    
                    # Categorize files (check documents first since .md can be in both)
                    if ext in self.DOCUMENT_EXTENSIONS:
                        metrics['document_files'] += 1
                    elif ext in self.DESIGN_EXTENSIONS:
                        metrics['design_files'] += 1
                    elif ext in self.LANGUAGE_EXTENSIONS:
                        metrics['code_files'] += 1
                        # Count lines of code
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                metrics['total_lines_of_code'] += sum(1 for _ in f)
                        except Exception:
                            pass
                    else:
                        metrics['other_files'] += 1
                
                except Exception:
                    continue
        
        # Calculate average file size
        if file_sizes:
            metrics['average_file_size'] = sum(file_sizes) // len(file_sizes)
        
        # Convert to MB for readability
        metrics['total_file_size_mb'] = round(metrics['total_file_size_bytes'] / (1024 * 1024), 2)
        
        return metrics
    
    def extract_skills(self, project_path: str) -> List[str]:
        """
        Extract skills based on languages, frameworks, and file types.
        Issue #39: Skill extraction (API-independent).
        
        Args:
            project_path (str): Path to analyze
        
        Returns:
            list: Extracted skills
        """
        skills = set()
        
        # Get languages and frameworks
        languages = self.detect_languages(project_path)
        frameworks = self.detect_frameworks(project_path)
        
        # Add language skills
        for lang in languages.get('languages_detected', []):
            skills.add(lang)
        
        # Add framework skills
        skills.update(frameworks)
        
        # Add additional skills based on file presence
        for root, _, files in os.walk(project_path):
            for file in files:
                # Testing skills
                if 'test' in file.lower() or file.startswith('test_'):
                    skills.add('Unit Testing')
                
                # Documentation skills
                if file.endswith('.md') or 'readme' in file.lower():
                    skills.add('Documentation')
                
                # Version control
                if file == '.gitignore' or '.git' in root:
                    skills.add('Git')
                
                # Containerization
                if file == 'Dockerfile' or file == 'docker-compose.yml':
                    skills.add('Docker')
                
                # CI/CD
                if '.github' in root or '.gitlab' in root:
                    skills.add('CI/CD')
        
        return sorted(list(skills))
    
    def get_file_breakdown(self, project_path: str) -> Dict:
        """
        Get detailed breakdown of file types.
        Issue #39: File analysis.
        
        Args:
            project_path (str): Path to analyze
        
        Returns:
            dict: File type breakdown
        """
        breakdown = {
            'by_extension': {},
            'by_category': {
                'code': 0,
                'documents': 0,
                'design': 0,
                'config': 0,
                'other': 0
            }
        }
        
        for root, _, files in os.walk(project_path):
            for file in files:
                ext = Path(file).suffix.lower()
                
                # Count by extension
                breakdown['by_extension'][ext] = breakdown['by_extension'].get(ext, 0) + 1
                
                # Count by category (check documents first since .md can be in both)
                if ext in self.DOCUMENT_EXTENSIONS:
                    breakdown['by_category']['documents'] += 1
                elif ext in self.DESIGN_EXTENSIONS:
                    breakdown['by_category']['design'] += 1
                elif ext in self.LANGUAGE_EXTENSIONS:
                    breakdown['by_category']['code'] += 1
                elif ext in ['.json', '.yml', '.yaml', '.xml', '.env', '.ini']:
                    breakdown['by_category']['config'] += 1
                else:
                    breakdown['by_category']['other'] += 1
        
        return breakdown
    
    def perform_deep_analysis(self, project_path: str) -> Dict:
        """
        Perform deep code analysis on the project to extract insights about:
        - OOP principles (abstraction, encapsulation, polymorphism)
        - Data structure choices and performance implications
        - Algorithm complexity awareness
        - Code quality indicators
        
        Args:
            project_path (str): Path to the project directory
            
        Returns:
            dict: Deep analysis results
        """
        file_analyses = []
        
        # Walk through project and analyze code files
        for root, _, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = Path(file).suffix.lower()
                
                # Only analyze code files
                if ext in self.LANGUAGE_EXTENSIONS:
                    language = self.LANGUAGE_EXTENSIONS[ext]
                    
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Perform deep analysis on this file
                        file_analysis = self.deep_analyzer.analyze_code_file(
                            file_path, content, language
                        )
                        
                        if file_analysis:
                            file_analyses.append(file_analysis)
                    
                    except Exception as e:
                        # Skip files that can't be read
                        continue
        
        # Aggregate results across all files
        if file_analyses:
            return self.deep_analyzer.aggregate_analysis(file_analyses)
        
        return {}
    
    def analyze_files_from_db(self, file_contents: List[Dict]) -> Dict:
        """
        Perform deep analysis on files retrieved from database.
        
        Args:
            file_contents: List of file content dictionaries from database
            
        Returns:
            dict: Deep analysis results
        """
        file_analyses = []
        
        for file_info in file_contents:
            # Skip binary files
            if file_info.get('is_binary', False):
                continue
            
            file_path = file_info.get('file_path', '')
            file_name = file_info.get('file_name', '')
            extension = file_info.get('file_extension', '').lower()
            content = file_info.get('file_content', '')
            
            # Get language from extension or content_type
            language = file_info.get('content_type', '')
            if not language and extension in self.LANGUAGE_EXTENSIONS:
                language = self.LANGUAGE_EXTENSIONS[extension]
            
            if not language or not content:
                continue
            
            # Convert content to string if it's bytes
            if isinstance(content, bytes):
                try:
                    content = content.decode('utf-8', errors='ignore')
                except Exception:
                    continue
            
            # Perform deep analysis
            try:
                file_analysis = self.deep_analyzer.analyze_code_file(
                    file_path, content, language
                )
                
                if file_analysis:
                    file_analyses.append(file_analysis)
            
            except Exception:
                continue
        
        # Aggregate results
        if file_analyses:
            return self.deep_analyzer.aggregate_analysis(file_analyses)
        
        return {}