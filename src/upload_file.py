import os
import shutil
import zipfile
import json
from config.db_config import with_db_cursor
from parsing.file_validator import validate_uploaded_file, WrongFormatError
from parsing.file_contents_manager import (
    init_file_contents_table,
    extract_and_store_file_contents,
    get_file_contents_by_upload_id,
)
from pathlib import Path

UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", "data/uploads"))

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and other security issues.
    
    Args:
        filename: The original filename
        
    Returns:
        A sanitized filename safe for use in file paths
    """
    if not filename:
        return "upload.zip"
    
    # Extract just the basename to remove any path components
    basename = os.path.basename(filename)
    
    # Limit length to 255 characters (database constraint)
    if len(basename) > 255:
        name, ext = os.path.splitext(basename)
        # Truncate name part, keeping extension
        basename = name[:255 - len(ext)] + ext
    
    return basename

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
def ensure_upload_dir() -> str | None:
    try:
        UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        return None
    except Exception as e:
        # Return a user-friendly error message
        return f"Failed to create upload directory '{UPLOAD_FOLDER}': {e}"

def init_uploaded_files_table():
    """Create the uploaded_files table if it doesn't exist, and ensure new columns exist."""
    try:
        # 1) Create the table (create it only if it does not exist)
        with with_db_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_files (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    filepath VARCHAR(500) NOT NULL,
                    status VARCHAR(50) DEFAULT 'uploaded',
                    metadata JSONB,
                    thumbnail BYTEA,
                    file_data BYTEA,
                    contributor_name VARCHAR(255),
                    user_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_user_name
                        FOREIGN KEY (user_name)
                        REFERENCES user_informations(user_name)
                        ON DELETE SET NULL
                        ON UPDATE CASCADE
                );
            """)
        print(" Uploaded files table initialized")

        # 2) Migration: Automatically add missing columns to the old table
        try:
            with with_db_cursor() as cursor:
                # The old database may not have file_data.
                cursor.execute("""
                    ALTER TABLE uploaded_files
                    ADD COLUMN IF NOT EXISTS file_data BYTEA;
                """)

                # The old database may not have thumbnail.
                cursor.execute("""
                    ALTER TABLE uploaded_files
                    ADD COLUMN IF NOT EXISTS thumbnail BYTEA;
                """)

                # The old database may not have last_modified_at.
                cursor.execute("""
                    ALTER TABLE uploaded_files
                    ADD COLUMN IF NOT EXISTS last_modified_at TIMESTAMP;
                """)
                # The old database may not have contributor_name.
                cursor.execute("""
                    ALTER TABLE uploaded_files
                    ADD COLUMN IF NOT EXISTS contributor_name VARCHAR(255);
                """)

                # The old database may not have user_name.
                cursor.execute("""
                    ALTER TABLE uploaded_files
                    ADD COLUMN IF NOT EXISTS user_name VARCHAR(255);
                """)
                # For duplicate check without loading full zip into DB query
                cursor.execute("""
                    ALTER TABLE uploaded_files
                    ADD COLUMN IF NOT EXISTS file_data_size BIGINT NULL;
                """)

                # Add foreign key constraint if it doesn't exist
                cursor.execute("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'fk_user_name'
                        ) THEN
                            ALTER TABLE uploaded_files
                            ADD CONSTRAINT fk_user_name
                                FOREIGN KEY (user_name)
                                REFERENCES user_informations(user_name)
                                ON DELETE SET NULL
                                ON UPDATE CASCADE;
                        END IF;
                    END $$;
                """)

                # Initialize the history's last_modified_at to created_at (only accept NULL).
                cursor.execute("""
                    UPDATE uploaded_files
                    SET last_modified_at = COALESCE(last_modified_at, created_at)
                    WHERE last_modified_at IS NULL;
                """)

                # Create index on user_name for faster lookups (after column is added)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_uploaded_files_user_name 
                    ON uploaded_files(user_name);
                """)

        except Exception as e:
            # If the migration fails, only print a warning to prevent the program from crashing.
            print(f" [WARN] Skipping uploaded_files migration: {e}")

        # 3) Initialize / migrate the file_contents table
        init_file_contents_table()

    except ConnectionError:
        raise Exception("Failed to connect to database")
    except Exception as e:
        print(f" Error initializing uploaded_files table: {e}")
        raise


def add_file_to_db(filepath, user_name: str = None, original_filename: str = None) -> UploadResult:
    # 1. Check if file exists
    # Return detailed error if not found
    if not os.path.exists(filepath):
        return UploadResult(
            success=False,
            message=(
                f"File does not exist: {filepath}. "
                "Please double-check the path and try again."
            ),
            error_type="FILE_NOT_FOUND",
            data={"filepath": filepath},
        )

    # Obtain the filename in advance for easier use in error messages.
    # Use original_filename if provided (from web upload), otherwise use basename
    # Sanitize the filename to prevent security issues
    if original_filename:
        filename = sanitize_filename(original_filename)
    else:
        filename = os.path.basename(filepath)

    # 2. Validate file format (extension, size, etc.)
    try:
        validate_uploaded_file(filepath)
    except WrongFormatError as e:
        # Customized more user-friendly prompts based on error content.
        raw_msg = str(e)
        lower_msg = raw_msg.lower()

        # If the validator tells us "not a valid zip", provide specific guidance.
        if "not a valid zip archive" in lower_msg or "not a valid zip" in lower_msg:
            friendly_msg = (
                f"File '{filename}' has a .zip extension but is not a valid ZIP archive. "
                "This often happens when a RAR/7z file is renamed to .zip. "
                "Please re-compress your project using the standard ZIP format "
                "(for example, Windows 'Send to → Compressed (zipped) folder' "
                "or macOS 'Compress') and upload again."
            )
            return UploadResult(
                success=False,
                message=friendly_msg,
                error_type="INVALID_ZIP",
                data={"filepath": filepath},
            )
        
        # For other types of WrongFormatError, retain the original message
        # String together the validator information to let the user know which formats are supported.
        return UploadResult(
            success=False,
            message=(
                "Invalid file format. "
                f"{str(e)}"
            ),
            error_type="INVALID_FORMAT",
            data={"filepath": filepath},
        )

    # 3. Prepare destination path
    dest_path = str(UPLOAD_FOLDER / filename)   # keep as str if the rest of your code expects str

    # 4. Create upload directory (via helper)
    err = ensure_upload_dir()
    if err:
        return UploadResult(
            success=False,
            message=err,
            error_type="DIRECTORY_ERROR",
            data={"destination": str(UPLOAD_FOLDER)}
        )

    # 5. Copy file to upload folder
    try:
        shutil.copy(filepath, dest_path)
        print(f"File copied to {dest_path}")
    except Exception as e:
        # More user-friendly error message
        return UploadResult(
            success=False,
            message=(
                f"File copy failed: {e}. "
                "Please make sure you have read permission on the source file "
                "and write permission to the uploads folder."
            ),
            error_type="COPY_ERROR",
            data={"source": filepath, "destination": dest_path},
        )

    # 5.5 Key Change
    # To prevent RAR/7z files from crashing after simply changing the extension to .zip.
    if not zipfile.is_zipfile(dest_path):
        return UploadResult(
            success=False,
            message=(
                f"File '{filename}' has a .zip extension but is not a valid ZIP archive. "
                "Please re-compress your project using the standard ZIP format "
                "and upload again."
            ),
            error_type="INVALID_ZIP",
            data={"filepath": dest_path},
        )
    
    # 6. Extract metadata from zip
    file_contents = []
    try:
        # This has already been confirmed as a valid ZIP file, so the is_zipfile check will not be performed again.
            with zipfile.ZipFile(dest_path, 'r') as zip_ref:
                file_contents = zip_ref.namelist()
            print(f"Files inside zip: {file_contents}")
    except Exception as e:
        # More user-friendly error message
        return UploadResult(
            success=False,
            message=(
                f"ZIP file extraction failed for '{filename}': {e}. "
                "The archive might be corrupted. "
                "Please re-create the ZIP file and try uploading again."
            ),
            error_type="ZIP_EXTRACTION_ERROR",
            data={"filepath": dest_path},
        )

    # 6. Check for duplicate uploads and save to database
    try:
        zip_size = os.path.getsize(dest_path)
        with with_db_cursor() as cursor:
            # 6.1 Duplicate check by size+filename+user (avoids loading full zip into query)
            if user_name:
                cursor.execute(
                    """
                    SELECT id, filename FROM uploaded_files
                    WHERE user_name = %s AND filename = %s AND COALESCE(file_data_size, 0) = %s
                    LIMIT 1
                    """,
                    (user_name, filename, zip_size),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, filename FROM uploaded_files
                    WHERE filename = %s AND COALESCE(file_data_size, 0) = %s
                    LIMIT 1
                    """,
                    (filename, zip_size),
                )
            existing = cursor.fetchone()
            if existing:
                existing_id, existing_filename = existing
                return UploadResult(
                    success=False,
                    message=(
                        "This ZIP file appears to have already been uploaded "
                        f"as '{existing_filename}' (ID {existing_id}). "
                        "Duplicate uploads are not allowed."
                    ),
                    error_type="DUPLICATE_UPLOAD",
                    data={"existing_file_id": existing_id, "existing_filename": existing_filename},
                )

            # 6.2 Load zip and insert (single read)
            with open(dest_path, "rb") as f:
                zip_bytes = f.read()
            cursor.execute("""
                INSERT INTO uploaded_files (
                    filename,
                    filepath,
                    status,
                    metadata,
                    file_data,
                    file_data_size,
                    user_name,
                    last_modified_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id
            """, (
                filename,
                dest_path,
                "uploaded",
                json.dumps({"files": file_contents}),
                zip_bytes,
                zip_size,
                user_name,
            ))
            uploaded_file_id = cursor.fetchone()[0]

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

    except ConnectionError:
        # Provide a separate database connection error message
        return UploadResult(
            success=False,
            message=(
                "Could not connect to the database while saving the uploaded file. "
                "Please try again later or contact the system administrator."
            ),
            error_type="DATABASE_CONNECTION_ERROR",
            data={"filename": filename},
        )
    except Exception as e:
        # Generalized DB save error message
        return UploadResult(
            success=False,
            message=(
                f"Database save failed for '{filename}': {e}. "
                "The file was copied to the uploads folder but could not be recorded in the database."
            ),
            error_type="DATABASE_SAVE_ERROR",
            data={"filename": filename},
        )


