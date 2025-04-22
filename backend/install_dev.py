"""
Install the backend in development mode.

This script installs the backend package in development mode, which allows you to
make changes to the code without having to reinstall the package.
"""

import os
import subprocess
import sys

def main():
    """Install the backend in development mode."""
    # Get the path to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Install the backend in development mode
    print(f"Installing backend in development mode from {backend_dir}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", backend_dir])
    
    print("Backend installed in development mode.")
    print("You can now import the backend package from anywhere.")

if __name__ == "__main__":
    main()
