"""
Run Script for Workflow Builder Backend

This script runs the Workflow Builder backend application.
It can run either the standard or versioned application.
"""

import logging
import uvicorn
import argparse
import os
import sys
import webbrowser
import time
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Workflow Builder backend")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to bind to (default: 8001)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--versioned",
        action="store_true",
        help="Run the versioned application"
    )
    parser.add_argument(
        "--version",
        type=str,
        default=None,
        help="Set the current version (only used with --versioned)"
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the browser after starting the server"
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Don't display the banner"
    )
    return parser.parse_args()

def display_banner():
    """Display a banner with information about the application."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                         WORKFLOW BUILDER BACKEND                             ║
║                                                                              ║
║  A powerful workflow engine with support for plugins and dynamic execution   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def open_browser_after_delay(url, delay=2):
    """Open the browser after a delay."""
    def _open_browser():
        time.sleep(delay)
        webbrowser.open(url)

    thread = threading.Thread(target=_open_browser)
    thread.daemon = True
    thread.start()

def main():
    """Run the Workflow Builder backend."""
    args = parse_args()

    # Display banner
    if not args.no_banner:
        display_banner()

    # Add the backend directory to the Python path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(backend_dir)
    sys.path.insert(0, parent_dir)  # Add parent directory to path

    # Prepare URL for browser
    url = f"http://{args.host}:{args.port}"
    if args.host == "0.0.0.0":
        browser_url = f"http://localhost:{args.port}"
    else:
        browser_url = url

    # Open browser if requested
    if args.open_browser:
        open_browser_after_delay(browser_url)

    if args.versioned:
        # Import here to avoid circular imports
        try:
            from backend.app.versioning import version_manager

            # Set the current version if specified
            if args.version:
                try:
                    version_manager.set_current_version(args.version)
                    logger.info(f"Set current version to {args.version}")
                except ValueError as e:
                    logger.error(f"Error setting version: {e}")
                    return

            # Log the current version
            logger.info(f"Running with version {version_manager.current_version}")

            # Run the versioned application
            logger.info(f"Starting versioned Workflow Builder API server at {url}")
            logger.info(f"Press Ctrl+C to stop the server")
            uvicorn.run(
                "backend.app.main_versioned:app",
                host=args.host,
                port=args.port,
                reload=args.reload
            )
        except ImportError as e:
            logger.error(f"Error importing versioning module: {e}")
            logger.error("Make sure the versioning module is properly installed.")
            return
    else:
        # Run the standard application
        logger.info(f"Starting Workflow Builder API server at {url}")
        logger.info(f"Press Ctrl+C to stop the server")
        uvicorn.run(
            "backend.app.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )

if __name__ == "__main__":
    main()
