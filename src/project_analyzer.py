import os
from collections import Counter
from analysis.analysis_router import AnalysisRouter
from analysis.local_analyzer import LocalAnalyzer
from config.db_config import with_db_cursor
import json


class ProjectAnalyzer:
    """
    Main class that orchestrates project analysis based on user permissions.
    Implements the complete workflow for Issue #10.
    """
    
    def __init__(self, user_name='default_user'):
        """
        Initialize the project analyzer.
        
        Args:
            user_name (str): User name
        """
        self.user_name = user_name
        self.router = AnalysisRouter(user_name)
        self.local_analyzer = LocalAnalyzer()
    
    def analyze_uploaded_project(self, uploaded_file_id):
        """
        Analyze a project that has been uploaded to the database.
        This is the main entry point for analyzing projects.
        
        Issue #10: Provides feedback regardless of external service permission.
        
        Args:
            uploaded_file_id (int): The ID of the uploaded file in the database
            
        Returns:
            dict: Complete analysis results
        """
        # Get the project information from database
        project_info = self._get_project_info(uploaded_file_id)
        if not project_info:
            return {
                'success': False,
                'error': 'Project not found in database'
            }
        
        project_path = project_info['filepath']
        
        # Check if the file still exists
        if not os.path.exists(project_path):
            return {
                'success': False,
                'error': f'Project file not found: {project_path}'
            }
        
        # Request external service permission if needed (Issue #10)
        # This happens on first analysis, then is cached
        from external_services.external_service_prompt import request_external_service_permission
        request_external_service_permission(self.user_name, 'LLM', force=False)
        
        # Update router with fresh permission data
        self.router = AnalysisRouter(self.user_name)
        
        # Route the analysis based on user permissions
        strategy = self.router.get_analysis_strategy('project')
        
        print(f"\n{'='*70}")
        print(f"Analyzing Project: {project_info['filename']}")
        print(f"Analysis Strategy: {strategy.upper()}")
        print(f"{'='*70}\n")
        
        if strategy == 'enhanced':
            # User has granted permission for external services
            print("Using enhanced analysis (local + external services)")
            print("Note: External service integration not yet implemented")
            print("Falling back to local analysis for now...\n")
            # For now, fall back to local analysis
            # TODO: Implement external service integration in future PRs
            analysis_results = self._perform_local_analysis(project_path, project_info)
        else:
            # User declined or has not granted permission - use local only
            print("Using local analysis only (your data stays completely private)\n")
            analysis_results = self._perform_local_analysis(project_path, project_info)
        
        # Add metadata
        analysis_results['uploaded_file_id'] = uploaded_file_id
        analysis_results['analysis_strategy'] = strategy
        analysis_results['success'] = True
        
        # Store analysis results in database
        self._store_analysis_results(uploaded_file_id, analysis_results)
        
        return analysis_results
    
    def _perform_local_analysis(self, project_path, project_info):
        """
        Perform local analysis on the project.
        Sub-issue #39: Uses API-independent local analysis methods.
        
        Args:
            project_path (str): Path to the project file/directory
            project_info (dict): Basic project information from database
            
        Returns:
            dict: Local analysis results
        """
        # Get file contents from database
        file_contents = self._get_file_contents(project_info['id'])
        
        if not file_contents:
            print("Warning: No file contents found in database")
            return {
                'error': 'No file contents available for analysis'
            }
        
        print(f"Analyzing {len(file_contents)} files from project...")
        
        # Prepare analysis results
        analysis = {
            'project_info': {
                'id': project_info['id'],
                'filename': project_info['filename'],
                'filepath': project_info['filepath'],
                'created_at': project_info['created_at'].isoformat() if project_info['created_at'] else None
            },
            'languages': self._analyze_languages_from_files(file_contents),
            'frameworks': self._detect_frameworks_from_files(file_contents),
            'skills': self._extract_skills_from_files(file_contents),
            'project_structure': self._analyze_structure(file_contents),
            'file_statistics': self._calculate_file_statistics(file_contents),
            'contribution_metrics': self._calculate_contribution_metrics(file_contents)
        }
        try:
            deep_analysis = self.local_analyzer.analyze_files_from_db(file_contents)
            if deep_analysis:
                analysis['deep_analysis'] = deep_analysis
        except Exception as e:
            print(f"Warning: Deep analysis failed: {e}")
            analysis['deep_analysis'] = {}
        return analysis
    
    def _get_project_info(self, uploaded_file_id):
        """Get basic project information from database."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, filename, filepath, status, created_at
                    FROM uploaded_files
                    WHERE id = %s
                """, (uploaded_file_id,))
                
                result = cursor.fetchone()
                
                if result:
                    return {
                        'id': result[0],
                        'filename': result[1],
                        'filepath': result[2],
                        'status': result[3],
                        'created_at': result[4]
                    }
                return None
        except Exception as e:
            print(f"Error retrieving project info: {e}")
            return None
    
    def _get_file_contents(self, uploaded_file_id):
        """Get file contents from database."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT file_path, file_name, file_extension, file_size,
                           file_content, content_type, is_binary, created_at
                    FROM file_contents
                    WHERE uploaded_file_id = %s
                    ORDER BY file_path
                """, (uploaded_file_id,))
                
                results = cursor.fetchall()
                
                files = []
                for row in results:
                    files.append({
                        'file_path': row[0],
                        'file_name': row[1],
                        'file_extension': row[2],
                        'file_size': row[3] or 0,
                        'file_content': row[4],
                        'content_type': row[5],
                        'is_binary': row[6],
                        'created_at': row[7]
                    })
                
                return files
        except Exception as e:
            print(f"Error retrieving file contents: {e}")
            return []
    
    def _analyze_languages_from_files(self, file_contents):
        from common.constants import LANGUAGE_EXTENSIONS
        language_counts = Counter()
        for f in file_contents:
            ext = f['file_extension'].lower()
            if ext in LANGUAGE_EXTENSIONS:
                lang = LANGUAGE_EXTENSIONS[ext]
                language_counts[lang] += 1
        total = sum(language_counts.values())
        percentages = {lang: round((count / total) * 100, 1) for lang, count in language_counts.items()} if total > 0 else {}
        return {
            'primary_language': language_counts.most_common(1)[0][0] if language_counts else 'Unknown',
            'file_counts': dict(language_counts),
            'language_percentages': percentages,
            'detected_languages': list(language_counts.keys())
        }
    
    def _detect_frameworks_from_files(self, file_contents):
        file_names = [f['file_name'].lower() for f in file_contents]
        framework_indicators = {
            'React': ['package.json', 'react', '.jsx'],
            'Vue': ['vue.config.js', 'vue'],
            'Angular': ['angular.json'],
            'Django': ['manage.py', 'settings.py'],
            'Flask': ['flask'],
            'Express': ['express'],
            'Spring': ['pom.xml', 'build.gradle'],
            'Node.js': ['package.json', 'node_modules'],
            'Docker': ['dockerfile', 'docker-compose.yml'],
            'PostgreSQL': ['psycopg', 'postgresql'],
            'MongoDB': ['mongoose', 'mongodb'],
            'FastAPI': ['fastapi'],
        }
        detected_frameworks = set()
        for framework, indicators in framework_indicators.items():
            if any(any(ind.lower() in name for name in file_names) for ind in indicators):
                detected_frameworks.add(framework)
        return sorted(list(detected_frameworks))
    
    def _extract_skills_from_files(self, file_contents):
        skills = set()
        file_names = [f['file_name'].lower() for f in file_contents]
        skills.update(self._analyze_languages_from_files(file_contents).get('detected_languages', []))
        skills.update(self._detect_frameworks_from_files(file_contents))
        skill_patterns = {
            'Testing': lambda n: 'test' in n or n.startswith('test_'),
            'Documentation': lambda n: 'readme' in n or n.endswith('.md'),
            'Configuration Management': lambda n: '.yml' in n or '.yaml' in n,
            'Docker': lambda n: 'dockerfile' in n,
            'Git': lambda n: '.git' in n or '.gitignore' in n,
            'CI/CD': lambda n: '.ci' in n or '.github' in n or 'jenkinsfile' in n
        }
        for skill, pattern in skill_patterns.items():
            if any(pattern(name) for name in file_names):
                skills.add(skill)
        return sorted(list(skills))
    
    def _analyze_structure(self, file_contents):
        """Analyze project structure from file list."""
        folders = set()
        for f in file_contents:
            folder = os.path.dirname(f['file_path'])
            if folder:
                folders.add(folder)
        
        depth = max((folder.count('/') for folder in folders), default=0)
        
        return {
            'total_folders': len(folders),
            'max_depth': depth,
            'has_tests': any('test' in f['file_path'].lower() for f in file_contents),
            'has_docs': any('doc' in f['file_path'].lower() or f['file_name'].lower() == 'readme.md' for f in file_contents),
            'has_config': any('config' in f['file_path'].lower() for f in file_contents)
        }
    
    def _calculate_file_statistics(self, file_contents):
        """Calculate file statistics."""
        total_files = len(file_contents)
        total_size = sum(f['file_size'] for f in file_contents)
        text_files = sum(1 for f in file_contents if not f['is_binary'])
        binary_files = sum(1 for f in file_contents if f['is_binary'])
        
        # Calculate LOC if available
        total_lines = 0
        for f in file_contents:
            if f['file_content'] and not f['is_binary']:
                try:
                    total_lines += int(f['file_content'])
                except (ValueError, TypeError):
                    pass
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'text_files': text_files,
            'binary_files': binary_files,
            'total_lines_of_code': total_lines
        }
    
    def _calculate_contribution_metrics(self, file_contents):
        """Calculate contribution metrics."""
        code_files = 0
        test_files = 0
        doc_files = 0
        config_files = 0
        
        for f in file_contents:
            path_lower = f['file_path'].lower()
            ext = f['file_extension'].lower()
            
            # Check document extensions first since some extensions (like .md) are in both
            if ext in self.local_analyzer.DOCUMENT_EXTENSIONS:
                doc_files += 1
            elif ext in ['.json', '.yml', '.yaml', '.xml', '.env', '.ini']:
                config_files += 1
            elif ext in self.local_analyzer.LANGUAGE_EXTENSIONS:
                if 'test' in path_lower:
                    test_files += 1
                else:
                    code_files += 1
        
        total = code_files + test_files + doc_files + config_files
        
        return {
            'code_files': code_files,
            'test_files': test_files,
            'documentation_files': doc_files,
            'configuration_files': config_files,
            'activity_distribution': {
                'code': round((code_files / total) * 100, 1) if total > 0 else 0,
                'testing': round((test_files / total) * 100, 1) if total > 0 else 0,
                'documentation': round((doc_files / total) * 100, 1) if total > 0 else 0,
                'configuration': round((config_files / total) * 100, 1) if total > 0 else 0
            }
        }
    
    def _store_analysis_results(self, uploaded_file_id, analysis_results):
        """Store analysis results in the database."""
        try:
            with with_db_cursor() as cursor:
                # Create analysis_results table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id SERIAL PRIMARY KEY,
                        uploaded_file_id INTEGER REFERENCES uploaded_files(id) ON DELETE CASCADE,
                        analysis_data JSONB,
                        analysis_strategy VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert analysis results
                cursor.execute("""
                    INSERT INTO analysis_results (uploaded_file_id, analysis_data, analysis_strategy)
                    VALUES (%s, %s, %s)
                """, (uploaded_file_id, json.dumps(analysis_results, default=str), analysis_results.get('analysis_strategy', 'local')))
                
                return True
        except Exception as e:
            print(f"Error storing analysis results: {e}")
            return False
    
    def display_analysis_results(self, analysis_results):
        if not analysis_results.get('success', False):
            print(f"\nAnalysis failed: {analysis_results.get('error', 'Unknown error')}\n")
            return
        proj = analysis_results.get('project_info', {})
        print("\n" + "="*70)
        print(f"ANALYSIS: {proj.get('filename', 'Unknown')}")
        print("="*70)
        langs = analysis_results.get('languages', {})
        stats = analysis_results.get('file_statistics', {})
        print(f"\nOverview:")
        print(f"  Language: {langs.get('primary_language', 'Unknown')}")
        print(f"  Files: {stats.get('total_files', 0)} ({stats.get('total_size_mb', 0)} MB)")
        frameworks = analysis_results.get('frameworks', [])
        if frameworks:
            print(f"  Frameworks: {', '.join(frameworks[:5])}")
        skills = analysis_results.get('skills', [])
        if skills:
            print(f"  Skills: {', '.join(skills[:8])}")
        structure = analysis_results.get('project_structure', {})
        if structure.get('has_tests') or structure.get('has_docs'):
            features = []
            if structure.get('has_tests'):
                features.append("Tests")
            if structure.get('has_docs'):
                features.append("Docs")
            print(f"  Features: {', '.join(features)}")
        if 'deep_analysis' in analysis_results and analysis_results['deep_analysis']:
            deep = analysis_results['deep_analysis']
            quality = deep.get('code_quality_summary', {})
            if quality.get('average_quality_score', 0) > 0:
                print(f"  Code Quality: {quality.get('average_quality_score', 0):.1f}/100")
            oop = deep.get('oop_principles_summary', {})
            oop_count = sum(oop.get(k, {}).get('count', 0) for k in ['abstraction', 'encapsulation', 'polymorphism', 'inheritance'])
            if oop_count > 0:
                print(f"  OOP Principles: {oop_count} instance(s) detected")
        print("="*70 + "\n")


def analyze_project_by_id(project_id, user_id='default_user'):
    """
    Convenience function to analyze a project by its uploaded file ID.
    This is the main entry point for Issue #10 from the command line.
    
    Args:
        project_id (int): The uploaded file ID to analyze
        user_id (str): User identifier
        
    Returns:
        dict: Analysis results
    """
    analyzer = ProjectAnalyzer(user_id)
    results = analyzer.analyze_uploaded_project(project_id)
    analyzer.display_analysis_results(results)
    return results