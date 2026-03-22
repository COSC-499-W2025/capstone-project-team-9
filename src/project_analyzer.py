import os
from collections import Counter
import json
import zipfile

from analysis.analysis_router import AnalysisRouter
from analysis.local_analyzer import LocalAnalyzer
from config.db_config import with_db_cursor
from common.logger import setup_logger

class ProjectAnalyzer:
    def __init__(self, user_id='default_user', interactive=True):
        self.user_id = user_id
        self.interactive = interactive
        self.router = AnalysisRouter(user_name=user_id)
        self.local_analyzer = LocalAnalyzer()
        self.logger = setup_logger(f"{__name__}.{user_id}")
    
    def analyze_uploaded_project(self, uploaded_file_id):
        # Get the project information from database
        project_info = self._get_project_info(uploaded_file_id)
        if not project_info:
            return {
                'success': False,
                'error': 'Project not found in database'
            }
        
        project_path = project_info['filepath']
        
        # Resolve the zip path on disk (needed only for optional zip success report).
        # The main analysis reads file contents from the database, so a missing
        # zip on disk is NOT fatal.
        resolved_zip_path = None
        candidate_paths = [
            project_path,
            os.path.join('data', project_path),
            os.path.abspath(project_path),
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                resolved_zip_path = p
                break
        
        if not resolved_zip_path:
            self.logger.warning(f"ZIP file not on disk ({project_path}); zip report will be skipped")
        
        # Request external service permission if needed (Issue #10)
        if self.interactive:
            from external_services.external_service_prompt import request_external_service_permission
            request_external_service_permission(self.user_id, 'LLM', force=False)
            self.router = AnalysisRouter(user_name=self.user_id)
        
        strategy = self.router.get_analysis_strategy('project')
        
        self.logger.info("-" * 70)
        self.logger.info(f"Analyzing Project: {project_info['filename']}")
        self.logger.info(f"Analysis Strategy: {strategy.upper()}")
        self.logger.info("-" * 70)
        
        analysis_results = self._perform_local_analysis(resolved_zip_path, project_info)
        
        # Add metadata
        analysis_results['uploaded_file_id'] = uploaded_file_id
        analysis_results['analysis_strategy'] = strategy
        analysis_results['success'] = True
        
        # Store analysis results in database
        self._store_analysis_results(uploaded_file_id, analysis_results)
        
        return analysis_results
    
    def _perform_local_analysis(self, project_path, project_info):
        # Metadata only first (no BYTEA load) - keeps large projects fast
        file_metadata = self._get_file_contents(project_info['id'], include_content=False)
        if not file_metadata:
            self.logger.warning("No file contents found in database")
            return {'error': 'No file contents available for analysis'}

        self.logger.info(f"Analyzing {len(file_metadata)} files from project...")

        file_statistics = self._calculate_file_statistics(file_metadata)
        file_statistics['total_lines_of_code'] = (
            file_statistics.get('total_lines_of_code', 0)
            + self._lines_from_content_when_missing_loc(project_info['id'], file_metadata)
        )

        analysis = {
            'project_info': {
                'id': project_info['id'],
                'filename': project_info['filename'],
                'filepath': project_info['filepath'],
                'created_at': project_info['created_at'].isoformat() if project_info['created_at'] else None
            },
            'languages': self._analyze_languages_from_files(file_metadata),
            'frameworks': self._detect_frameworks_from_files(file_metadata),
            'skills': self._extract_skills_from_files(file_metadata),
            'project_structure': self._analyze_structure(file_metadata),
            'file_statistics': file_statistics,
            'contribution_metrics': self._calculate_contribution_metrics(file_metadata)
        }
        try:
            if project_path and zipfile.is_zipfile(project_path):
                from analysis.zip_project_analyzer import analyze_zip_project
                zip_report = analyze_zip_project(project_path)
                analysis['zip_success_report'] = {
                    'project_name': zip_report.get('project_name'),
                    'zip_file_mtime': zip_report.get('zip_file_mtime'),
                    'zip_earliest_entry': zip_report.get('zip_earliest_entry'),
                    'metrics': zip_report.get('metrics', {}),
                    'signals': zip_report.get('signals', {}),
                    'evidence': zip_report.get('evidence', {}),
                    'success': zip_report.get('success', {}),
                }
        except Exception as e:
            analysis['zip_success_report'] = {'error': f'Zip success report unavailable: {e}'}

        # First file created (in project): from ZIP earliest entry, else min source_created_at from DB
        first_created = None
        if analysis.get('zip_success_report', {}).get('zip_earliest_entry'):
            first_created = analysis['zip_success_report']['zip_earliest_entry']
        else:
            dates = [f.get('source_created_at') for f in file_metadata if f.get('source_created_at')]
            if dates:
                first_created = min(dates)
                if hasattr(first_created, 'isoformat'):
                    first_created = first_created.isoformat()
        analysis['first_file_created'] = first_created

        # Deep analysis: fetch content only for first 40 code files
        code_paths = [f['file_path'] for f in file_metadata
                      if (f.get('file_extension') or '').lower() in LANGUAGE_EXTENSIONS
                      and not f.get('is_binary')][:40]
        if code_paths:
            try:
                code_with_content = get_file_contents_content_for_paths(project_info['id'], code_paths)
                if code_with_content:
                    deep_analysis = self.local_analyzer.analyze_files_from_db(code_with_content)
                    if deep_analysis:
                        analysis['deep_analysis'] = deep_analysis
            except Exception as e:
                self.logger.warning(f"Deep analysis failed: {e}")
        if 'deep_analysis' not in analysis:
            analysis['deep_analysis'] = {}

        # Document subjects: fetch content only for first few PDFs/images
        pdf_ext = {'.pdf'}
        img_ext = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
        doc_paths = []
        for f in file_metadata:
            if len(doc_paths) >= 6:
                break
            ext = (f.get('file_extension') or '').lower()
            if ext in pdf_ext or ext in img_ext:
                doc_paths.append(f['file_path'])
        try:
            doc_with_content = get_file_contents_content_for_paths(project_info['id'], doc_paths) if doc_paths else []
            analysis['document_subjects'] = self.local_analyzer.extract_document_subjects_from_files(
                doc_with_content, max_files=6, max_text_chars=8000)
        except Exception as e:
            self.logger.warning(f"Document subject extraction failed: {e}")
            analysis['document_subjects'] = {"enabled": False, "error": str(e)}
        return analysis
    
    def _get_project_info(self, uploaded_file_id):
        """
        Get basic project information from database.
        Data Isolation: Only returns project if it belongs to the current user.
        """
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT id, filename, filepath, status, created_at
                    FROM uploaded_files
                    WHERE id = %s AND user_name = %s
                """, (uploaded_file_id, self.user_id))
                
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
            self.logger.error(f"Error retrieving project info: {e}")
            return None
    
    def _get_file_contents(self, uploaded_file_id, include_content=True):
        """Get file records from database. Set include_content=False for metadata-only (fast)."""
        try:
            from parsing.file_contents_manager import get_file_contents_by_upload_id
            rows = get_file_contents_by_upload_id(uploaded_file_id, include_content=include_content)
            # Normalize to expected keys (content_type -> content_type, add created_at if missing)
            return [
                {
                    'file_path': r['file_path'],
                    'file_name': r['file_name'],
                    'file_extension': r.get('file_extension') or '',
                    'file_size': r.get('file_size') or 0,
                    'file_content': r.get('file_content'),
                    'content_type': r.get('content_type'),
                    'is_binary': r.get('is_binary', False),
                    'created_at': r.get('created_at'),
                    'line_count': r.get('line_count'),
                    'source_created_at': r.get('source_created_at'),
                }
                for r in rows
            ]
        except Exception as e:
            self.logger.error(f"Error retrieving file contents: {e}")
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
    
    def _count_lines(self, content):
        """Count lines in file content (bytes or str). Fast, no full decode for bytes."""
        if content is None:
            return 0
        if isinstance(content, bytes):
            return content.count(b'\n') + (1 if content and not content.endswith(b'\n') else 0)
        return len(content.splitlines()) or (1 if content.strip() else 0)

    def _calculate_file_statistics(self, file_contents):
        """Calculate file statistics. Prefer line_count from DB; else count from content."""
        from common.constants import LANGUAGE_EXTENSIONS
        total_files = len(file_contents)
        total_size = sum(f['file_size'] for f in file_contents)
        text_files = sum(1 for f in file_contents if not f.get('is_binary'))
        binary_files = sum(1 for f in file_contents if f.get('is_binary'))
        total_lines = 0
        for f in file_contents:
            if f.get('is_binary'):
                continue
            ext = (f.get('file_extension') or '').lower()
            if ext not in LANGUAGE_EXTENSIONS:
                continue
            if f.get('line_count') is not None:
                total_lines += f['line_count']
            elif f.get('file_content'):
                total_lines += self._count_lines(f['file_content'])
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'text_files': text_files,
            'binary_files': binary_files,
            'total_lines_of_code': total_lines
        }

    def _lines_from_content_when_missing_loc(self, uploaded_file_id, file_metadata):
        """Sum lines from stored BYTEA for code files with NULL line_count (batched)."""
        from common.constants import LANGUAGE_EXTENSIONS
        from parsing.file_contents_manager import get_file_contents_content_for_paths

        code_without_loc = [
            f['file_path'] for f in file_metadata
            if (f.get('file_extension') or '').lower() in LANGUAGE_EXTENSIONS
            and not f.get('is_binary')
            and f.get('line_count') is None
        ]
        if not code_without_loc:
            return 0
        added = 0
        chunk_size = 80
        for i in range(0, len(code_without_loc), chunk_size):
            batch = code_without_loc[i:i + chunk_size]
            try:
                with_content = get_file_contents_content_for_paths(uploaded_file_id, batch)
                for rec in with_content:
                    lc = self._count_lines(rec.get('file_content'))
                    if lc:
                        added += lc
            except Exception as e:
                self.logger.debug(f"LOC batch fetch failed: {e}")
        return added

    def get_total_lines_of_code(self, uploaded_file_id, file_metadata):
        """LOC from line_count and/or BYTEA for rows missing line_count (metadata-only safe)."""
        stats = self._calculate_file_statistics(file_metadata)
        return stats.get('total_lines_of_code', 0) + self._lines_from_content_when_missing_loc(
            uploaded_file_id, file_metadata
        )

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
            self.logger.error(f"Error storing analysis results: {e}")
            return False
    
    def display_analysis_results(self, analysis_results):
        if not analysis_results.get('success', False):
            self.logger.error(f"Analysis failed: {analysis_results.get('error', 'Unknown error')}")
            return
            
        proj = analysis_results.get('project_info', {})
        self.logger.info("-" * 70)
        self.logger.info(f"ANALYSIS: {proj.get('filename', 'Unknown')}")
        self.logger.info("-" * 70)
        
        langs = analysis_results.get('languages', {})
        stats = analysis_results.get('file_statistics', {})
        self.logger.info(f"Overview:")
        self.logger.info(f"  Language: {langs.get('primary_language', 'Unknown')}")
        self.logger.info(f"  Files: {stats.get('total_files', 0)} ({stats.get('total_size_mb', 0)} MB)")
        
        frameworks = analysis_results.get('frameworks', [])
        if frameworks:
            self.logger.info(f"  Frameworks: {', '.join(frameworks[:5])}")
            
        skills = analysis_results.get('skills', [])
        if skills:
            self.logger.info(f"  Skills: {', '.join(skills[:8])}")
            
        structure = analysis_results.get('project_structure', {})
        if structure.get('has_tests') or structure.get('has_docs'):
            features = []
            if structure.get('has_tests'):
                features.append("Tests")
            if structure.get('has_docs'):
                features.append("Docs")
            self.logger.info(f"  Features: {', '.join(features)}")
            
        if 'deep_analysis' in analysis_results and analysis_results['deep_analysis']:
            deep = analysis_results['deep_analysis']
            quality = deep.get('code_quality_summary', {})
            if quality.get('average_quality_score', 0) > 0:
                self.logger.info(f"  Code Quality: {quality.get('average_quality_score', 0):.1f}/100")
            oop = deep.get('oop_principles_summary', {})
            oop_count = sum(oop.get(k, {}).get('count', 0) for k in ['abstraction', 'encapsulation', 'polymorphism', 'inheritance'])
            if oop_count > 0:
                self.logger.info(f"  OOP Principles: {oop_count} instance(s) detected")
        self.logger.info("-" * 70)


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