def get_uploaded_file_contents(uploaded_file_id):
    """
    Retrieve all file contents for a specific uploaded file.
    
    Args:
        uploaded_file_id (int): The ID of the uploaded file record
    
    Returns:
        list: List of file content records
    """
    return get_file_contents_by_upload_id(uploaded_file_id)


def add_thumbnail_to_project(project_id, thumbnail_path) -> UploadResult:
    """Attach a thumbnail image to an existing uploaded project."""
    if not isinstance(project_id, int) or project_id <= 0:
        return UploadResult(
            success=False,
            message="Invalid project ID.",
            error_type="INVALID_PROJECT_ID",
            data={"project_id": project_id},
        )

    if not os.path.exists(thumbnail_path):
        return UploadResult(
            success=False,
            message=f"Thumbnail file does not exist: {thumbnail_path}.",
            error_type="THUMBNAIL_NOT_FOUND",
            data={"thumbnail_path": thumbnail_path},
        )

    try:
        with open(thumbnail_path, "rb") as f:
            thumbnail_bytes = f.read()
        with with_db_cursor() as cursor:
            cursor.execute("""
                UPDATE uploaded_files
                SET thumbnail = %s,
                    last_modified_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id
            """, (thumbnail_bytes, project_id))
            updated = cursor.fetchone()

        if not updated:
            return UploadResult(
                success=False,
                message=f"No project found with ID {project_id}.",
                error_type="PROJECT_NOT_FOUND",
                data={"project_id": project_id},
            )

        return UploadResult(
            success=True,
            message="Thumbnail updated successfully.",
            error_type=None,
            data={"project_id": project_id, "thumbnail_path": thumbnail_path},
        )
    except ConnectionError:
        return UploadResult(
            success=False,
            message="Could not connect to the database while saving the thumbnail.",
            error_type="DATABASE_CONNECTION_ERROR",
            data={"project_id": project_id},
        )
    except Exception as e:
        return UploadResult(
            success=False,
            message=f"Failed to save thumbnail: {e}",
            error_type="THUMBNAIL_SAVE_ERROR",
            data={"project_id": project_id},
        )


