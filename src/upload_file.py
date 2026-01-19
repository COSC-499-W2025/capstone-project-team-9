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

UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", "uploads"))

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

                # The old database may not have last_modified_at.
                cursor.execute("""
                    ALTER TABLE uploaded_files
                    ADD COLUMN IF NOT EXISTS last_modified_at TIMESTAMP;
                """)

                # The old database may not have user_name.
                cursor.execute("""
                    ALTER TABLE uploaded_files
                    ADD COLUMN IF NOT EXISTS user_name VARCHAR(255);
                """)

                # The old database may not have contributor_name.
                cursor.execute("""
                    ALTER TABLE uploaded_files
                    ADD COLUMN IF NOT EXISTS contributor_name VARCHAR(255);
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


def add_file_to_db(filepath, user_name: str = None) -> UploadResult:
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
        with open(dest_path, "rb") as f:
            zip_bytes = f.read()

        with with_db_cursor() as cursor:
            # 6.1 Check if an identical ZIP (same bytes) has already been uploaded
            cursor.execute(
                """
                SELECT id, filename
                FROM uploaded_files
                WHERE file_data = %s
                LIMIT 1
                """,
                (zip_bytes,),
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
                    data={
                        "existing_file_id": existing_id,
                        "existing_filename": existing_filename,
                    },
                )

            # 6.2 No duplicate found: insert new uploaded_files record
            cursor.execute("""
                INSERT INTO uploaded_files (
                    filename,
                    filepath,
                    status,
                    metadata,
                    file_data,
                    user_name,
                    last_modified_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id
            """, (
                filename,
                dest_path,
                "uploaded",
                json.dumps({"files": file_contents}),
                zip_bytes,
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
