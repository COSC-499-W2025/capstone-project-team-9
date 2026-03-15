from datetime import datetime
from config.db_config import with_db_cursor, get_connection
from analysis.project_ranking import rank_all_projects, calculate_project_score
from analysis.key_metrics import analyze_project_from_db
from analysis.ranking_storage import get_stored_ranking_by_project_id
from project_summarizer import ProjectSummarizer, summarize_project
from parsing.file_contents_manager import get_file_contents_by_upload_id, get_file_statistics
from portfolio.skill_mapper import SkillMapper
from account.user_manager import AuthManager
from collaborative.identify_projects import _identify_authors_from_zip, _extract_common_names_from_filenames
from database.user_preferences import get_user_git_username
from resume.evidence_extractor import build_evidence
import json


class ResumeManager:
    """Manages user resume data model and storage operations."""
    
    @staticmethod
    def init_resume_table():
        """
        Initialize the generated_resumes table in the database.
        Creates table structure for storing user-aggregated resume data.
        Uses JSONB for flexible resume content storage across different resume types.
        Uses user_name from user_informations as foreign key.
        """
        try:
            with with_db_cursor() as cursor:
                # First, create table if it doesn't exist (with new structure)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS generated_resumes (
                        id SERIAL PRIMARY KEY,
                        user_name VARCHAR(255) NOT NULL UNIQUE,
                        resume_data JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Migration: If old table exists with user_id, migrate to user_name
                # This must happen before creating the index or adding constraints
                cursor.execute("""
                    DO $$
                    BEGIN
                        -- Check if user_id column exists (old schema)
                        IF EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name='generated_resumes' AND column_name='user_id'
                        ) THEN
                            -- Rename user_id to user_name
                            ALTER TABLE generated_resumes RENAME COLUMN user_id TO user_name;
                            
                            -- Drop old index if exists
                            DROP INDEX IF EXISTS idx_generated_resumes_user_id;
                        END IF;
                    END $$;
                """)
                
                # Create index on user_name (works for both new and migrated tables)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_generated_resumes_user_name 
                    ON generated_resumes(user_name);
                """)
                
                # Add foreign key constraint if it doesn't exist
                cursor.execute("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.table_constraints 
                            WHERE constraint_name = 'fk_user_name' AND table_name = 'generated_resumes'
                        ) THEN
                            ALTER TABLE generated_resumes
                            ADD CONSTRAINT fk_user_name
                            FOREIGN KEY (user_name)
                            REFERENCES user_informations(user_name)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE;
                        END IF;
                    END $$;
                """)
            
            print("[SUCCESS] Resume table initialized successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error initializing resume table: {e}")
            return False
    
    @staticmethod
    def init_portfolio_settings_table():
        """Initialize the portfolio_settings table for storing visibility and component settings."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS portfolio_settings (
                        id SERIAL PRIMARY KEY,
                        user_name VARCHAR(255) NOT NULL UNIQUE,
                        is_public BOOLEAN DEFAULT FALSE,
                        show_timeline BOOLEAN DEFAULT TRUE,
                        show_heatmap BOOLEAN DEFAULT TRUE,
                        show_top_projects BOOLEAN DEFAULT TRUE,
                        show_skills BOOLEAN DEFAULT TRUE,
                        show_stats BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_portfolio_settings_user_name
                    ON portfolio_settings(user_name);
                """)
            print("[SUCCESS] Portfolio settings table initialized successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Error initializing portfolio settings table: {e}")
            return False

    @staticmethod
    def get_portfolio_settings(user_name: str) -> dict:
        """Get portfolio visibility and component settings for a user."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT is_public, show_timeline, show_heatmap, show_top_projects,
                           show_skills, show_stats, updated_at
                    FROM portfolio_settings
                    WHERE user_name = %s
                """, (user_name,))
                result = cursor.fetchone()
            if result:
                return {
                    'is_public': result[0],
                    'show_timeline': result[1],
                    'show_heatmap': result[2],
                    'show_top_projects': result[3],
                    'show_skills': result[4],
                    'show_stats': result[5],
                    'updated_at': result[6].isoformat() if result[6] else None
                }
            return {
                'is_public': False,
                'show_timeline': True,
                'show_heatmap': True,
                'show_top_projects': True,
                'show_skills': True,
                'show_stats': True,
                'updated_at': None
            }
        except Exception as e:
            print(f"[ERROR] Failed to get portfolio settings: {e}")
            return {
                'is_public': False, 'show_timeline': True, 'show_heatmap': True,
                'show_top_projects': True, 'show_skills': True, 'show_stats': True,
                'updated_at': None
            }

    @staticmethod
    def save_portfolio_settings(user_name: str, settings: dict) -> bool:
        """Save portfolio visibility and component settings."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO portfolio_settings
                        (user_name, is_public, show_timeline, show_heatmap,
                         show_top_projects, show_skills, show_stats)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_name)
                    DO UPDATE SET
                        is_public = EXCLUDED.is_public,
                        show_timeline = EXCLUDED.show_timeline,
                        show_heatmap = EXCLUDED.show_heatmap,
                        show_top_projects = EXCLUDED.show_top_projects,
                        show_skills = EXCLUDED.show_skills,
                        show_stats = EXCLUDED.show_stats,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    user_name,
                    settings.get('is_public', False),
                    settings.get('show_timeline', True),
                    settings.get('show_heatmap', True),
                    settings.get('show_top_projects', True),
                    settings.get('show_skills', True),
                    settings.get('show_stats', True)
                ))
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save portfolio settings: {e}")
            return False

    @staticmethod
    def init_portfolio_timeline_overrides_table():
        """Initialize the portfolio_timeline_overrides table for per-project skill edits."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS portfolio_timeline_overrides (
                        id SERIAL PRIMARY KEY,
                        user_name VARCHAR(255) NOT NULL,
                        project_id INTEGER NOT NULL,
                        hidden_skills JSONB DEFAULT '[]'::jsonb,
                        added_skills JSONB DEFAULT '[]'::jsonb,
                        custom_date DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_name, project_id)
                    );
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_portfolio_tl_overrides_user
                    ON portfolio_timeline_overrides(user_name);
                """)
            print("[SUCCESS] portfolio_timeline_overrides table initialized")
            return True
        except Exception as e:
            print(f"[ERROR] Error initializing portfolio_timeline_overrides table: {e}")
            return False

    @staticmethod
    def save_timeline_override(user_name: str, project_id: int, override_data: dict) -> bool:
        """Save or update timeline overrides for a specific project."""
        try:
            hidden = json.dumps(override_data.get('hidden_skills', []))
            added = json.dumps(override_data.get('added_skills', []))
            custom_date = override_data.get('custom_date') or None

            with with_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO portfolio_timeline_overrides
                        (user_name, project_id, hidden_skills, added_skills, custom_date)
                    VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
                    ON CONFLICT (user_name, project_id)
                    DO UPDATE SET
                        hidden_skills = EXCLUDED.hidden_skills,
                        added_skills  = EXCLUDED.added_skills,
                        custom_date   = EXCLUDED.custom_date,
                        updated_at    = CURRENT_TIMESTAMP
                """, (user_name, project_id, hidden, added, custom_date))
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save timeline override: {e}")
            return False

    @staticmethod
    def get_timeline_overrides(user_name: str) -> dict:
        """Get all timeline overrides for a user, keyed by project_id."""
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT project_id, hidden_skills, added_skills, custom_date
                    FROM portfolio_timeline_overrides
                    WHERE user_name = %s
                """, (user_name,))
                rows = cursor.fetchall()
            result = {}
            for row in rows:
                pid = row[0]
                result[pid] = {
                    'hidden_skills': row[1] if row[1] else [],
                    'added_skills': row[2] if row[2] else [],
                    'custom_date': row[3].isoformat() if row[3] else None
                }
            return result
        except Exception as e:
            print(f"[ERROR] Failed to get timeline overrides: {e}")
            return {}

    @staticmethod
    def init_portfolio_customizations_table():
        """
        Initialize the portfolio_customizations table in the database.
        Creates table structure for storing user customizations for portfolio showcase projects.
        Each row represents customizations for a specific project by a specific user.
        """
        try:
            with with_db_cursor() as cursor:
                # Create portfolio_customizations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS portfolio_customizations (
                        id SERIAL PRIMARY KEY,
                        user_name VARCHAR(255) NOT NULL,
                        project_id INTEGER NOT NULL,
                        custom_title TEXT,
                        custom_description TEXT,
                        custom_role TEXT,
                        -- Layout / presentation-only controls. These MUST NOT
                        -- change underlying verified analysis data.
                        display_order INTEGER,
                        highlight BOOLEAN,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_name, project_id)
                    );
                """)
                
                # Create index on user_name for faster lookups
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_portfolio_customizations_user_name 
                    ON portfolio_customizations(user_name);
                """)
                
                # Create index on project_id for faster lookups
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_portfolio_customizations_project_id 
                    ON portfolio_customizations(project_id);
                """)

                # Migrations for older schemas: add missing columns if necessary
                cursor.execute("""
                    DO $$
                    BEGIN
                        -- Ensure display_order exists
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'portfolio_customizations'
                              AND column_name = 'display_order'
                        ) THEN
                            ALTER TABLE portfolio_customizations
                            ADD COLUMN display_order INTEGER;
                        END IF;

                        -- Ensure highlight exists
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'portfolio_customizations'
                              AND column_name = 'highlight'
                        ) THEN
                            ALTER TABLE portfolio_customizations
                            ADD COLUMN highlight BOOLEAN;
                        END IF;
                    END $$;
                """)

                # Add foreign key constraint to user_informations
                cursor.execute("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.table_constraints 
                            WHERE constraint_name = 'fk_portfolio_customizations_user_name' 
                            AND table_name = 'portfolio_customizations'
                        ) THEN
                            ALTER TABLE portfolio_customizations
                            ADD CONSTRAINT fk_portfolio_customizations_user_name
                            FOREIGN KEY (user_name)
                            REFERENCES user_informations(user_name)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE;
                        END IF;
                    END $$;
                """)
            
            print("[SUCCESS] Portfolio customizations table initialized successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error initializing portfolio customizations table: {e}")
            return False
    
    @staticmethod
    def store_user_resume(user_name, resume_data):
        """
        Store or update a user-aggregated resume.
        
        Uses UPSERT logic (ON CONFLICT) to ensure only the latest version is stored.
        The resume_data parameter should contain aggregated information from top user projects
        including top projects, skills, portfolio metrics, and experience duration.
        
        Args:
            user_name (str): Username (string) to identify the user
            resume_data (dict): Aggregated resume data containing top projects and skills
            
        Returns:
            bool: True if storage successful, False otherwise
        """
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO generated_resumes (user_name, resume_data)
                    VALUES (%s, %s)
                    ON CONFLICT (user_name)
                    DO UPDATE SET 
                        resume_data = EXCLUDED.resume_data,
                        updated_at = CURRENT_TIMESTAMP
                """, (user_name, json.dumps(resume_data)))
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error storing user resume: {e}")
            return False
    
    @staticmethod
    def clear_custom_project_wording(user_id: str, project_id: int) -> bool:
        """
        Clear custom wording for a project resume item.
        Equivalent to saving an empty wording (fallback to stored/generated summary).
        """
        return ResumeManager.save_custom_project_wording(user_id, project_id, "")


    @staticmethod
    def list_custom_worded_projects(user_id: str) -> list[int]:
        """
        Return a list of project_ids that have custom resume wording saved.
        """
        try:
            existing = ResumeManager.get_user_resume(user_id)
            if not existing or "resume_data" not in existing:
                return []

            resume_data = existing.get("resume_data")

            if not isinstance(resume_data, dict):
                return []

            custom_map = resume_data.get("custom_project_wording", {}) or {}
            if not isinstance(custom_map, dict):
                return []

            project_ids: list[int] = []
            for k, v in custom_map.items():
                if isinstance(v, str) and v.strip():
                    try:
                        project_ids.append(int(k))
                    except Exception:
                        # ignore non-int keys
                        continue

            return sorted(project_ids)
        except Exception as e:
            print(f"[ERROR] Failed to list custom worded projects: {e}")
            return []


    @staticmethod
    def save_custom_project_wording(user_id: str, project_id: int, wording: str) -> bool:
        """
        Save or clear custom resume wording for a specific project.

        Stored under:
          resume_data["custom_project_wording"][str(project_id)] = wording
        """
        try:
            existing = ResumeManager.get_user_resume(user_id)

            resume_data = existing.get("resume_data") if existing else {}
            if not isinstance(resume_data, dict):
                resume_data = {}

            custom_map = resume_data.get("custom_project_wording", {})

            if not isinstance(custom_map, dict):
                custom_map = {}

            key = str(project_id)
            wording = (wording or "").strip()

            if wording:
                custom_map[key] = wording
            else:
                # empty wording clears customization
                custom_map.pop(key, None)

            resume_data["custom_project_wording"] = custom_map
            return ResumeManager.store_user_resume(user_id, resume_data)

        except Exception as e:
            print(f"[ERROR] Failed to save custom project wording: {e}")
            return False

    @staticmethod
    def save_portfolio_customization(user_name: str, project_id: int, custom_data: dict) -> bool:
        """
        Save or update portfolio customization for a specific project.
        
        Args:
            user_name (str): Username to identify the user
            project_id (int): Project ID
            custom_data (dict): Dictionary containing custom_title, custom_description, custom_role
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            custom_title = (custom_data.get('custom_title') or "").strip()
            custom_description = (custom_data.get('custom_description') or "").strip()
            custom_role = (custom_data.get('custom_role') or "").strip()
            display_order = custom_data.get('display_order')
            highlight = custom_data.get('highlight')
            
            with with_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO portfolio_customizations 
                        (user_name, project_id, custom_title, custom_description, custom_role, display_order, highlight)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_name, project_id)
                    DO UPDATE SET 
                        custom_title = EXCLUDED.custom_title,
                        custom_description = EXCLUDED.custom_description,
                        custom_role = EXCLUDED.custom_role,
                        display_order = EXCLUDED.display_order,
                        highlight = EXCLUDED.highlight,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    user_name,
                    project_id,
                    custom_title or None,
                    custom_description or None,
                    custom_role or None,
                    display_order,
                    highlight,
                ))
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save portfolio customization: {e}")
            return False
    
    @staticmethod
    def get_portfolio_customization(user_name: str, project_id: int) -> dict | None:
        """
        Retrieve portfolio customization for a specific project.
        
        Args:
            user_name (str): Username to identify the user
            project_id (int): Project ID
            
        Returns:
            dict: Dictionary containing custom_title, custom_description, custom_role, created_at, updated_at
                  Returns None if no customization exists
        """
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT custom_title,
                           custom_description,
                           custom_role,
                           display_order,
                           highlight,
                           created_at,
                           updated_at
                    FROM portfolio_customizations
                    WHERE user_name = %s AND project_id = %s
                """, (user_name, project_id))
                
                result = cursor.fetchone()
            
            if result:
                return {
                    'project_id': project_id,
                    'custom_title': result[0],
                    'custom_description': result[1],
                    'custom_role': result[2],
                    'display_order': result[3],
                    'highlight': result[4],
                    'created_at': result[5],
                    'updated_at': result[6],
                }
            return None
            
        except Exception as e:
            print(f"[ERROR] Failed to get portfolio customization: {e}")
            return None
    
    @staticmethod
    def list_customized_portfolio_projects(user_name: str) -> list[int]:
        """
        Return a list of project_ids that have portfolio customizations saved.
        
        Args:
            user_name (str): Username to identify the user
            
        Returns:
            list[int]: List of project IDs with customizations
        """
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT project_id
                    FROM portfolio_customizations
                    WHERE user_name = %s
                    ORDER BY project_id
                """, (user_name,))
                
                results = cursor.fetchall()
            
            return [row[0] for row in results]
            
        except Exception as e:
            print(f"[ERROR] Failed to list customized portfolio projects: {e}")
            return []
    
    @staticmethod
    def clear_portfolio_customization(user_name: str, project_id: int) -> bool:
        """
        Delete portfolio customization for a specific project.
        
        Args:
            user_name (str): Username to identify the user
            project_id (int): Project ID
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM portfolio_customizations
                    WHERE user_name = %s AND project_id = %s
                """, (user_name, project_id))
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to clear portfolio customization: {e}")
            return False

    @staticmethod
    def get_user_resume(user_name):
        """
        Retrieve the aggregated user resume.
        
        Fetches the most recent user resume from the database.
        Returns resume data along with creation and last update timestamps
        for tracking resume generation history.
        
        Args:
            user_name (str): Username (string) to identify the user
            
        Returns:
            dict: Dictionary containing resume_data, created_at, and updated_at
                  Returns None if no resume exists for the user
        """
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT resume_data, created_at, updated_at
                    FROM generated_resumes
                    WHERE user_name = %s
                """, (user_name,))
                
                result = cursor.fetchone()
            
            if result:
                resume_data = result[0]
                # Parse JSON if it's a string (PostgreSQL JSONB might return as dict or string depending on driver)
                if isinstance(resume_data, str):
                    resume_data = json.loads(resume_data)
                elif isinstance(resume_data, dict):
                    # Already parsed, use as is
                    pass
                else:
                    # Try to parse anyway
                    try:
                        resume_data = json.loads(str(resume_data))
                    except:
                        resume_data = result[0]
                
                return {
                    'resume_data': resume_data,
                    'created_at': result[1],
                    'updated_at': result[2]
                }
            return None
            
        except Exception as e:
            print(f"[ERROR] Error retrieving user resume: {e}")
            return None
    
    @staticmethod
    def delete_user_resume(user_name):
        """
        Delete a user's resume.
        
        Removes the user's resume from the database. This operation is typically
        triggered when a user withdraws consent (per requirement #1) or requests
        data deletion for privacy compliance.
        
        Args:
            user_name (str): Username (string) to identify the user
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM generated_resumes
                    WHERE user_name = %s
                """, (user_name,))
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error deleting user resume: {e}")
            return False
    
    @staticmethod
    def resume_exists(user_name):
        """
        Check if a resume exists for the given user.
        
        Useful for determining whether to generate a new resume
        or retrieve an existing one.
        
        Args:
            user_name (str): Username (string) to identify the user
            
        Returns:
            bool: True if resume exists, False otherwise
        """
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    SELECT 1 FROM generated_resumes WHERE user_name = %s
                """, (user_name,))
                
                result = cursor.fetchone()
            
            return result is not None
            
        except Exception as e:
            print(f"[ERROR] Error checking resume existence: {e}")
            return False
    
    @staticmethod
    def _detect_frameworks_from_files(file_contents):
        """
        Detect frameworks from file contents.
        
        Args:
            file_contents: List of file content dictionaries
            
        Returns:
            list: Detected frameworks
        """
        file_names = [f.get('file_name', '').lower() for f in file_contents]
        framework_indicators = {
            'React': ['package.json', 'react', '.jsx', '.tsx'],
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
            for indicator in indicators:
                for name in file_names:
                    if indicator.lower() in name:
                        detected_frameworks.add(framework)
                        break
        return sorted(list(detected_frameworks))
    
    @staticmethod
    def generate_user_resume(user_name, top_projects_count=5, selection: dict | None = None):
        """
        Generate a user-aggregated resume from top ranked projects.
        
        Leverages existing ranking system to identify top projects by score.
        Uses ProjectSummarizer to extract summary data from each top project.
        Aggregates skills, metrics, and project information for portfolio building.
        
        Args:
            user_name (str): Username (string) to identify the user
            top_projects_count (int): Number of top projects to include (default: 5)
            
        Returns:
            dict: Generated resume data containing top projects and aggregated skills
                  Returns None if generation fails or no projects exist
        """
        try:
            # Data Isolation: Rank only projects belonging to this user
            ranked_projects = rank_all_projects(user_name=user_name)
            
            if not ranked_projects:
                return None
            
            # ---- NEW: apply selection filters ----
            if selection:
                # allow overriding top_projects_count
                if "top_projects_count" in selection and isinstance(selection["top_projects_count"], int):
                    top_projects_count = selection["top_projects_count"]

                selected_ids = selection.get("selected_project_ids")
                if selected_ids:
                    ranked_projects = [p for p in ranked_projects if p.get("project_id") in selected_ids]
            # ---- END NEW ----

            top_projects = ranked_projects[:top_projects_count]
            
            # Collect all authors from top projects to let user select their name
            all_authors = set()
            for project in top_projects:
                try:
                    project_id = project['project_id']
                    file_contents = get_file_contents_by_upload_id(project_id)
                    authors = _identify_authors_from_zip(project_id) | _extract_common_names_from_filenames(file_contents)
                    all_authors.update(authors)
                except Exception:
                    continue
            
            # Get user's display name from detected authors (similar to choose_author_from_zip logic)
            display_name = user_name  # Default fallback
            if all_authors:
                git_username = get_user_git_username(user_name)
                if git_username and git_username in all_authors:
                    # Auto-select if git username matches
                    display_name = git_username
                else:
                    # Let user select their name from detected authors
                    authors_list = sorted(list(all_authors))
                    print(f"\n{'='*70}")
                    print("Select Your Name for Resume")
                    print(f"{'='*70}")
                    print("Detected author names from your projects:")
                    for idx, name in enumerate(authors_list, start=1):
                        print(f"  {idx}. {name}")
                    print(f"  {len(authors_list) + 1}. Use my login username: {user_name}")
                    print(f"  {len(authors_list) + 2}. Enter custom name")
                    
                    while True:
                        try:
                            choice = input("\nSelect an option: ").strip()
                            
                            if choice.isdigit():
                                choice_num = int(choice)
                                if 1 <= choice_num <= len(authors_list):
                                    display_name = authors_list[choice_num - 1]
                                    print(f"\nSelected: {display_name}")
                                    break
                                elif choice_num == len(authors_list) + 1:
                                    display_name = user_name
                                    print(f"\nUsing login username: {display_name}")
                                    break
                                elif choice_num == len(authors_list) + 2:
                                    custom_name = input("Enter your name: ").strip()
                                    if custom_name:
                                        display_name = custom_name
                                        print(f"\nUsing custom name: {display_name}")
                                        break
                                    else:
                                        print("Please enter a valid name.")
                                else:
                                    print(f"Please enter a number between 1 and {len(authors_list) + 2}.")
                            else:
                                print("Invalid input. Enter a number.")
                        except (ValueError, KeyboardInterrupt):
                            print("\nUsing default username.")
                            display_name = user_name
                            break
            else:
                # No authors detected, use login username or ask for custom name
                print(f"\nNo author names detected in projects.")
                use_custom = input("Enter your name for the resume (or press Enter to use login username): ").strip()
                if use_custom:
                    display_name = use_custom
                else:
                    display_name = user_name
            
            summarizer = ProjectSummarizer()
            skill_mapper = SkillMapper()
            
            # load custom project wording map
            custom_wording_map = {}
            try:
                existing_resume = ResumeManager.get_user_resume(user_name)
                if existing_resume and isinstance(existing_resume.get("resume_data"), dict):
                    custom_wording_map = existing_resume["resume_data"].get("custom_project_wording", {}) or {}
                    if not isinstance(custom_wording_map, dict):
                        custom_wording_map = {}
            except Exception:
                custom_wording_map = {}

            # Aggregated resume fields (always initialized to avoid NameError)
            all_skills: set = set()
            all_languages: set = set()
            all_frameworks: set = set()
            project_summaries: list = []
            
            include_skills = True
            skills_mode = "categorized"   # "categorized" or "all"

            if selection:
                include_skills = selection.get("include_skills", True)
                skills_mode = selection.get("skills_mode", "categorized")

            for project in top_projects:
                try:
                    project_id = project['project_id']
                    
                    # custom wording takes priority
                    custom_text = custom_wording_map.get(str(project_id), "")
                    project_summary_text = (custom_text or "").strip()

                    if not project_summary_text:
                        stored_ranking = get_stored_ranking_by_project_id(project_id)
                        project_summary_text = stored_ranking.get('summary', '') if stored_ranking else ''

                    if not project_summary_text:
                        try:
                            # Data Isolation: Pass user_name to verify project ownership
                            project_summary_text = summarize_project(project_id, user_name=user_name)
                        except Exception as e:
                            print(f"[WARNING] Could not generate summary for project {project_id}: {e}")
                            project_summary_text = ''
                    
                    # Get comprehensive summary for additional data
                    # Data Isolation: Pass user_name to verify project ownership
                    summary = summarizer.generate_project_summary(project_id, user_name=user_name)
                    
                    if summary and 'error' not in summary:
                        # Extract languages
                        languages_data = summary.get('languages', {})
                        project_languages = languages_data.get('languages', [])
                        primary_language = languages_data.get('primary_language', 'Unknown')
                        all_languages.update(project_languages)
                        
                        # Get timeline info
                        time_analysis = summary.get('time_analysis', {})
                        duration_days = time_analysis.get('duration_days', 0)
                        intensity = time_analysis.get('intensity', 'Unknown')
                        first_file = time_analysis.get('first_file', '')
                        last_file = time_analysis.get('last_file', '')
                        
                        # Get collaboration info
                        collab_analysis = summary.get('collaboration_analysis', {})
                        collaboration_level = collab_analysis.get('collaboration_level', 'Unknown')
                        
                        # Get file contents for framework detection
                        file_contents = get_file_contents_by_upload_id(project_id)
                        frameworks = ResumeManager._detect_frameworks_from_files(file_contents)
                        all_frameworks.update(frameworks)
                        
                        # Only collect skills if enabled
                        if include_skills:
                            # Extract skills from deep analysis
                            code_analysis = summary.get('code_analysis', {})
                            deep_analysis_skills = skill_mapper.extract_skills_from_deep_analysis(code_analysis)

                            # Combine all skills for this project
                            project_skills = set(project_languages)
                            project_skills.update(frameworks)
                            project_skills.update(deep_analysis_skills)

                            # all_skills is initialized before the loop (aggregates skills across projects)
                            all_skills.update(project_skills)
                        else:
                            # Still keep per-project skills key stable, but empty
                            project_skills = set()
                        
                        # Clean project name
                        project_name = project['filename']
                        # Remove common suffixes and extensions
                        clean_name = project_name
                        # Remove file extensions
                        if clean_name.endswith('.zip'):
                            clean_name = clean_name[:-4]
                        # Remove common git suffixes
                        clean_name = clean_name.replace('-master', '').replace('-main', '').replace('-main.zip', '')
                        # Replace underscores and hyphens with spaces
                        clean_name = clean_name.replace('_', ' ').replace('-', ' ')
                        # Title case and clean up multiple spaces
                        clean_name = ' '.join(clean_name.split()).title()
                        # If name is empty or too short, use original
                        if not clean_name or len(clean_name) < 2:
                            clean_name = project_name.replace('.zip', '')
                        
                        # Optional: gather file stats for evidence (LOC, file count)
                        file_stats = {}
                        try:
                            file_stats = get_file_statistics(project_id) or {}
                        except Exception:
                            file_stats = {}
                        

                        evidence = build_evidence(
                            {
                                "languages": {"languages": project_languages, "primary_language": primary_language},
                                "frameworks": frameworks,
                                "time_analysis": {
                                    "duration_days": duration_days,
                                    "intensity": intensity,
                                    "first_file": first_file,
                                    "last_file": last_file,
                                },
                                "collaboration_analysis": {"collaboration_level": collaboration_level},
                                "code_analysis": summary.get("code_analysis", {}),
                                "project_info": summary.get("project_info", {}),
                                "project_structure": summary.get("project_structure", {}),
                                "file_statistics": file_stats,
                            }
                        )

                        # Build enriched project summary for resume
                        project_summaries.append({
                            'project_name': clean_name,
                            'project_id': project_id,
                            'primary_language': primary_language,
                            'languages': project_languages,
                            'frameworks': frameworks,
                            'skills': sorted(list(project_skills))[:15],
                            'duration_days': duration_days,
                            'intensity': intensity,
                            'first_file': first_file,
                            'last_file': last_file,
                            'collaboration_level': collaboration_level,
                            'summary': project_summary_text,  # Use stored summary from database
                            'project_info': summary.get('project_info', {}),
                            'evidence': evidence
                        })
                
                except Exception as e:
                    print(f"[ERROR] Failed to summarize project {project['project_id']}: {e}")
                    continue
            
            # Categorize skills (respect selection)
            if include_skills:
                all_skills_list = sorted(list(all_skills))
                if skills_mode == "categorized":
                    # SkillMapper expects a set for set operations (e.g., set difference)
                    categorized_skills = skill_mapper.categorize_skills(all_skills)
                else:
                    categorized_skills = {}
            else:
                all_skills_list = []
                categorized_skills = {}
            
            # Build comprehensive resume data
            resume_data = {
                'display_name': display_name,
                'user_name': user_name,
                'total_projects_analyzed': len(ranked_projects),
                'top_projects_displayed': len(project_summaries),
                'all_skills': all_skills_list,
                'categorized_skills': categorized_skills,
                'languages': sorted(list(all_languages)),
                'frameworks': sorted(list(all_frameworks)),
                'top_projects': project_summaries,
                'generated_at': datetime.now().isoformat()
            }
            
            return resume_data
            
        except Exception as e:
            print(f"[ERROR] Error generating user resume: {e}")
            return None
