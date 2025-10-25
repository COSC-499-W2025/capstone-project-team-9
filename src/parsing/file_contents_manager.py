import os
import zipfile
import json
from config.db_config import get_connection


def init_file_contents_table():
    """Create the file_contents table if it doesn't exist."""
    conn = get_connection()
    if not conn:
        raise Exception("Failed to connect to database")
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_contents (
                id SERIAL PRIMARY KEY,
                uploaded_file_id INTEGER REFERENCES uploaded_files(id) ON DELETE CASCADE,
                file_path VARCHAR(1000) NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_extension VARCHAR(50),
                file_size BIGINT,
                file_content TEXT, -- Stores line count as string for text files, "0" for binary files
                content_type VARCHAR(100),
                is_binary BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        print("✓ File contents table initialized")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error initializing file_contents table: {e}")
        raise
    finally:
        conn.close()


def extract_and_store_file_contents(uploaded_file_id, zip_file_path, max_files=1000, batch_size=50):
    """
    Extract all files from a zip archive and store their line counts in the database.
    Handles nested folders and large numbers of files efficiently.
    
    Args:
        uploaded_file_id (int): The ID of the uploaded file record
        zip_file_path (str): Path to the zip file
        max_files (int): Maximum number of files to process (safety limit)
        batch_size (int): Number of files to process in each batch
    
    Returns:
        dict: Summary of extraction results
    """
    if not os.path.exists(zip_file_path):
        print(f"Zip file does not exist: {zip_file_path}")
        return {"success": False, "error": "File not found"}
    
    if not zipfile.is_zipfile(zip_file_path):
        print(f"Not a valid zip file: {zip_file_path}")
        return {"success": False, "error": "Invalid zip file"}
    
    conn = get_connection()
    if not conn:
        print("Could not connect to database.")
        return {"success": False, "error": "Database connection failed"}
    
    extracted_files = []
    errors = []
    processed_count = 0
    
    try:
        cursor = conn.cursor()
        
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            total_files = len([f for f in file_list if not f.endswith('/')])
            
            print(f"Found {total_files} files in zip archive")
            
            if total_files > max_files:
                print(f"Warning: Zip contains {total_files} files, but processing limit is {max_files}")
                return {"success": False, "error": f"Too many files ({total_files}). Maximum allowed: {max_files}"}
            
            # Process files in batches for better memory management
            batch_data = []
            
            for file_path in file_list:
                try:
                    # Skip directories
                    if file_path.endswith('/'):
                        continue
                    
                    # Extract file info
                    file_name = os.path.basename(file_path)
                    file_extension = os.path.splitext(file_name)[1].lower()
                    
                    # Get file info from zip
                    file_info = zip_ref.getinfo(file_path)
                    file_size = file_info.file_size
                    
                    # Determine if file is binary
                    is_binary = _is_binary_file(file_extension)
                    
                    # Read file content and count lines
                    file_content = None
                    content_type = _get_content_type(file_extension)
                    
                    if not is_binary:
                        try:
                            # Try to read as text and count lines
                            text_content = zip_ref.read(file_path).decode('utf-8')
                            line_count = len(text_content.splitlines())
                            file_content = str(line_count)  # Store line count as string
                        except UnicodeDecodeError:
                            # If UTF-8 fails, try other encodings
                            try:
                                text_content = zip_ref.read(file_path).decode('latin-1')
                                line_count = len(text_content.splitlines())
                                file_content = str(line_count)  # Store line count as string
                            except:
                                # If all text decoding fails, mark as binary
                                is_binary = True
                                file_content = "0"  # Binary files have 0 lines
                    
                    # Add to batch
                    batch_data.append((
                        uploaded_file_id, file_path, file_name, file_extension,
                        file_size, file_content, content_type, is_binary
                    ))
                    
                    extracted_files.append({
                        "file_path": file_path,
                        "file_name": file_name,
                        "file_size": file_size,
                        "is_binary": is_binary
                    })
                    
                    processed_count += 1
                    
                    # Process batch when it reaches batch_size
                    if len(batch_data) >= batch_size:
                        _insert_batch(cursor, batch_data)
                        batch_data = []
                        print(f"Processed {processed_count}/{total_files} files...")
                    
                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    errors.append(error_msg)
                    print(error_msg)
            
            # Insert remaining files in the last batch
            if batch_data:
                _insert_batch(cursor, batch_data)
            
            conn.commit()
            print(f"✓ Successfully extracted {len(extracted_files)} files from zip")
            
            return {
                "success": True,
                "extracted_files": extracted_files,
                "total_files": len(extracted_files),
                "errors": errors,
                "processed_count": processed_count
            }
        
    except Exception as e:
        conn.rollback()
        error_msg = f"Error extracting zip contents: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}
    finally:
        cursor.close()
        conn.close()


def _insert_batch(cursor, batch_data):
    """Insert a batch of file contents into the database."""
    try:
        cursor.executemany("""
            INSERT INTO file_contents 
            (uploaded_file_id, file_path, file_name, file_extension, 
             file_size, file_content, content_type, is_binary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, batch_data)
    except Exception as e:
        print(f"Error inserting batch: {e}")
        raise


def get_file_contents_by_folder(uploaded_file_id, folder_path=""):
    """
    Retrieve file line counts organized by folder structure.
    
    Args:
        uploaded_file_id (int): The ID of the uploaded file record
        folder_path (str): Optional folder path to filter by
    
    Returns:
        dict: File line counts organized by folder structure
    """
    conn = get_connection()
    if not conn:
        print("Could not connect to database.")
        return {}
    
    try:
        cursor = conn.cursor()
        
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
        
    except Exception as e:
        print(f"Error retrieving file contents by folder: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()


def get_file_statistics(uploaded_file_id):
    """
    Get statistics about the files in an uploaded zip.
    
    Args:
        uploaded_file_id (int): The ID of the uploaded file record
    
    Returns:
        dict: File statistics
    """
    conn = get_connection()
    if not conn:
        print("Could not connect to database.")
        return {}
    
    try:
        cursor = conn.cursor()
        
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
        
        # Get file extensions
        cursor.execute("""
            SELECT file_extension, COUNT(*) as count
            FROM file_contents
            WHERE uploaded_file_id = %s AND file_extension != ''
            GROUP BY file_extension
            ORDER BY count DESC
        """, (uploaded_file_id,))
        
        extensions = cursor.fetchall()
        
        # Get folder structure
        cursor.execute("""
            SELECT DISTINCT 
                CASE 
                    WHEN file_path LIKE '%/%' THEN 
                        substring(file_path from 1 for position('/' in reverse(file_path)) - 1)
                    ELSE 'root'
                END as folder,
                COUNT(*) as file_count
            FROM file_contents
            WHERE uploaded_file_id = %s
            GROUP BY folder
            ORDER BY folder
        """, (uploaded_file_id,))
        
        folders = cursor.fetchall()
        
        return {
            "total_files": stats[0] or 0,
            "total_size_bytes": stats[1] or 0,
            "text_files": stats[2] or 0,
            "binary_files": stats[3] or 0,
            "file_extensions": [{"extension": ext[0], "count": ext[1]} for ext in extensions],
            "folders": [{"folder": folder[0], "file_count": folder[1]} for folder in folders]
        }
        
    except Exception as e:
        print(f"Error getting file statistics: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()


def get_file_contents_by_upload_id(uploaded_file_id):
    """
    Retrieve all file line counts for a specific uploaded file.
    
    Args:
        uploaded_file_id (int): The ID of the uploaded file record
    
    Returns:
        list: List of file line count records
    """
    conn = get_connection()
    if not conn:
        print("Could not connect to database.")
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, file_path, file_name, file_extension, file_size,
                   file_content, content_type, is_binary, created_at
            FROM file_contents
            WHERE uploaded_file_id = %s
            ORDER BY file_path
        """, (uploaded_file_id,))
        
        results = cursor.fetchall()
        files = []
        
        for row in results:
            files.append({
                "id": row[0],
                "file_path": row[1],
                "file_name": row[2],
                "file_extension": row[3],
                "file_size": row[4],
                "file_content": row[5],
                "content_type": row[6],
                "is_binary": row[7],
                "created_at": row[8]
            })
        
        return files
        
    except Exception as e:
        print(f"Error retrieving file contents: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


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
