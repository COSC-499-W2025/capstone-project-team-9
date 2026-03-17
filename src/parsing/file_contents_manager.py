import os
import zipfile
import json
from datetime import datetime 
from psycopg import Binary
from config.db_config import with_db_cursor, with_db_connection


def init_file_contents_table():
    """Create the file_contents table if it doesn't exist, and ensure source_* columns exist."""
    try:
        # Create table if not exists
        with with_db_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_contents (
                    id SERIAL PRIMARY KEY,
                    uploaded_file_id INTEGER REFERENCES uploaded_files(id) ON DELETE CASCADE,
                    file_path VARCHAR(1000) NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    file_extension VARCHAR(50),
                    file_size BIGINT,
                    file_content BYTEA,
                    content_type VARCHAR(100),
                    is_binary BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        print("File contents table initialized")

        # schema migration: ensure source_* and line_count columns exist
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    ALTER TABLE file_contents
                    ADD COLUMN IF NOT EXISTS source_created_at TIMESTAMP NULL;
                """)
                cursor.execute("""
                    ALTER TABLE file_contents
                    ADD COLUMN IF NOT EXISTS source_modified_at TIMESTAMP NULL;
                """)
                cursor.execute("""
                    ALTER TABLE file_contents
                    ADD COLUMN IF NOT EXISTS line_count INTEGER NULL;
                """)
            # print("file_contents table migrated: source_* columns ensured")
        except Exception as e:
            print(f"[WARN] Skipping file_contents source_* migration: {e}")

        # 3. Add indexes for performance
        try:
            with with_db_cursor() as cursor:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_file_contents_upload_source_ts
                    ON file_contents (uploaded_file_id, source_created_at, source_modified_at);
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_file_contents_uploaded_file_id
                    ON file_contents (uploaded_file_id);
                """)
        except Exception as e:
            print(f"[WARN] Skipping index creation: {e}")

    except ConnectionError:
        raise Exception("Failed to connect to database")
    except Exception as e:
        print(f"Error initializing file_contents table: {e}")
        raise


# Exclude dependency/build dirs to keep uploads and analysis fast (same as zip_project_analyzer)
EXCLUDED_ZIP_PARTS = {"__macosx", ".git", ".svn", ".hg", "__pycache__", "node_modules", ".venv", "venv", "dist", "build", "target", "out", ".next", ".nuxt"}
MAX_FILE_SIZE_FOR_CONTENT = 1 * 1024 * 1024  # 1MB: skip storing content for huge files to avoid memory blowup


def _should_skip_zip_path(file_path: str) -> bool:
    """Skip paths under excluded dirs (e.g. node_modules, .git)."""
    normalized = file_path.replace("\\", "/").lower()
    parts = normalized.split("/")
    return any(part in EXCLUDED_ZIP_PARTS for part in parts)


