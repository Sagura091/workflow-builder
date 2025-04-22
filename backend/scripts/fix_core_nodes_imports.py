"""
Fix Core Nodes Imports

This script fixes imports in all core node files to use absolute imports.
"""

import os
import re
import sys

def fix_imports_in_file(file_path):
    """
    Fix imports in a file.
    
    Args:
        file_path: Path to the file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace 'from app.' with 'from backend.app.'
    content = re.sub(r'from app\.', 'from backend.app.', content)
    
    # Replace 'import app.' with 'import backend.app.'
    content = re.sub(r'import app\.', 'import backend.app.', content)
    
    # Replace relative imports with absolute imports
    content = re.sub(r'from \.\.\.\. import', 'from backend.core_nodes import', content)
    content = re.sub(r'from \.\.\.\.([\w\.]+) import', r'from backend.core_nodes.\1 import', content)
    content = re.sub(r'from \.\.\. import', 'from backend.core_nodes import', content)
    content = re.sub(r'from \.\.\.([\w\.]+) import', r'from backend.core_nodes.\1 import', content)
    content = re.sub(r'from \.\. import', 'from backend.core_nodes.control_flow import', content)
    content = re.sub(r'from \.\.([\w\.]+) import', r'from backend.core_nodes.control_flow.\1 import', content)
    content = re.sub(r'from \. import', 'from backend.core_nodes.control_flow import', content)
    content = re.sub(r'from \.([\w\.]+) import', r'from backend.core_nodes.control_flow.\1 import', content)
    
    # Add json import if needed
    if 'json.loads' in content or 'json.dumps' in content or 'json.JSONDecodeError' in content:
        if 'import json' not in content:
            content = 'import json\n' + content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_imports_in_directory(directory):
    """
    Fix imports in all Python files in a directory.
    
    Args:
        directory: Path to the directory
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                print(f"Fixing imports in {file_path}")
                fix_imports_in_file(file_path)

def main():
    """Fix imports in core nodes."""
    # Get the path to the backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Fix imports in core nodes
    core_nodes_dir = os.path.join(backend_dir, 'core_nodes')
    if os.path.exists(core_nodes_dir):
        print(f"Fixing imports in core nodes directory: {core_nodes_dir}")
        fix_imports_in_directory(core_nodes_dir)
    
    print("Done fixing imports in core nodes.")

if __name__ == "__main__":
    main()
