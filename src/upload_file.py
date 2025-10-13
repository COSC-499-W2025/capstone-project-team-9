import os
import shutil
import zipfile
from config.db_config import get_connection # for getting a connection to the database

UPLOAD_FOLDER = "data/uploads"

# this will be the function to add a file to the database. the user will type in the path to the file, and this function will handle the rest.
# it will copy the file to the upload folder, extract metadata from the zip (list of files inside), and store that in the database.
# Currently it does not store the metadata, just the filename and path but the Table in the database has a column for metadata
def add_file_to_db(filepath):
    if not os.path.exists(filepath):
        print("File does not exist.")
        return
    
    filename = os.path.basename(filepath)
    dest_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Copy file to upload folder
    shutil.copy(filepath, dest_path)
    print(f"File copied to {dest_path}")
    
    # Extract metadata from zip (list of files inside)
    file_contents = []
    if zipfile.is_zipfile(dest_path):
        with zipfile.ZipFile(dest_path, 'r') as zip_ref:
            file_contents = zip_ref.namelist()  # list of files inside
        print(f"Files inside zip: {file_contents}")
    
    # Store in database and close the connection to avoid connection leaks
    conn = get_connection()
    if not conn:
        print("Could not connect to database.")
        return
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO uploaded_files (filename, filepath, status)
        VALUES (%s, %s, %s)
    """, (filename, dest_path, "uploaded"))

    conn.commit()
    conn.close()
    print("File metadata saved to database.")