def extract_and_store_file_contents(uploaded_file_id, zip_file_path, max_files=1000, batch_size=50):
    """
    Extract files from a zip and store in the database.
    Skips node_modules, .git, etc. Does not load full content for duplicate check or for files > 1MB.
    """
    if not os.path.exists(zip_file_path):
        print(f"Zip file does not exist: {zip_file_path}")
        return {"success": False, "error": "File not found"}
    
    if not zipfile.is_zipfile(zip_file_path):
        print(f"Not a valid zip file: {zip_file_path}")
        return {"success": False, "error": "Invalid zip file"}
    
    extracted_files = []
    errors = []
    processed_count = 0

    try:
        with with_db_connection() as (conn, cursor):
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                # Filter excluded dirs first so we don't exceed max_files with deps
                candidate = [f for f in file_list if not f.endswith('/') and not _should_skip_zip_path(f)]
                total_candidates = len(candidate)
                
                print(f"Found {total_candidates} files in zip (after excluding deps/build dirs)")
                
                if total_candidates > max_files:
                    return {"success": False, "error": f"Too many files ({total_candidates}). Maximum allowed: {max_files}"}
                
                batch_data = []
                seen_paths = set()

                for file_path in candidate:
                    try:
                        file_name = os.path.basename(file_path)
                        file_extension = os.path.splitext(file_name)[1].lower()
                        file_info = zip_ref.getinfo(file_path)
                        file_size = file_info.file_size

                        if file_path in seen_paths:
                            continue
                        seen_paths.add(file_path)

                        try:
                            src_ts = datetime(*file_info.date_time)
                        except Exception:
                            src_ts = None

                        is_binary = _is_binary_file(file_extension)
                        content_type = _get_content_type(file_extension)

                        # Skip storing content for very large files to avoid memory/DB blowup
                        store_content = file_size <= MAX_FILE_SIZE_FOR_CONTENT
                        line_count = None
                        if store_content:
                            file_bytes = zip_ref.read(file_path)
                            file_content = Binary(file_bytes)
                            if not is_binary and file_bytes:
                                line_count = file_bytes.count(b"\n") + (1 if not file_bytes.endswith(b"\n") else 0)
                        else:
                            file_content = None

                        batch_data.append((
                            uploaded_file_id,
                            file_path,
                            file_name,
                            file_extension,
                            file_size,
                            file_content,
                            content_type,
                            is_binary,
                            src_ts,
                            src_ts,
                            line_count,
                        ))

                        extracted_files.append({
                            "file_path": file_path,
                            "file_name": file_name,
                            "file_size": file_size,
                            "is_binary": is_binary
                        })

                        processed_count += 1

                        if len(batch_data) >= batch_size:
                            _insert_batch(cursor, batch_data)
                            batch_data = []
                            print(f"Processed {processed_count}/{total_files} files...")

                    except Exception as e:
                        errors.append(f"Error processing {file_path}: {str(e)}")
                        print(f"Error processing {file_path}: {str(e)}")


                if batch_data:
                    _insert_batch(cursor, batch_data)

                conn.commit()
                print(f"Successfully extracted {len(extracted_files)} files from zip")

        return {
            "success": True,
            "extracted_files": extracted_files,
            "total_files": len(extracted_files),
            "errors": errors,
            "processed_count": processed_count
        }

    except ConnectionError:
        print("Could not connect to database.")
        return {"success": False, "error": "Database connection failed"}
    except Exception as e:
        print(f"Error extracting zip contents: {e}")
        return {"success": False, "error": str(e)}



