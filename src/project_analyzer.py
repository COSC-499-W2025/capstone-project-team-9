import os
from analysis.analysis_router import AnalysisRouter
from analysis.local_analyzer import LocalAnalyzer
from config.db_config import get_connection
import json


class ProjectAnalyzer:
    """
    Main class that orchestrates project analysis based on user permissions.
    Implements the complete workflow for Issue #10.
    """
    
    def __init__(self, user_id='default_user'):
        """
        Initialize the project analyzer.
        
        Args:
            user_id (str): User identifier
        """
        self.user_id = user_id
        self.router = AnalysisRouter(user_id)
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
        
        # Route the analysis based on user permissions
        strategy = self.router.get_analysis_strategy('project')
        
        print(f"\n{'='*70}")
        print(f"Analyzing Project: {project_info['filename']}")
        print(f"Analysis Strategy: {strategy.upper()}")
        print(f"{'='*70}\n")
        
        if strategy == 'enhanced':
            # User has granted permission for external services
            print("ℹ️  Using enhanced analysis (local + external services)")
            print("⚠️  Note: External service integration not yet implemented")
            print("   Falling back to local analysis for now...\n")
            # For now, fall back to local analysis
            # TODO: Implement external service integration in future PRs
            analysis_results = self._perform_local_analysis(project_path, project_info)
        else:
            # User declined or has not granted permission - use local only
            print("ℹ️  Using local analysis only (no external services)")
            print("✓  Your data stays completely private on your machine\n")
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
        # For ZIP files, we need to extract first or analyze the extracted contents
        # Since file_contents are already in database, we can analyze from there
        
        # Get file contents from database
        file_contents = self._get_file_contents(project_info['id'])
        
        if not file_contents:
            print("⚠️  Warning: No file contents found in database")
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
            'file_statistics': self._analyze_file_statistics(file_contents),
            'languages': self._analyze_languages(file_contents),
            'frameworks': self._detect_frameworks_from_files(file_contents),
            'skills': self._extract_skills_from_files(file_contents),
            'project_structure': self._analyze_structure(file_contents),
            'contribution_metrics': self._calculate_contribution_metrics(file_contents)
        }
        
        return analysis
    
    def _get_project_info(self, uploaded_file_id):
        """Get basic project information from database."""
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, filename, filepath, status, created_at
                FROM uploaded_files
                WHERE id = %s
            """, (uploaded_file_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
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
        finally:
            conn.close()
    
    def _get_file_contents(self, uploaded_file_id):
        """Get file contents from database."""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT file_path, file_name, file_extension, file_size,
                       file_content, content_type, is_binary, created_at
                FROM file_contents
                WHERE uploaded_file_id = %s
                ORDER BY file_path
            """, (uploaded_file_id,))
            
            results = cursor.fetchall()
            cursor.close()
            
            files = []
            for row in results:
                files.append({
                    'file_path': row[0],
                    'file_name': row[1],
                    'file_extension': row[2],
                    'file_size': row[3],
                    'file_content': row[4],
                    'content_type': row[5],
                    'is_binary': row[6],
                    'created_at': row[7]
                })
            
            return files
            
        except Exception as e:
            print(f"Error retrieving file contents: {e}")
            return []
        finally:
            conn.close()
    
    def _analyze_file_statistics(self, file_contents):
        """Analyze basic file statistics."""
        total_files = len(file_contents)
        total_size = sum(f['file_size'] for f in file_contents)
        text_files = sum(1 for f in file_contents if not f['is_binary'])
        binary_files = sum(1 for f in file_contents if f['is_binary'])
        
        # Count lines of code
        total_lines = 0
        for f in file_contents:
            if not f['is_binary'] and f['file_content']:
                try:
                    total_lines += int(f['file_content'])
                except (ValueError, TypeError):
                    pass
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'text_files': text_files,
            'binary_files': binary_files,
            'total_lines_of_code': total_lines
        }
    
    def _analyze_languages(self, file_contents):
        """Analyze programming languages used."""
        from collections import Counter
        
        language_map = self.local_analyzer.LANGUAGE_EXTENSIONS
        language_counts = Counter()
        
        for file_info in file_contents:
            ext = file_info['file_extension'].lower()
            if ext in language_map:
                language_counts[language_map[ext]] += 1
        
        total = sum(language_counts.values())
        
        return {
            'languages_detected': list(language_counts.keys()),
            'language_counts': dict(language_counts),
            'primary_language': language_counts.most_common(1)[0][0] if language_counts else 'Unknown',
            'language_percentages': {
                lang: round((count / total) * 100, 1) 
                for lang, count in language_counts.items()
            } if total > 0 else {}
        }
    
    def _detect_frameworks_from_files(self, file_contents):
        """Detect frameworks from file names and patterns."""
        frameworks = set()
        
        framework_indicators = {
            'React': ['package.json', 'jsx', 'tsx'],
            'Vue': ['vue.config.js', '.vue'],
            'Angular': ['angular.json'],
            'Django': ['settings.py', 'manage.py'],
            'Flask': ['app.py', 'flask'],
            'Express': ['package.json', 'express'],
            'Node.js': ['package.json', 'node_modules'],
            'Docker': ['Dockerfile', 'docker-compose.yml'],
            'Git': ['.gitignore', '.git'],
            'PostgreSQL': ['psycopg'],
            'MongoDB': ['mongoose']
        }
        
        file_names = [f['file_name'].lower() for f in file_contents]
        file_paths = [f['file_path'].lower() for f in file_contents]
        
        for framework, indicators in framework_indicators.items():
            for indicator in indicators:
                if any(indicator in name for name in file_names + file_paths):
                    frameworks.add(framework)
                    break
        
        return sorted(list(frameworks))
    
    def _extract_skills_from_files(self, file_contents):
        """Extract skills based on files and frameworks."""
        skills = set()
        
        # Add language skills
        languages = self._analyze_languages(file_contents)
        skills.update(languages['languages_detected'])
        
        # Add framework skills
        frameworks = self._detect_frameworks_from_files(file_contents)
        skills.update(frameworks)
        
        # Add additional skills based on file patterns
        file_names = [f['file_name'].lower() for f in file_contents]
        
        if any('test' in name for name in file_names):
            skills.add('Testing')
        if any('readme' in name or name.endswith('.md') for name in file_names):
            skills.add('Documentation')
        if any('.yml' in name or '.yaml' in name for name in file_names):
            skills.add('Configuration Management')
        
        return sorted(list(skills))
    
    def _analyze_structure(self, file_contents):
        """Analyze project structure."""
        folders = set()
        for file_info in file_contents:
            folder = os.path.dirname(file_info['file_path'])
            if folder:
                folders.add(folder)
        
        depth = max(folder.count('/') for folder in folders) if folders else 0
        
        return {
            'total_folders': len(folders),
            'max_depth': depth,
            'has_tests': any('test' in f['file_path'].lower() for f in file_contents),
            'has_docs': any('doc' in f['file_path'].lower() or f['file_name'].lower() == 'readme.md' for f in file_contents),
            'has_config': any('config' in f['file_path'].lower() for f in file_contents)
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
            
            if ext in self.local_analyzer.LANGUAGE_EXTENSIONS:
                if 'test' in path_lower:
                    test_files += 1
                else:
                    code_files += 1
            elif ext in self.local_analyzer.DOCUMENT_EXTENSIONS:
                doc_files += 1
            elif ext in ['.json', '.yml', '.yaml', '.xml', '.env', '.ini']:
                config_files += 1
        
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
        conn = get_connection()
        if not conn:
            print("Warning: Could not store analysis results")
            return False
        
        try:
            cursor = conn.cursor()
            
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
            
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error storing analysis results: {e}")
            return False
        finally:
            conn.close()
    
    def display_analysis_results(self, analysis_results):
        """
        Display analysis results in a formatted way.
        Issue #10: Provides feedback to user.
        
        Args:
            analysis_results (dict): Analysis results to display
        """
        if not analysis_results.get('success', False):
            print(f"\n✗ Analysis failed: {analysis_results.get('error', 'Unknown error')}\n")
            return
        
        print("\n" + "="*70)
        print("ANALYSIS RESULTS")
        print("="*70)
        
        # Project Info
        proj = analysis_results.get('project_info', {})
        print(f"\n📦 Project: {proj.get('filename', 'Unknown')}")
        print(f"   ID: {proj.get('id', 'N/A')}")
        print(f"   Created: {proj.get('created_at', 'Unknown')}")
        
        # File Statistics
        stats = analysis_results.get('file_statistics', {})
        print(f"\n📊 File Statistics:")
        print(f"   Total Files: {stats.get('total_files', 0)}")
        print(f"   Total Size: {stats.get('total_size_mb', 0)} MB")
        print(f"   Text Files: {stats.get('text_files', 0)}")
        print(f"   Binary Files: {stats.get('binary_files', 0)}")
        print(f"   Lines of Code: {stats.get('total_lines_of_code', 0)}")
        
        # Languages
        langs = analysis_results.get('languages', {})
        print(f"\n💻 Programming Languages:")
        print(f"   Primary: {langs.get('primary_language', 'Unknown')}")
        if langs.get('language_percentages'):
            print(f"   Distribution:")
            for lang, pct in langs['language_percentages'].items():
                print(f"     - {lang}: {pct}%")
        
        # Frameworks
        frameworks = analysis_results.get('frameworks', [])
        if frameworks:
            print(f"\n🔧 Frameworks & Technologies:")
            for fw in frameworks:
                print(f"   - {fw}")
        
        # Skills
        skills = analysis_results.get('skills', [])
        if skills:
            print(f"\n🎯 Skills Identified:")
            for skill in skills:
                print(f"   - {skill}")
        
        # Structure
        structure = analysis_results.get('project_structure', {})
        print(f"\n📁 Project Structure:")
        print(f"   Folders: {structure.get('total_folders', 0)}")
        print(f"   Max Depth: {structure.get('max_depth', 0)}")
        print(f"   Has Tests: {'✓' if structure.get('has_tests') else '✗'}")
        print(f"   Has Docs: {'✓' if structure.get('has_docs') else '✗'}")
        print(f"   Has Config: {'✓' if structure.get('has_config') else '✗'}")
        
        # Contribution Metrics
        metrics = analysis_results.get('contribution_metrics', {})
        print(f"\n📈 Contribution Metrics:")
        print(f"   Code Files: {metrics.get('code_files', 0)}")
        print(f"   Test Files: {metrics.get('test_files', 0)}")
        print(f"   Documentation Files: {metrics.get('documentation_files', 0)}")
        print(f"   Configuration Files: {metrics.get('configuration_files', 0)}")
        
        dist = metrics.get('activity_distribution', {})
        if dist:
            print(f"   Activity Distribution:")
            print(f"     - Code: {dist.get('code', 0)}%")
            print(f"     - Testing: {dist.get('testing', 0)}%")
            print(f"     - Documentation: {dist.get('documentation', 0)}%")
            print(f"     - Configuration: {dist.get('configuration', 0)}%")
        
        print("\n" + "="*70)
        print(f"Analysis Strategy Used: {analysis_results.get('analysis_strategy', 'local').upper()}")
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