"""
Project Manager Module

Manages project listing and retrieval operations.
Supports both alphabetical and chronological ordering of projects.
"""
import json
import os
from config.db_config import with_db_cursor
from config.db_config import with_db_connection
from account.user_manager import AuthManager

def _table_exists(cursor, table_name: str) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = %s
        """,
        (table_name,),
    )
    return cursor.fetchone() is not None

def list_projects(user_name=None):
    """
    List all stored projects (ZIP files) for a specific user in alphabetical order.
    Data Isolation: Only returns projects belonging to the specified user.
    
    Args:
        user_name (str, optional): Username to filter projects by. If None, uses current user.
    
    Returns:
        list: List of project dictionaries with id, filename, created_at, and file_count.
    """
    # Get current user if user_name not provided
    if user_name is None:
        user_name = AuthManager.get_current_username()
        if not user_name:
            print("No user is currently logged in.")
            return []
    
    try:
        with with_db_cursor() as cursor:
            # Data Isolation: Filter projects by user_name to ensure users only see their own data
            cursor.execute("""
                SELECT id, filename, status, metadata, created_at, thumbnail
                FROM uploaded_files
                WHERE user_name = %s
                ORDER BY filename ASC
            """, (user_name,))
            projects = cursor.fetchall()
        
        # if there are no projects, return an empty list
        if not projects:
            print("No projects found in database.")
            return []
        
        print("-"*80)
        print("Stored Projects (Alphabetical Order)")  
        print("-"*80)
        
        project_list = []
        
        for project in projects:
            project_id, filename, status, metadata, created_at, thumbnail = project
            
            # Count files in metadata if available
            file_count = 0
            if metadata:
                try:
                    metadata_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
                    if 'files' in metadata_dict and metadata_dict['files']:
                        # Count only actual files (not directories)
                        actual_files = [f for f in metadata_dict['files'] if not f.endswith('/')]
                        file_count = len(actual_files)
                except (json.JSONDecodeError, TypeError):
                    pass
            
            has_thumbnail = thumbnail is not None

            project_list.append({
                'id': project_id,
                'filename': filename,
                'created_at': created_at,
                'file_count': file_count,
                'has_thumbnail': has_thumbnail
            })
            
            # Display project info
            created_date = created_at.strftime("%Y-%m-%d") if created_at else "Unknown"
            print(f"\n{len(project_list)}. {filename}")
            thumbnail_label = "Yes" if has_thumbnail else "No"
            print(f"   ID: {project_id}, Created: {created_date}, Files: {file_count}, Thumbnail: {thumbnail_label}")
        
        print("\n" + "-"*80)
        print(f"Total projects: {len(project_list)}")
        print("-"*80)
        
        return project_list
        
    except ConnectionError:
        print("Could not connect to database.")
        return []


def delete_project(project_id, user_name=None):
    """
    Delete a stored project and its related data for a specific user.
    Data Isolation: Only deletes projects belonging to the specified user.

    Args:
        project_id (int): The ID of the project to delete
        user_name (str, optional): Username to verify project ownership. If None, uses current user.

    Returns:
        dict: Result information including deleted counts and file removal status.
    """
    if user_name is None:
        user_name = AuthManager.get_current_username()
        if not user_name:
            print("No user is currently logged in.")
            return {"success": False, "error": "Not logged in"}

    try:
        with with_db_connection() as (conn, cursor):
            cursor.execute("""
                SELECT id, filename, filepath
                FROM uploaded_files
                WHERE id = %s AND user_name = %s
            """, (project_id, user_name))
            project = cursor.fetchone()

            if not project:
                print(f"Project with ID {project_id} not found.")
                return {"success": False, "error": "Project not found"}

            _, filename, filepath = project

            deleted = {
                "project_metrics": 0,
                "analysis_results": 0,
                "project_rankings": 0,
                "file_contents": 0,
                "uploaded_files": 0,
            }

            if _table_exists(cursor, "project_metrics"):
                cursor.execute("DELETE FROM project_metrics WHERE project_id = %s;", (project_id,))
                deleted["project_metrics"] = cursor.rowcount or 0

            if _table_exists(cursor, "analysis_results"):
                cursor.execute("DELETE FROM analysis_results WHERE uploaded_file_id = %s;", (project_id,))
                deleted["analysis_results"] = cursor.rowcount or 0

            if _table_exists(cursor, "project_rankings"):
                cursor.execute("DELETE FROM project_rankings WHERE project_id = %s;", (project_id,))
                deleted["project_rankings"] = cursor.rowcount or 0

            if _table_exists(cursor, "file_contents"):
                cursor.execute("DELETE FROM file_contents WHERE uploaded_file_id = %s;", (project_id,))
                deleted["file_contents"] = cursor.rowcount or 0

            cursor.execute("""
                DELETE FROM uploaded_files
                WHERE id = %s AND user_name = %s
            """, (project_id, user_name))
            deleted["uploaded_files"] = cursor.rowcount or 0

        file_deleted = False
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                file_deleted = True
            except Exception as e:
                print(f"[WARN] Failed to remove uploaded file '{filepath}': {e}")

        return {
            "success": True,
            "project_id": project_id,
            "filename": filename,
            "filepath": filepath,
            "deleted": deleted,
            "file_deleted": file_deleted,
        }
    except ConnectionError:
        print("Could not connect to database.")
        return {"success": False, "error": "Database connection failed"}
    except Exception as e:
        print(f"Error deleting project: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"Error retrieving projects: {e}")
        return []


def list_project_files(project_id, user_name=None):
    """
    List individual files within a specific project.
    Data Isolation: Verifies project belongs to the user before returning files.
    
    Args:
        project_id (int): The ID of the project to list files for
        user_name (str, optional): Username to verify project ownership. If None, uses current user.
        
    Returns:
        list: List of file paths/names in the project
    """
    # Get current user if user_name not provided
    if user_name is None:
        user_name = AuthManager.get_current_username()
        if not user_name:
            print("No user is currently logged in.")
            return []
    
    try:
        with with_db_cursor() as cursor:
            # Data Isolation: Verify project belongs to the specified user
            cursor.execute("""
                SELECT metadata
                FROM uploaded_files
                WHERE id = %s AND user_name = %s
            """, (project_id, user_name))
            
            result = cursor.fetchone()
            
            if not result:
                print(f"Project with ID {project_id} not found.")
                return []
            
            metadata = result[0]
            
            if not metadata:
                print("No file metadata available for this project.")
                return []
            
            try:
                metadata_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
                if 'files' in metadata_dict and metadata_dict['files']:
                    # Filter out directories and return actual files
                    actual_files = [f for f in metadata_dict['files'] if not f.endswith('/')]
                    return actual_files
                else:
                    print("No files found in project metadata.")
                    return []
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error parsing project metadata: {e}")
                return []
                
    except ConnectionError:
        print("Could not connect to database.")
        return []
    except Exception as e:
        print(f"Error retrieving project files: {e}")
        return []

# this function will get a project by its id
def get_project_by_id(project_id, user_name=None):
    """
    Get a project by its ID for a specific user.
    Data Isolation: Only returns project if it belongs to the specified user.
    
    Args:
        project_id (int): The ID of the project to retrieve
        user_name (str, optional): Username to verify project ownership. If None, uses current user.
        
    Returns:
        dict: Project information or None if not found or access denied
    """
    # Get current user if user_name not provided
    if user_name is None:
        user_name = AuthManager.get_current_username()
        if not user_name:
            print("No user is currently logged in.")
            return None
    
    try:
        with with_db_cursor() as cursor:
            # Data Isolation: Verify project belongs to the specified user
            cursor.execute("""
                SELECT id, filename, filepath, status, metadata, created_at
                FROM uploaded_files
                WHERE id = %s AND user_name = %s
            """, (project_id, user_name))
            
            project = cursor.fetchone()
        
        if not project:
            print(f"Project with ID {project_id} not found.")
            return None
        
        project_id, filename, filepath, status, metadata, created_at = project
        
        # return the project information
        return {
            'id': project_id,
            'filename': filename,
            'filepath': filepath,
            'status': status,
            'metadata': metadata,
            'created_at': created_at
        }
        
    except ConnectionError:
        print("Could not connect to database.")
        return None
    except Exception as e:
        print(f"Error retrieving project: {e}")
        return None

# this function will get the total number of projects in the database
def get_project_count(user_name=None):
    """
    Get the total number of projects for a specific user.
    Data Isolation: Only counts projects belonging to the specified user.
    
    Args:
        user_name (str, optional): Username to filter projects by. If None, uses current user.
        
    Returns:
        int: Number of projects owned by the user
    """
    # Get current user if user_name not provided
    if user_name is None:
        user_name = AuthManager.get_current_username()
        if not user_name:
            return 0
    
    try:
        with with_db_cursor() as cursor:
            # Data Isolation: Count only projects belonging to the specified user
            cursor.execute("""
                SELECT COUNT(*) 
                FROM uploaded_files 
                WHERE user_name = %s
            """, (user_name,))
            count = cursor.fetchone()[0]
        return count
        
    except ConnectionError:
        print("Could not connect to database.")
        return 0
    except Exception as e:
        print(f"Error getting project count: {e}")
        return 0


def list_projects_chronologically(user_name=None):
    """
    List all stored projects (ZIP files) for a specific user in chronological order by creation date.
    Data Isolation: Only returns projects belonging to the specified user.
    Requirement: Produce a chronological list of projects.
    
    Args:
        user_name (str, optional): Username to filter projects by. If None, uses current user.
    
    Returns:
        list: List of project dictionaries with id, filename, created_at, and file_count,
              ordered by created_at ascending (oldest first).
    """
    # Get current user if user_name not provided
    if user_name is None:
        user_name = AuthManager.get_current_username()
        if not user_name:
            print("No user is currently logged in.")
            return []
    
    try:
        with with_db_cursor() as cursor:
            # Data Isolation: Filter projects by user_name to ensure users only see their own data
            cursor.execute("""
                SELECT id, filename, status, metadata, created_at
                FROM uploaded_files
                WHERE user_name = %s
                ORDER BY created_at ASC
            """, (user_name,))
            projects = cursor.fetchall()
        
        # if there are no projects, return an empty list
        if not projects:
            print("No projects found in database.")
            return []
        
        print("-"*80)
        print("Stored Projects (Chronological Order - Oldest First)")  
        print("-"*80)
        
        project_list = []
        
        for project in projects:
            project_id, filename, status, metadata, created_at = project
            
            # Count files in metadata if available
            file_count = 0
            if metadata:
                try:
                    metadata_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
                    if 'files' in metadata_dict and metadata_dict['files']:
                        # Count only actual files (not directories)
                        actual_files = [f for f in metadata_dict['files'] if not f.endswith('/')]
                        file_count = len(actual_files)
                except (json.JSONDecodeError, TypeError):
                    pass
            
            project_list.append({
                'id': project_id,
                'filename': filename,
                'created_at': created_at,
                'file_count': file_count
            })
            
            # Display project info
            created_date = created_at.strftime("%Y-%m-%d") if created_at else "Unknown"
            print(f"\n{len(project_list)}. {filename}")
            print(f"   ID: {project_id}, Created: {created_date}, Files: {file_count}")
        
        print("\n" + "-"*80)
        print(f"Total projects: {len(project_list)}")
        print("-"*80)
        
        return project_list
        
    except ConnectionError:
        print("Could not connect to database.")
        return []
    except Exception as e:
        print(f"Error retrieving projects chronologically: {e}")
        return []
