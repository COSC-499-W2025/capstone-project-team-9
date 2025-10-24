import os
import shutil
import zipfile
import json
from config.db_config import get_connection
from parsing.file_validator import validate_uploaded_file, WrongFormatError
from parsing.file_contents_manager import init_file_contents_table, extract_and_store_file_contents, get_file_contents_by_upload_id

UPLOAD_FOLDER = "data/uploads"

def init_uploaded_files_table():
    """Create the uploaded_files table if it doesn't exist."""
    conn = get_connection()
    if not conn:
        raise Exception("Failed to connect to database")
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploaded_files (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                filepath VARCHAR(500) NOT NULL,
                status VARCHAR(50) DEFAULT 'uploaded',
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        print("✓ Uploaded files table initialized")
        
        # Also initialize the file contents table
        init_file_contents_table()
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error initializing uploaded_files table: {e}")
        raise
    finally:
        conn.close()

def add_file_to_db(filepath):
    if not os.path.exists(filepath):
        print("File does not exist.")
        return
    
    # Validate file format
    try:
        validate_uploaded_file(filepath)
    except WrongFormatError as e:
        print(f"Invalid file format: {e}")
        return
    
    filename = os.path.basename(filepath)
    dest_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Copy file to upload folder
    shutil.copy(filepath, dest_path)
    print(f"File copied to {dest_path}")
    
    # Extract metadata from zip
    file_contents = []
    if zipfile.is_zipfile(dest_path):
        with zipfile.ZipFile(dest_path, 'r') as zip_ref:
            file_contents = zip_ref.namelist()
        print(f"Files inside zip: {file_contents}")
    
    # Store in database
    conn = get_connection()
    if not conn:
        print("Could not connect to database.")
        return
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO uploaded_files (filename, filepath, status, metadata)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (filename, dest_path, "uploaded", json.dumps({"files": file_contents})))
        
        uploaded_file_id = cur.fetchone()[0]
        conn.commit()
        print("File metadata saved to database.")
        
        # Extract and store file contents
        print("Extracting file contents...")
        extraction_result = extract_and_store_file_contents(uploaded_file_id, dest_path)
        
        if extraction_result["success"]:
            print(f"✓ Successfully extracted {extraction_result['total_files']} files")
            if extraction_result["errors"]:
                print(f"⚠ {len(extraction_result['errors'])} files had errors during extraction")
        else:
            print(f"✗ Error extracting file contents: {extraction_result['error']}")
        
    except Exception as e:
        print(f"Error saving to database: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_uploaded_file_contents(uploaded_file_id):
    """
    Retrieve all file contents for a specific uploaded file.
    
    Args:
        uploaded_file_id (int): The ID of the uploaded file record
    
    Returns:
        list: List of file content records
    """
    return get_file_contents_by_upload_id(uploaded_file_id)


def list_uploaded_files():
    """
    Get a list of all uploaded files with their metadata.
    
    Returns:
        list: List of uploaded file records
    """
    conn = get_connection()
    if not conn:
        print("Could not connect to database.")
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, filepath, status, metadata, created_at
            FROM uploaded_files
            ORDER BY created_at DESC
        """)
        
        results = cursor.fetchall()
        files = []
        
        for row in results:
            files.append({
                "id": row[0],
                "filename": row[1],
                "filepath": row[2],
                "status": row[3],
                "metadata": row[4],
                "created_at": row[5]
            })
        
        return files
        
    except Exception as e:
        print(f"Error retrieving uploaded files: {e}")
        return []
    finally:
        cursor.close()
        conn.close()