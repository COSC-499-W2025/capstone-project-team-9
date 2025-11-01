"""
Shared constants for language, document/design extensions, and project type indicators.
"""

# Programming language extensions
LANGUAGE_EXTENSIONS = {
    # Web Technologies
    '.html': 'HTML', '.htm': 'HTML', '.css': 'CSS', '.js': 'JavaScript',
    '.jsx': 'React JSX', '.ts': 'TypeScript', '.tsx': 'React TypeScript',
    '.vue': 'Vue.js', '.svelte': 'Svelte',

    # Backend Languages
    '.py': 'Python', '.java': 'Java', '.cpp': 'C++', '.c': 'C',
    '.cs': 'C#', '.php': 'PHP', '.rb': 'Ruby', '.go': 'Go',
    '.rs': 'Rust', '.swift': 'Swift', '.kt': 'Kotlin',

    # Scripting Languages
    '.sh': 'Shell Script', '.bat': 'Batch', '.ps1': 'PowerShell',
    '.r': 'R', '.m': 'MATLAB', '.pl': 'Perl', '.lua': 'Lua',

    # Data & Config
    '.json': 'JSON', '.xml': 'XML', '.yaml': 'YAML', '.yml': 'YAML',
    '.toml': 'TOML', '.ini': 'INI', '.cfg': 'Config', '.conf': 'Config',
    '.sql': 'SQL', '.md': 'Markdown', '.txt': 'Text',

    # Mobile Development
    '.dart': 'Dart', '.scala': 'Scala',

    # Other
    '.dockerfile': 'Dockerfile', '.dockerignore': 'Docker Ignore',
    '.gitignore': 'Git Ignore', '.gitattributes': 'Git Attributes'
}

# Project type detection indicators
PROJECT_TYPE_INDICATORS = {
    'web': ['.html', '.css', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte'],
    'backend': ['.py', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs'],
    'mobile': ['.dart', '.swift', '.kt', '.java'],
    'data_science': ['.py', '.r', '.m', '.ipynb'],
    'devops': ['.dockerfile', '.yml', '.yaml', '.sh', '.bat', '.ps1'],
    'documentation': ['.md', '.txt', '.rst'],
    'database': ['.sql', '.db', '.sqlite']
}

# Document types
DOCUMENT_EXTENSIONS = {
    '.md': 'Markdown',
    '.txt': 'Text',
    '.pdf': 'PDF',
    '.doc': 'Word Document',
    '.docx': 'Word Document',
    '.rst': 'reStructuredText',
}

# Design file types
DESIGN_EXTENSIONS = {
    '.png': 'PNG Image',
    '.jpg': 'JPEG Image',
    '.jpeg': 'JPEG Image',
    '.gif': 'GIF Image',
    '.svg': 'SVG Vector',
    '.psd': 'Photoshop',
    '.ai': 'Illustrator',
    '.sketch': 'Sketch',
    '.fig': 'Figma',
}


