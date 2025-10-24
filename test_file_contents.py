#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced upload file functionality.
This script demonstrates how to use the new file contents extraction feature
with nested folders and various file types.
"""

import os
import sys
import zipfile
import tempfile
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from upload_file import init_uploaded_files_table, add_file_to_db, get_uploaded_file_contents, list_uploaded_files
from parsing.file_contents_manager import get_file_contents_by_folder, get_file_statistics


def create_complex_test_zip():
    """Create a complex test zip file with nested folders and various file types."""
    # Create a temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # Create nested folder structure
        folders = [
            'src',
            'src/components',
            'src/utils',
            'src/components/ui',
            'tests',
            'tests/unit',
            'tests/integration',
            'docs',
            'assets',
            'assets/images',
            'config'
        ]
        
        for folder in folders:
            os.makedirs(os.path.join(temp_dir, folder), exist_ok=True)
        
        # Create test files with various types
        test_files = {
            # Root level files
            'README.md': '# Complex Test Project\n\nThis is a comprehensive test project with nested folders.',
            'package.json': '{"name": "test-project", "version": "1.0.0", "dependencies": {}}',
            'requirements.txt': 'flask==2.0.1\nrequests==2.25.1\npytest==6.2.2',
            'Dockerfile': 'FROM python:3.9\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt',
            
            # Source files
            'src/main.py': '#!/usr/bin/env python3\nimport sys\nprint("Hello from main!")\n',
            'src/config.py': 'DATABASE_URL = "postgresql://localhost/test"\nDEBUG = True\n',
            'src/components/__init__.py': '# Components package\n',
            'src/components/ui/button.py': 'class Button:\n    def __init__(self, text):\n        self.text = text\n',
            'src/components/ui/modal.py': 'class Modal:\n    def show(self):\n        pass\n',
            'src/utils/helpers.py': 'def format_date(date):\n    return date.strftime("%Y-%m-%d")\n',
            'src/utils/validators.py': 'def is_valid_email(email):\n    return "@" in email\n',
            
            # Test files
            'tests/__init__.py': '# Tests package\n',
            'tests/test_main.py': 'import unittest\nfrom src.main import main\n\nclass TestMain(unittest.TestCase):\n    def test_main(self):\n        self.assertTrue(True)\n',
            'tests/unit/test_utils.py': 'import unittest\nfrom src.utils.helpers import format_date\n\nclass TestUtils(unittest.TestCase):\n    def test_format_date(self):\n        pass\n',
            'tests/integration/test_api.py': 'import unittest\n\nclass TestAPI(unittest.TestCase):\n    def test_endpoint(self):\n        pass\n',
            
            # Documentation
            'docs/README.md': '# Documentation\n\nThis is the documentation folder.',
            'docs/api.md': '# API Documentation\n\n## Endpoints\n- GET /api/users\n- POST /api/users',
            'docs/deployment.md': '# Deployment Guide\n\n## Steps\n1. Build the application\n2. Deploy to server',
            
            # Configuration files
            'config/settings.json': '{"database": {"host": "localhost", "port": 5432}, "cache": {"enabled": true}}',
            'config/logging.yaml': 'version: 1\nhandlers:\n  console:\n    class: logging.StreamHandler\n',
            
            # Asset files (simulated)
            'assets/images/logo.png': 'PNG_DATA_PLACEHOLDER',
            'assets/images/icon.svg': '<svg><circle r="10" fill="blue"/></svg>',
            
            # Large text file to test performance
            'large_file.txt': 'This is a large file.\n' * 1000,  # 1000 lines
        }
        
        # Write test files
        for file_path, content in test_files.items():
            full_path = os.path.join(temp_dir, file_path)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Create zip file
        zip_path = os.path.join(temp_dir, 'complex_test_project.zip')
        with zipfile.ZipFile(zip_path, 'w') as zip_ref:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.zip'):
                        continue  # Skip the zip file itself
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_dir)
                    zip_ref.write(file_path, arc_path)
        
        return zip_path


def test_complex_upload_and_extraction():
    """Test the upload and file content extraction functionality with complex structure."""
    print("=== Testing Complex Upload File with Nested Folders ===\n")
    
    try:
        # Initialize database tables
        print("1. Initializing database tables...")
        init_uploaded_files_table()
        print("✓ Database tables initialized\n")
        
        # Create complex test zip file
        print("2. Creating complex test zip file with nested folders...")
        test_zip_path = create_complex_test_zip()
        print(f"✓ Complex test zip created: {test_zip_path}\n")
        
        # Upload file and extract contents
        print("3. Uploading file and extracting contents...")
        add_file_to_db(test_zip_path)
        print("✓ File uploaded and contents extracted\n")
        
        # List uploaded files
        print("4. Listing uploaded files...")
        uploaded_files = list_uploaded_files()
        if uploaded_files:
            print(f"✓ Found {len(uploaded_files)} uploaded file(s)")
            for file_info in uploaded_files:
                print(f"   - ID: {file_info['id']}, Filename: {file_info['filename']}")
        print()
        
        # Get file statistics
        if uploaded_files:
            print("5. Getting file statistics...")
            stats = get_file_statistics(uploaded_files[0]['id'])
            print(f"✓ File Statistics:")
            print(f"   - Total files: {stats['total_files']}")
            print(f"   - Total size: {stats['total_size_bytes']} bytes")
            print(f"   - Text files: {stats['text_files']}")
            print(f"   - Binary files: {stats['binary_files']}")
            print(f"   - File extensions: {[ext['extension'] for ext in stats['file_extensions'][:5]]}")
            print(f"   - Folders: {[folder['folder'] for folder in stats['folders']]}")
            print()
        
        # Get file contents organized by folder
        if uploaded_files:
            print("6. Retrieving file contents organized by folder...")
            folder_structure = get_file_contents_by_folder(uploaded_files[0]['id'])
            print(f"✓ Retrieved files organized by {len(folder_structure)} folders:")
            
            for folder, files in folder_structure.items():
                print(f"   📁 {folder} ({len(files)} files)")
                for file_info in files[:3]:  # Show first 3 files per folder
                    print(f"      - {file_info['file_name']} ({file_info['file_size']} bytes)")
                if len(files) > 3:
                    print(f"      ... and {len(files) - 3} more files")
            print()
        
        # Show some file contents
        if uploaded_files:
            print("7. Showing sample file contents...")
            file_contents = get_uploaded_file_contents(uploaded_files[0]['id'])
            
            # Find some interesting files to show
            interesting_files = [f for f in file_contents if f['file_name'] in ['main.py', 'README.md', 'package.json']]
            
            for file_info in interesting_files[:2]:  # Show first 2 interesting files
                print(f"   📄 {file_info['file_path']}")
                print(f"      Size: {file_info['file_size']} bytes")
                print(f"      Type: {file_info['content_type']}")
                print(f"      Binary: {file_info['is_binary']}")
                if file_info['file_content'] and len(file_info['file_content']) < 200:
                    print(f"      Content preview: {file_info['file_content'][:100]}...")
                print()
        
        print("=== Complex Test completed successfully! ===")
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


def test_performance_with_many_files():
    """Test performance with a large number of files."""
    print("\n=== Testing Performance with Many Files ===\n")
    
    try:
        # Create a zip with many files
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, 'many_files.zip')
            
            with zipfile.ZipFile(zip_path, 'w') as zip_ref:
                # Create 100 small files
                for i in range(100):
                    content = f"# File {i}\nThis is file number {i}\n" + "Line " * 10
                    zip_ref.writestr(f"file_{i:03d}.txt", content)
            
            print(f"Created zip with 100 files: {zip_path}")
            
            # Upload and extract
            print("Uploading and extracting many files...")
            add_file_to_db(zip_path)
            print("✓ Many files uploaded and extracted successfully!")
            
    except Exception as e:
        print(f"✗ Performance test failed: {e}")


if __name__ == "__main__":
    test_complex_upload_and_extraction()
    test_performance_with_many_files()
