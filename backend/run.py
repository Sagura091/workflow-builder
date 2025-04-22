import uvicorn
import argparse
import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(backend_dir)
sys.path.insert(0, parent_dir)  # Add parent directory to path

def main():
    """Run the FastAPI application with uvicorn."""
    parser = argparse.ArgumentParser(description="Run the Workflow Builder API server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    print(f"Starting Workflow Builder API server at http://{args.host}:{args.port}")

    # Import the app directly
    from backend.app.main import app

    # Run the app with uvicorn
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
