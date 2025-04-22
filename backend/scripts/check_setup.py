"""
Check Setup

This script checks if the backend is properly set up.
"""

import os
import sys
import importlib.util

def check_module(module_name):
    """
    Check if a module can be imported.
    
    Args:
        module_name: Name of the module
        
    Returns:
        bool: True if the module can be imported, False otherwise
    """
    try:
        importlib.import_module(module_name)
        return True
    except ImportError as e:
        print(f"Error importing {module_name}: {e}")
        return False

def main():
    """Check if the backend is properly set up."""
    print("Checking backend setup...")
    
    # Get the path to the backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Add the backend directory to the Python path
    sys.path.insert(0, os.path.dirname(backend_dir))
    
    # Check if the backend package can be imported
    if check_module('backend'):
        print("✓ Backend package can be imported")
    else:
        print("✗ Backend package cannot be imported")
    
    # Check if core nodes can be imported
    if check_module('backend.core_nodes'):
        print("✓ Core nodes package can be imported")
    else:
        print("✗ Core nodes package cannot be imported")
    
    # Check if plugins can be imported
    if check_module('backend.plugins'):
        print("✓ Plugins package can be imported")
    else:
        print("✗ Plugins package cannot be imported")
    
    # Check if app can be imported
    if check_module('backend.app'):
        print("✓ App package can be imported")
    else:
        print("✗ App package cannot be imported")
    
    print("Setup check complete.")

if __name__ == "__main__":
    main()