def add_thumbnail_bytes_to_project(project_id, thumbnail_bytes) -> UploadResult:
    """Attach a thumbnail image (raw bytes) to an existing uploaded project."""
    if not isinstance(project_id, int) or project_id <= 0:
        return UploadResult(
            success=False,
            message="Invalid project ID.",
            error_type="INVALID_PROJECT_ID",
            data={"project_id": project_id},
        )

    if not isinstance(thumbnail_bytes, (bytes, bytearray)) or len(thumbnail_bytes) == 0:
        return UploadResult(
            success=False,
            message="Thumbnail content is empty or invalid.",
            error_type="THUMBNAIL_INVALID_BYTES",
            data={"project_id": project_id},
        )

    try:
        with with_db_cursor() as cursor:
            cursor.execute("""
                UPDATE uploaded_files
                SET thumbnail = %s,
                    last_modified_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id
            """, (bytes(thumbnail_bytes), project_id))
            updated = cursor.fetchone()

        if not updated:
            return UploadResult(
                success=False,
                message=f"No project found with ID {project_id}.",
                error_type="PROJECT_NOT_FOUND",
                data={"project_id": project_id},
            )

        return UploadResult(
            success=True,
            message="Thumbnail updated successfully.",
            error_type=None,
            data={"project_id": project_id},
        )
    except ConnectionError:
        return UploadResult(
            success=False,
            message="Could not connect to the database while saving the thumbnail.",
            error_type="DATABASE_CONNECTION_ERROR",
            data={"project_id": project_id},
        )
    except Exception as e:
        return UploadResult(
            success=False,
            message=f"Failed to save thumbnail: {e}",
            error_type="THUMBNAIL_SAVE_ERROR",
            data={"project_id": project_id},
        )


