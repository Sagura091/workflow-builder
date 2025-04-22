"""
Fix Imports

This script fixes imports in core nodes and plugins to use absolute imports.
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

    # Replace relative imports with absolute imports
    content = re.sub(r'from \.\.\.', 'from backend.core_nodes', content)
    content = re.sub(r'from \.\.\.\.(\w+)', r'from backend.core_nodes.\1', content)

    # Replace 'from app.' with absolute imports
    content = re.sub(r'from app\.', 'from backend.app.', content)

    # Replace 'import app.' with absolute imports
    content = re.sub(r'import app\.', 'import backend.app.', content)

    # Replace 'from backend.core_nodes' with absolute imports
    content = re.sub(r'from backend\.core_nodes', 'from backend.core_nodes', content)

    # Replace 'from backend.plugins' with absolute imports
    content = re.sub(r'from backend\.plugins', 'from backend.plugins', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_imports_in_directory(directory):
    """
    Fix imports in all Python files in a directory.

    Args:
        directory: Path to the directory
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                print(f"Fixing imports in {file_path}")
                fix_imports_in_file(file_path)

def main():
    """Fix imports in core nodes and plugins."""
    # Get the path to the backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Fix imports in core nodes
    core_nodes_dir = os.path.join(backend_dir, 'core_nodes')
    if os.path.exists(core_nodes_dir):
        print(f"Fixing imports in core nodes directory: {core_nodes_dir}")
        fix_imports_in_directory(core_nodes_dir)

    # Fix imports in plugins
    plugins_dir = os.path.join(backend_dir, 'plugins')
    if os.path.exists(plugins_dir):
        print(f"Fixing imports in plugins directory: {plugins_dir}")
        fix_imports_in_directory(plugins_dir)

    print("Done fixing imports.")

if __name__ == "__main__":
    main()