def _insert_batch(cursor, batch_data):
    """Insert a batch of file contents into the database."""
    try:
        cursor.executemany("""
            INSERT INTO file_contents 
            (uploaded_file_id, file_path, file_name, file_extension,
             file_size, file_content, content_type, is_binary,
             source_created_at, source_modified_at, line_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, batch_data)
    except Exception as e:
        print(f"Error inserting batch: {e}")
        raise

def get_zip_file(uploaded_file_id):
    try:
        with with_db_cursor() as cursor:
            cursor.execute("""
                SELECT file_data
                FROM uploaded_files
                WHERE id = %s
            """, (uploaded_file_id,))
            row = cursor.fetchone()
            if row:
                return row[0]  # file_data column
            return None
    except ConnectionError:
        print("Could not connect to database.")
        return {}
    except Exception as e:
        print(f"Error retrieving the zip file: {e}")
        return {}

def get_file_contents_by_folder(uploaded_file_id, folder_path=""):
    """
    Retrieve file line counts organized by folder structure.
    
    Args:
        uploaded_file_id (int): The ID of the uploaded file record
        folder_path (str): Optional folder path to filter by
    
    Returns:
        dict: File line counts organized by folder structure
    """
    try:
        with with_db_cursor() as cursor:
            if folder_path:
                cursor.execute("""
                    SELECT file_path, file_name, file_extension, file_size,
                           file_content, content_type, is_binary, created_at
                    FROM file_contents
                    WHERE uploaded_file_id = %s AND file_path LIKE %s
                    ORDER BY file_path
                """, (uploaded_file_id, f"{folder_path}%"))
            else:
                cursor.execute("""
                    SELECT file_path, file_name, file_extension, file_size,
                           file_content, content_type, is_binary, created_at
                    FROM file_contents
                    WHERE uploaded_file_id = %s
                    ORDER BY file_path
                """, (uploaded_file_id,))
            
            results = cursor.fetchall()
        
        # Organize files by folder structure
        folder_structure = {}
        
        for row in results:
            file_path = row[0]
            file_name = row[1]
            file_extension = row[2]
            file_size = row[3]
            file_content = row[4]
            content_type = row[5]
            is_binary = row[6]
            created_at = row[7]
            
            # Extract folder path
            folder = os.path.dirname(file_path) if os.path.dirname(file_path) else "root"
            
            if folder not in folder_structure:
                folder_structure[folder] = []
            
            folder_structure[folder].append({
                "file_path": file_path,
                "file_name": file_name,
                "file_extension": file_extension,
                "file_size": file_size,
                "file_content": file_content,
                "content_type": content_type,
                "is_binary": is_binary,
                "created_at": created_at
            })
        
        return folder_structure
        
    except ConnectionError:
        print("Could not connect to database.")
        return {}
    except Exception as e:
        print(f"Error retrieving file contents by folder: {e}")
        return {}


def get_file_statistics(uploaded_file_id):
    """
    Get statistics about the files in an uploaded zip.
    
    Args:
        uploaded_file_id (int): The ID of the uploaded file record
    
    Returns:
        dict: File statistics
    """
    try:
        with with_db_cursor() as cursor:
            # Get basic counts
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_files,
                    SUM(file_size) as total_size,
                    COUNT(CASE WHEN is_binary = false THEN 1 END) as text_files,
                    COUNT(CASE WHEN is_binary = true THEN 1 END) as binary_files
                FROM file_contents
                WHERE uploaded_file_id = %s
            """, (uploaded_file_id,))
            
            stats = cursor.fetchone()
            
            # Handle case where no files are found
            if not stats or len(stats) < 4:
                return {
                    "total_files": 0,
                    "total_size_bytes": 0,
                    "text_files": 0,
                    "binary_files": 0,
                    "file_extensions": [],
                    "folders": []
                }
            
            # Get file extensions
            cursor.execute("""
                SELECT file_extension, COUNT(*) as count
                FROM file_contents
                WHERE uploaded_file_id = %s AND file_extension != ''
                GROUP BY file_extension
                ORDER BY count DESC
            """, (uploaded_file_id,))
            
            extensions = cursor.fetchall()
            
            # Get folder structure (simplified approach)
            cursor.execute("""
                SELECT 
                    COALESCE(split_part(file_path, '/', 1), 'root') as folder,
                    COUNT(*) as file_count
                FROM file_contents
                WHERE uploaded_file_id = %s
                GROUP BY folder
                ORDER BY folder
            """, (uploaded_file_id,))
            
            folders = cursor.fetchall()
        
        return {
            "total_files": stats[0] or 0,
            "total_size_bytes": int(stats[1]) if stats[1] else 0,
            "text_files": stats[2] or 0,
            "binary_files": stats[3] or 0,
            "file_extensions": [{"extension": ext[0], "count": ext[1]} for ext in extensions],
            "folders": [{"folder": folder[0], "file_count": folder[1]} for folder in folders]
        }
        
    except ConnectionError:
        print("Could not connect to database.")
        return {}
    except Exception as e:
        print(f"Error getting file statistics: {e}")
        return {}


