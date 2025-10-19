import os
import shutil
import zipfile
import json
from config.db_config import get_connection
from parsing.file_validator import validate_uploaded_file, WrongFormatError

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
        """, (filename, dest_path, "uploaded", json.dumps({"files": file_contents})))
        
        conn.commit()
        print("File metadata saved to database.")
    except Exception as e:
        print(f"Error saving to database: {e}")
        conn.rollback()
    finally:
        conn.close()