def list_uploaded_files():
    """
    Get a list of all uploaded files with their metadata.
    
    Returns:
        list: List of uploaded file records
    """
    try:
        with with_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    filename,
                    filepath,
                    status,
                    metadata,
                    user_name,
                    created_at,
                    last_modified_at
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
                "user_name": row[5],
                "created_at": row[6],
                "last_modified_at": row[7],
            })
        
        return files
        
    except ConnectionError:
        print("Could not connect to database.")
        return []
    except Exception as e:
        print(f"Error retrieving uploaded files: {e}")
        return []


def merge_zip_to_project(project_id: int, zip_file_path: str, user_name: str = None) -> UploadResult:
    """
    Merge files from a new ZIP archive into an existing project.
    
    This allows incremental additions to a portfolio/résumé by adding new files
    from another zipped folder. Duplicate files (same path and content) are skipped.
    
    Args:
        project_id: The ID of the existing project to merge into
        zip_file_path: Path to the new ZIP file to merge
        user_name: Optional username to verify ownership
        
    Returns:
        UploadResult with merge statistics
    """
    from parsing.file_contents_manager import _is_binary_file, _get_content_type
    from psycopg import Binary
    
    # 1. Validate project exists and user has access
    try:
        with with_db_cursor() as cursor:
            if user_name:
                cursor.execute(
                    "SELECT id, filename, metadata FROM uploaded_files WHERE id = %s AND user_name = %s",
                    (project_id, user_name)
                )
            else:
                cursor.execute(
                    "SELECT id, filename, metadata FROM uploaded_files WHERE id = %s",
                    (project_id,)
                )
            project = cursor.fetchone()
            
            if not project:
                return UploadResult(
                    success=False,
                    message=f"Project with ID {project_id} not found or access denied.",
                    error_type="PROJECT_NOT_FOUND",
                    data={"project_id": project_id}
                )
    except Exception as e:
        return UploadResult(
            success=False,
            message=f"Database error checking project: {e}",
            error_type="DATABASE_ERROR",
            data={"project_id": project_id}
        )
    
    project_filename = project[1]
    existing_metadata = project[2] or {}
    
    # 2. Validate new ZIP file
    if not os.path.exists(zip_file_path):
        return UploadResult(
            success=False,
            message=f"ZIP file does not exist: {zip_file_path}",
            error_type="FILE_NOT_FOUND",
            data={"filepath": zip_file_path}
        )
    
    if not zipfile.is_zipfile(zip_file_path):
        return UploadResult(
            success=False,
            message="The provided file is not a valid ZIP archive.",
            error_type="INVALID_ZIP",
            data={"filepath": zip_file_path}
        )
    
    # 3. Get existing file paths to detect duplicates
    existing_paths = set()
    try:
        with with_db_cursor() as cursor:
            cursor.execute(
                "SELECT file_path FROM file_contents WHERE uploaded_file_id = %s",
                (project_id,)
            )
            existing_paths = {row[0] for row in cursor.fetchall()}
    except Exception as e:
        return UploadResult(
            success=False,
            message=f"Error reading existing files: {e}",
            error_type="DATABASE_ERROR",
            data={"project_id": project_id}
        )
    
    # 4. Extract and merge new files
    new_files = []
    skipped_files = []
    errors = []
    
    try:
        from datetime import datetime
        from config.db_config import with_db_connection
        
        with with_db_connection() as (conn, cursor):
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                for file_path in file_list:
                    try:
                        # Skip directories
                        if file_path.endswith('/'):
                            continue
                        
                        # Check if file already exists in the project
                        if file_path in existing_paths:
                            skipped_files.append(file_path)
                            continue
                        
                        file_name = os.path.basename(file_path)
                        file_extension = os.path.splitext(file_name)[1].lower()
                        file_info = zip_ref.getinfo(file_path)
                        file_size = file_info.file_size
                        
                        # Get source timestamp
                        try:
                            src_ts = datetime(*file_info.date_time)
                        except Exception:
                            src_ts = None
                        
                        is_binary = _is_binary_file(file_extension)
                        content_type = _get_content_type(file_extension)
                        
                        file_bytes = zip_ref.read(file_path)
                        file_content = Binary(file_bytes)
                        
                        # Insert new file
                        cursor.execute("""
                            INSERT INTO file_contents 
                            (uploaded_file_id, file_path, file_name, file_extension, 
                             file_size, file_content, content_type, is_binary,
                             source_created_at, source_modified_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            project_id,
                            file_path,
                            file_name,
                            file_extension,
                            file_size,
                            file_content,
                            content_type,
                            is_binary,
                            src_ts,
                            src_ts,
                        ))
                        
                        new_files.append({
                            "file_path": file_path,
                            "file_name": file_name,
                            "file_size": file_size
                        })
                        
                    except Exception as e:
                        errors.append(f"Error processing {file_path}: {str(e)}")
            
            # Update project metadata
            if isinstance(existing_metadata, str):
                try:
                    existing_metadata = json.loads(existing_metadata)
                except:
                    existing_metadata = {}
            
            existing_files_list = existing_metadata.get('files', [])
            new_file_paths = [f['file_path'] for f in new_files]
            updated_files_list = existing_files_list + new_file_paths
            
            updated_metadata = {
                **existing_metadata,
                'files': updated_files_list,
                'last_merge': datetime.now().isoformat(),
                'merge_count': existing_metadata.get('merge_count', 0) + 1
            }
            
            cursor.execute("""
                UPDATE uploaded_files 
                SET metadata = %s, last_modified_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (json.dumps(updated_metadata), project_id))
            
            conn.commit()
        
        return UploadResult(
            success=True,
            message=f"Successfully merged {len(new_files)} new files into project '{project_filename}'.",
            error_type=None,
            data={
                "project_id": project_id,
                "new_files_count": len(new_files),
                "skipped_duplicates": len(skipped_files),
                "new_files": new_files,
                "skipped_files": skipped_files,
                "errors": errors
            }
        )
        
    except Exception as e:
        return UploadResult(
            success=False,
            message=f"Error merging files: {e}",
            error_type="MERGE_ERROR",
            data={"project_id": project_id}
        )


def list_uploaded_files_by_user(user_name: str):
    """
    Get a list of all uploaded files for a specific user.
    
    Args:
        user_name (str): The username to filter by
    
    Returns:
        list: List of uploaded file records for the specified user
    """
    try:
        with with_db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    filename,
                    filepath,
                    status,
                    metadata,
                    user_name,
                    created_at,
                    last_modified_at
                FROM uploaded_files
                WHERE user_name = %s
                ORDER BY created_at DESC
            """, (user_name,))
            
            results = cursor.fetchall()
        
        files = []
        for row in results:
            files.append({
                "id": row[0],
                "filename": row[1],
                "filepath": row[2],
                "status": row[3],
                "metadata": row[4],
                "user_name": row[5],
                "created_at": row[6],
                "last_modified_at": row[7],
            })
        
        return files
        
    except ConnectionError:
        print("Could not connect to database.")
        return []
    except Exception as e:
        print(f"Error retrieving uploaded files for user {user_name}: {e}")
        return []
