"""
Fix All Imports

This script fixes all imports in the codebase to use absolute imports.
Run this script once after cloning the repository or when making significant changes.
"""

import os
import sys
import subprocess
import importlib.util

def main():
    """Fix all imports in the codebase."""
    print("Fixing all imports in the codebase...")
    
    # Get the path to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the backend directory to the Python path
    parent_dir = os.path.dirname(backend_dir)
    sys.path.insert(0, parent_dir)  # Add parent directory to path
    
    # Create a __init__.py file in core_nodes directory if it doesn't exist
    core_nodes_dir = os.path.join(backend_dir, 'core_nodes')
    if not os.path.exists(os.path.join(core_nodes_dir, '__init__.py')):
        with open(os.path.join(core_nodes_dir, '__init__.py'), 'w') as f:
            f.write('# This file is required to make Python treat the directory as a package\n')
    
    # Create __init__.py files in core_nodes subdirectories
    for root, dirs, files in os.walk(core_nodes_dir):
        for dir_name in dirs:
            if not dir_name.startswith('__'):
                init_file = os.path.join(root, dir_name, '__init__.py')
                if not os.path.exists(init_file):
                    with open(init_file, 'w') as f:
                        f.write('# This file is required to make Python treat the directory as a package\n')
    
    # Create a __init__.py file in plugins directory if it doesn't exist
    plugins_dir = os.path.join(backend_dir, 'plugins')
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
    if not os.path.exists(os.path.join(plugins_dir, '__init__.py')):
        with open(os.path.join(plugins_dir, '__init__.py'), 'w') as f:
            f.write('# This file is required to make Python treat the directory as a package\n')
    
    # Create __init__.py files in plugins subdirectories
    for root, dirs, files in os.walk(plugins_dir):
        for dir_name in dirs:
            if not dir_name.startswith('__'):
                init_file = os.path.join(root, dir_name, '__init__.py')
                if not os.path.exists(init_file):
                    with open(init_file, 'w') as f:
                        f.write('# This file is required to make Python treat the directory as a package\n')
    
    # Run all import fixing scripts
    scripts_dir = os.path.join(backend_dir, 'scripts')
    
    # Fix imports in core nodes and plugins
    fix_imports_script = os.path.join(scripts_dir, 'fix_imports.py')
    if os.path.exists(fix_imports_script):
        print("Running fix_imports.py...")
        subprocess.run([sys.executable, fix_imports_script], check=True)
    
    # Fix imports in core nodes
    fix_core_nodes_imports_script = os.path.join(scripts_dir, 'fix_core_nodes_imports.py')
    if os.path.exists(fix_core_nodes_imports_script):
        print("Running fix_core_nodes_imports.py...")
        subprocess.run([sys.executable, fix_core_nodes_imports_script], check=True)
    
    # Fix imports in base node
    fix_base_node_imports_script = os.path.join(scripts_dir, 'fix_base_node_imports.py')
    if os.path.exists(fix_base_node_imports_script):
        print("Running fix_base_node_imports.py...")
        subprocess.run([sys.executable, fix_base_node_imports_script], check=True)
    
    # Fix imports in app
    fix_app_imports_script = os.path.join(scripts_dir, 'fix_app_imports.py')
    if os.path.exists(fix_app_imports_script):
        print("Running fix_app_imports.py...")
        subprocess.run([sys.executable, fix_app_imports_script], check=True)
    
    print("All imports fixed successfully!")
    print("You can now run the backend with 'python run.py'")

if __name__ == "__main__":
    main()
