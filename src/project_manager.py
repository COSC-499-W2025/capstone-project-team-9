# this file will list the projects in the database uploaded_files table. 
# it will list the projects in alphabetical order.
# it will also list the individual files in the projects if there are any.
import json
from config.db_config import get_connection


def list_projects():

    conn = get_connection()
    if not conn:
        print("Could not connect to database.")
        return []
# get the projects from the database
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, status, metadata, created_at
            FROM uploaded_files
            ORDER BY filename ASC
        """)
        projects = cursor.fetchall()
        cursor.close()
# if there are no projects, return an empty list
        if not projects:
            print("No projects found in database.")
            return []
        print("-"*80)
        print("Stored Projects (Alphabetical Order)")  
        print("-"*80)
        individual_projects = []
        
        for project in projects:
            project_id, filename, status, metadata, created_at = project
            
     # if there is metadata, try to extract the individual files
            if metadata:
                try:
                    metadata_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
                    if 'files' in metadata_dict and metadata_dict['files']:
# since we only want to list the individual files, we need to filter out the directories
                        actual_files = []
                        for file in metadata_dict['files']:
                            if not file.endswith('/'):
                                # Extract just the filename (last part after '/')
                                individual_filename = file.split('/')[-1]
                                actual_files.append(individual_filename)
                        
                        # Add each file as a separate project entry
                        for individual_file in actual_files:
                            individual_projects.append({
                                'zip_name': filename,
                                'file_name': individual_file,
                                'project_id': project_id,
                                'created_at': created_at
                            })
                    else:
                        #this is a base case that will just show the zip file and list that as the project. unlikely to happen
                        # If no files, add the ZIP itself as a project
                        individual_projects.append({
                            'zip_name': filename,
                            'file_name': filename,
                            'project_id': project_id,
                            'created_at': created_at
                        })
                except (json.JSONDecodeError, TypeError):
                    # If metadata error, add the ZIP itself as a project
                    individual_projects.append({
                        'zip_name': filename,
                        'file_name': filename,
                        'project_id': project_id,
                        'created_at': created_at
                    })
            else:
                # If no metadata, add the ZIP itself as a project
                individual_projects.append({
                    'zip_name': filename,
                    'file_name': filename,
                    'project_id': project_id,
                    'created_at': created_at
                })
        
        # Sort individual projects by filename
        individual_projects.sort(key=lambda x: x['file_name'])
        
        # Display individual projects
        for project in individual_projects:
            print(f"\nProject: {project['file_name']}")
            if project['file_name'] != project['zip_name']:
                print(f"From: {project['zip_name']}")
        
        print("\n" + "-"*80)
        print(f"Total individual projects: {len(individual_projects)}")
        print(f"Total ZIP files: {len(projects)}")
        print("-"*80)
        
        return projects
        
    except Exception as e:
        print(f"Error retrieving projects: {e}")
        return []
    finally:
        conn.close()

# this function will get a project by its id
def get_project_by_id(project_id):

    conn = get_connection()
    # if the connection is not successful, return None
    if not conn:
        print("Could not connect to database.")
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, filepath, status, metadata, created_at
            FROM uploaded_files
            WHERE id = %s
        """, (project_id,))
        
        project = cursor.fetchone()
        cursor.close()
        
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
        
    except Exception as e:
        print(f"Error retrieving project: {e}")
        return None
    finally:
        conn.close()

# this function will get the total number of projects in the database
def get_project_count():

    conn = get_connection()
    if not conn:
        print("Could not connect to database.")
        return 0
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM uploaded_files")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
        
    except Exception as e:
        print(f"Error getting project count: {e}")
        return 0
    finally:
        conn.close()
