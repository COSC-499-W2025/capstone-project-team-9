import os
import shutil
import zipfile
import json
from config.db_config import get_connection
from parsing.file_validator import validate_uploaded_file, WrongFormatError
from parsing.file_contents_manager import init_file_contents_table, extract_and_store_file_contents, get_file_contents_by_upload_id

UPLOAD_FOLDER = "data/uploads"

class UploadResult:
    """Encapsulates the result of an upload operation"""
    def __init__(self, success: bool, message: str, error_type: str = None, data: dict = None):
        self.success = success
        self.message = message
        self.error_type = error_type
        self.data = data or {}
    
    def to_dict(self):
        """Convert to dictionary format for UI consumption"""
        return {
            "success": self.success,
            "message": self.message,
            "error_type": self.error_type,
            "data": self.data
        }

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
        print(" Uploaded files table initialized")
        
        # Also initialize the file contents table
        init_file_contents_table()
        
    except Exception as e:
        conn.rollback()
        print(f" Error initializing uploaded_files table: {e}")
        raise
    finally:
        conn.close()

def add_file_to_db(filepath) -> UploadResult:
    """
    Upload file to database with comprehensive error handling
    
    Args:
        filepath: Path to the file to upload
        
    Returns:
        UploadResult: Object containing success status, message, error type, and data
    """
    # 1. Check if file exists
    if not os.path.exists(filepath):
        return UploadResult(
            success=False,
            message=f"File does not exist: {filepath}",
            error_type="FILE_NOT_FOUND"
        )
    
    # 2. Validate file format
    try:
        validate_uploaded_file(filepath)
    except WrongFormatError as e:
        return UploadResult(
            success=False,
            message=f"Invalid file format: {str(e)}",
            error_type="INVALID_FORMAT",
            data={"filepath": filepath}
        )
    
    filename = os.path.basename(filepath)
    dest_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # 3. Create upload directory
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    except Exception as e:
        return UploadResult(
            success=False,
            message=f"Failed to create upload directory: {str(e)}",
            error_type="DIRECTORY_ERROR"
        )
    
    # 4. Copy file to upload folder
    try:
        shutil.copy(filepath, dest_path)
        print(f"File copied to {dest_path}")
    except Exception as e:
        return UploadResult(
            success=False,
            message=f"File copy failed: {str(e)}",
            error_type="COPY_ERROR",
            data={"source": filepath, "destination": dest_path}
        )
    
    # 5. Extract metadata from zip
    file_contents = []
    try:
        if zipfile.is_zipfile(dest_path):
            with zipfile.ZipFile(dest_path, 'r') as zip_ref:
                file_contents = zip_ref.namelist()
            print(f"Files inside zip: {file_contents}")
    except Exception as e:
        return UploadResult(
            success=False,
            message=f"ZIP file extraction failed: {str(e)}",
            error_type="ZIP_EXTRACTION_ERROR",
            data={"filepath": dest_path}
        )
    
    # 6. Connect to database
    conn = get_connection()
    if not conn:
        return UploadResult(
            success=False,
            message="Could not connect to database",
            error_type="DATABASE_CONNECTION_ERROR"
        )
    
    # 7. Save to database
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO uploaded_files (filename, filepath, status, metadata)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (filename, dest_path, "uploaded", json.dumps({"files": file_contents})))
        
        uploaded_file_id = cur.fetchone()[0]
        conn.commit()
        
        # Extract and store file contents
        print("Extracting file contents...")
        extraction_result = extract_and_store_file_contents(uploaded_file_id, dest_path)

        return UploadResult(
            success=True,
            message=f"File '{filename}' uploaded successfully!",
            error_type=None,
            data={
                "file_id": uploaded_file_id,
                "filename": filename,
                "filepath": dest_path,
                "file_count": len(file_contents),
                "files": file_contents
            }
        )

    except Exception as e:
        conn.rollback()
        return UploadResult(
            success=False,
            message=f"Database save failed: {str(e)}",
            error_type="DATABASE_SAVE_ERROR",
            data={"filename": filename}
        )
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
        if cursor:
            cursor.close()
        if conn:
            conn.close()
