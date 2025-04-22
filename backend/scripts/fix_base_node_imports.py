"""
Fix Base Node Imports

This script fixes imports of the BaseNode class in all core node files.
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
    
    # Replace relative imports of BaseNode with absolute imports
    content = re.sub(r'from \.\.\.\. import BaseNode', 'from backend.core_nodes.base_node import BaseNode', content)
    content = re.sub(r'from \.\.\.\.([\w\.]+) import BaseNode', 'from backend.core_nodes.base_node import BaseNode', content)
    content = re.sub(r'from \.\.\. import BaseNode', 'from backend.core_nodes.base_node import BaseNode', content)
    content = re.sub(r'from \.\.\.([\w\.]+) import BaseNode', 'from backend.core_nodes.base_node import BaseNode', content)
    content = re.sub(r'from \.\. import BaseNode', 'from backend.core_nodes.base_node import BaseNode', content)
    content = re.sub(r'from \.\.([\w\.]+) import BaseNode', 'from backend.core_nodes.base_node import BaseNode', content)
    content = re.sub(r'from \. import BaseNode', 'from backend.core_nodes.base_node import BaseNode', content)
    content = re.sub(r'from \.([\w\.]+) import BaseNode', 'from backend.core_nodes.base_node import BaseNode', content)
    
    # Replace any other incorrect imports of BaseNode
    content = re.sub(r'from backend\.core_nodes\.[\w\.]+\.base_node import BaseNode', 'from backend.core_nodes.base_node import BaseNode', content)
    
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
            if file.endswith('.py') and not file.startswith('__') and file != 'base_node.py':
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
