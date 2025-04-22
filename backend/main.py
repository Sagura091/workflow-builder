# backend/main.py
"""
Main entry point for the Workflow Builder API.

This module creates and exports the FastAPI application instance.
"""

import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(backend_dir)
sys.path.insert(0, parent_dir)  # Add parent directory to path

from backend.app import create_app

# Create the FastAPI application
app = create_app()

# This is used by uvicorn when running the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)