def get_file_contents_by_upload_id(uploaded_file_id, include_content=True):
    """
    Retrieve file records for an upload. Set include_content=False to avoid loading
    large BYTEA blobs (use for structure/languages/stats when line_count is present).
    """
    try:
        with with_db_cursor() as cursor:
            if include_content:
                cursor.execute("""
                    SELECT id, file_path, file_name, file_extension, file_size,
                           file_content, content_type, is_binary, created_at, line_count,
                           source_created_at
                    FROM file_contents
                    WHERE uploaded_file_id = %s
                    ORDER BY file_path
                """, (uploaded_file_id,))
            else:
                cursor.execute("""
                    SELECT id, file_path, file_name, file_extension, file_size,
                           content_type, is_binary, created_at, line_count,
                           source_created_at
                    FROM file_contents
                    WHERE uploaded_file_id = %s
                    ORDER BY file_path
                """, (uploaded_file_id,))
            results = cursor.fetchall()
        files = []
        for row in results:
            if include_content:
                files.append({
                    "id": row[0],
                    "file_path": row[1],
                    "file_name": row[2],
                    "file_extension": row[3],
                    "file_size": row[4],
                    "file_content": row[5],
                    "content_type": row[6],
                    "is_binary": row[7],
                    "created_at": row[8],
                    "line_count": row[9] if len(row) > 9 else None,
                    "source_created_at": row[10] if len(row) > 10 else None,
                })
            else:
                files.append({
                    "id": row[0],
                    "file_path": row[1],
                    "file_name": row[2],
                    "file_extension": row[3],
                    "file_size": row[4],
                    "file_content": None,
                    "content_type": row[5],
                    "is_binary": row[6],
                    "created_at": row[7],
                    "line_count": row[8] if len(row) > 8 else None,
                    "source_created_at": row[9] if len(row) > 9 else None,
                })
        return files
    except ConnectionError:
        print("Could not connect to database.")
        return []
    except Exception as e:
        print(f"Error retrieving file contents: {e}")
        return []


def get_file_contents_content_for_paths(uploaded_file_id, file_paths):
    """
    Fetch file_content only for the given paths. Use for deep analysis / doc extraction
    so we don't load all file contents into memory.
    """
    if not file_paths:
        return []
    try:
        with with_db_cursor() as cursor:
            cursor.execute("""
                SELECT file_path, file_name, file_extension, file_size,
                       file_content, content_type, is_binary
                FROM file_contents
                WHERE uploaded_file_id = %s AND file_path = ANY(%s)
            """, (uploaded_file_id, list(file_paths)))
            results = cursor.fetchall()
        return [
            {
                "file_path": row[0],
                "file_name": row[1],
                "file_extension": row[2],
                "file_size": row[3],
                "file_content": row[4],
                "content_type": row[5],
                "is_binary": row[6],
            }
            for row in results
        ]
    except Exception as e:
        print(f"Error fetching content for paths: {e}")
        return []


def _is_binary_file(file_extension):
    """Determine if a file is binary based on its extension."""
    binary_extensions = {
        # Executables and libraries
        '.exe', '.dll', '.so', '.dylib', '.bin', '.app', '.deb', '.rpm',
        # Archives
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lzma',
        # Images
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.ico', 
        '.svg', '.webp', '.raw', '.cr2', '.nef', '.arw', '.dng',
        # Videos
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v',
        # Audio
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
        # Documents (binary formats)
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.odt', '.ods', '.odp', '.rtf',
        # Design files
        '.psd', '.ai', '.eps', '.indd', '.sketch', '.fig', '.xd',
        # Database files
        '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb',
        # Other binary formats
        '.dat', '.bin', '.iso', '.img', '.dmg', '.pkg', '.msi',
        # Fonts
        '.ttf', '.otf', '.woff', '.woff2', '.eot',
        # Compiled code
        '.pyc', '.pyo', '.class', '.jar', '.war', '.ear'
    }
    return file_extension.lower() in binary_extensions


def _get_content_type(file_extension):
    """Get MIME content type based on file extension."""
    content_types = {
        '.txt': 'text/plain',
        '.html': 'text/html',
        '.htm': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.csv': 'text/csv',
        '.py': 'text/x-python',
        '.java': 'text/x-java-source',
        '.cpp': 'text/x-c++src',
        '.c': 'text/x-csrc',
        '.h': 'text/x-chdr',
        '.php': 'text/x-php',
        '.rb': 'text/x-ruby',
        '.go': 'text/x-go',
        '.rs': 'text/x-rust',
        '.md': 'text/markdown',
        '.yml': 'text/yaml',
        '.yaml': 'text/yaml',
        '.sql': 'text/x-sql',
        '.sh': 'text/x-shellscript',
        '.bat': 'text/x-msdos-batch',
        '.ps1': 'text/x-powershell',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.pdf': 'application/pdf',
        '.zip': 'application/zip'
    }
    return content_types.get(file_extension.lower(), 'application/octet-stream')
