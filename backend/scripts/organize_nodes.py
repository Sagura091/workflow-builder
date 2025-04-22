#!/usr/bin/env python
"""
Script to organize plugins and core nodes in the workflow builder backend.
This script will:
1. Identify duplicate files between plugins and core_nodes
2. Move plugins to their appropriate category directories
3. Remove duplicates from the root plugins directory
4. Organize core nodes according to the registry
"""

import os
import shutil
import re
import sys
import json
from typing import Dict, List, Set, Tuple, Any

# Define the root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the plugins and core_nodes directories
PLUGINS_DIR = os.path.join(ROOT_DIR, "plugins")
CORE_NODES_DIR = os.path.join(ROOT_DIR, "core_nodes")
CONFIG_DIR = os.path.join(ROOT_DIR, "config")

# Path to the core nodes registry
CORE_NODES_REGISTRY_PATH = os.path.join(CONFIG_DIR, "core_nodes_registry.json")

# Define the category directories
PLUGIN_CATEGORIES = {
    "text_processing": ["text", "string", "nlp", "language", "tokenize", "analyze", "split", "uppercase", "lowercase"],
    "data_handling": ["data", "filter", "map", "sort", "merge", "transform", "convert", "json", "csv", "array", "object"],
    "web_api": ["http", "api", "request", "response", "web", "url", "fetch"],
    "file_operations": ["file", "read", "write", "save", "load", "import", "export"],
    "control_flow": ["flow", "conditional", "loop", "switch", "branch", "if", "else", "while", "for", "trigger"]
}

# Define the core node categories
CORE_NODE_CATEGORIES = {
    "control_flow": ["begin", "end", "conditional", "loop", "switch", "branch", "if", "else", "while", "for", "trigger"],
    "data": ["variable", "object", "property", "array", "json", "csv"],
    "file_storage": ["file", "read", "write", "save", "load", "import", "export"],
    "math": ["math", "add", "subtract", "multiply", "divide", "calculate", "number", "format"],
    "text": ["text", "string", "template", "format", "regex", "replace", "concat"],
    "utilities": ["delay", "logger", "random", "uuid", "date", "time"],
    "web_api": ["http", "api", "request", "response", "web", "url", "fetch"]
}

# Define files that should be kept in the root plugins directory
KEEP_IN_ROOT = ["base_plugin.py", "__init__.py"]

# Define duplicates that should be removed from plugins (keep in core_nodes)
DUPLICATES_TO_REMOVE = [
    "conditional.py",
    "data_merger.py",
    "file_reader.py",
    "http_request.py",
    "loop.py",
    "input_text.py",
    "output_text.py"
]

def get_all_python_files(directory: str) -> List[str]:
    """Get all Python files in a directory."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                python_files.append(os.path.join(root, file))
    return python_files

def get_file_content(file_path: str) -> str:
    """Get the content of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read file {file_path}: {e}")
        return ""

def determine_category(file_path: str, file_content: str, categories: Dict[str, List[str]]) -> str:
    """Determine the category of a file based on its name and content."""
    file_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(file_name)[0]

    # Check if the file name contains any category keywords
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in file_name_without_ext.lower():
                return category

    # Check if the file content contains any category keywords
    for category, keywords in categories.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', file_content.lower()):
                return category

    # Default category
    print(f"No category found for {file_path}, using default category 'utilities'")
    return "utilities"

def find_duplicates() -> Set[str]:
    """Find duplicate files between plugins and core_nodes."""
    plugin_files = [os.path.basename(f) for f in get_all_python_files(PLUGINS_DIR)]
    core_node_files = [os.path.basename(f) for f in get_all_python_files(CORE_NODES_DIR)]

    return set(plugin_files) & set(core_node_files)

def organize_plugins() -> None:
    """Organize plugins into category directories."""
    # Create all category directories if they don't exist
    for category in PLUGIN_CATEGORIES:
        category_dir = os.path.join(PLUGINS_DIR, category)
        os.makedirs(category_dir, exist_ok=True)

    # Create a utilities category if it doesn't exist
    utilities_dir = os.path.join(PLUGINS_DIR, "utilities")
    os.makedirs(utilities_dir, exist_ok=True)

    # Get all Python files in the plugins directory
    plugin_files = [f for f in get_all_python_files(PLUGINS_DIR)
                   if os.path.dirname(f) == PLUGINS_DIR]  # Only files in the root plugins directory

    # Find duplicates
    duplicates = find_duplicates()
    print(f"Found {len(duplicates)} duplicate files between plugins and core_nodes:")
    for duplicate in duplicates:
        print(f"  - {duplicate}")

    # Organize plugins
    for file_path in plugin_files:
        file_name = os.path.basename(file_path)

        # Skip files that should be kept in the root directory
        if file_name in KEEP_IN_ROOT:
            print(f"Keeping {file_name} in the root plugins directory")
            continue

        # Remove duplicates
        if file_name in DUPLICATES_TO_REMOVE:
            print(f"Removing duplicate {file_name} from plugins (keeping in core_nodes)")
            os.remove(file_path)
            continue

        # Determine the category
        file_content = get_file_content(file_path)
        category = determine_category(file_path, file_content, PLUGIN_CATEGORIES)

        # Move the file to the category directory
        category_dir = os.path.join(PLUGINS_DIR, category)
        dest_path = os.path.join(category_dir, file_name)

        # Ensure the category directory exists
        os.makedirs(category_dir, exist_ok=True)

        try:
            print(f"Moving {file_name} to {category} category")
            shutil.copy2(file_path, dest_path)

            # Remove the original file
            os.remove(file_path)
        except Exception as e:
            print(f"Error moving {file_name} to {category} category: {e}")

def load_core_nodes_registry() -> List[Dict[str, Any]]:
    """Load the core nodes registry from the JSON file."""
    if not os.path.exists(CORE_NODES_REGISTRY_PATH):
        print(f"Warning: Core nodes registry not found at {CORE_NODES_REGISTRY_PATH}")
        return []

    try:
        with open(CORE_NODES_REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry_data = json.load(f)
        return registry_data.get("core_nodes", [])
    except Exception as e:
        print(f"Error loading core nodes registry: {e}")
        return []

def organize_core_nodes() -> None:
    """Organize core nodes into category directories."""
    # Create category directories if they don't exist
    for category in CORE_NODE_CATEGORIES:
        category_dir = os.path.join(CORE_NODES_DIR, category)
        os.makedirs(category_dir, exist_ok=True)

    # Load the core nodes registry
    core_nodes_registry = load_core_nodes_registry()
    registry_map = {entry["file"]: entry for entry in core_nodes_registry}

    # Get all Python files in the core_nodes directory
    core_node_files = [f for f in get_all_python_files(CORE_NODES_DIR)
                      if os.path.dirname(f) == CORE_NODES_DIR]  # Only files in the root core_nodes directory

    # Organize core nodes
    for file_path in core_node_files:
        file_name = os.path.basename(file_path)

        # Skip __init__.py and base_node.py
        if file_name in ["__init__.py", "base_node.py"]:
            print(f"Keeping {file_name} in the root core_nodes directory")
            continue

        # Check if the file is in the registry
        if file_name in registry_map:
            # Use the category from the registry
            registry_entry = registry_map[file_name]
            category = registry_entry["category"]
            print(f"Using registry: {file_name} -> {category} category")
        else:
            # Determine the category based on file content
            file_content = get_file_content(file_path)
            category = determine_category(file_path, file_content, CORE_NODE_CATEGORIES)
            print(f"No registry entry: {file_name} -> {category} category (based on content)")

            # Add to registry for future use
            node_id = f"core.{os.path.splitext(file_name)[0]}"
            new_entry = {
                "id": node_id,
                "file": file_name,
                "category": category,
                "description": f"Auto-categorized {os.path.splitext(file_name)[0]} node"
            }
            core_nodes_registry.append(new_entry)

        # Move the file to the category directory
        category_dir = os.path.join(CORE_NODES_DIR, category)
        dest_path = os.path.join(category_dir, file_name)

        # Ensure the category directory exists
        os.makedirs(category_dir, exist_ok=True)

        try:
            print(f"Moving {file_name} to {category} category")
            shutil.copy2(file_path, dest_path)

            # Remove the original file
            os.remove(file_path)
        except Exception as e:
            print(f"Error moving {file_name} to {category} category: {e}")

    # Update the registry with any new entries
    if core_nodes_registry:
        try:
            registry_data = {"core_nodes": core_nodes_registry}
            with open(CORE_NODES_REGISTRY_PATH, "w", encoding="utf-8") as f:
                json.dump(registry_data, f, indent=2)
            print(f"Updated core nodes registry at {CORE_NODES_REGISTRY_PATH}")
        except Exception as e:
            print(f"Error updating core nodes registry: {e}")

def create_init_files() -> None:
    """Create __init__.py files in all directories."""
    # Create __init__.py in plugins directory
    init_path = os.path.join(PLUGINS_DIR, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("# This file is required to make Python treat the directory as a package\n")

    # Create __init__.py in core_nodes directory
    init_path = os.path.join(CORE_NODES_DIR, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("# This file is required to make Python treat the directory as a package\n")

    # Create __init__.py in all plugin category directories
    for category in PLUGIN_CATEGORIES:
        category_dir = os.path.join(PLUGINS_DIR, category)
        init_path = os.path.join(category_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w", encoding="utf-8") as f:
                f.write(f"# This file is required to make Python treat the {category} directory as a package\n")

    # Create __init__.py in all core_node category directories
    for category in CORE_NODE_CATEGORIES:
        category_dir = os.path.join(CORE_NODES_DIR, category)
        init_path = os.path.join(category_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w", encoding="utf-8") as f:
                f.write(f"# This file is required to make Python treat the {category} directory as a package\n")

def main() -> None:
    """Main function."""
    print("Starting organization of plugins and core nodes...")

    # Check if the directories exist
    if not os.path.exists(PLUGINS_DIR):
        print(f"Error: Plugins directory {PLUGINS_DIR} does not exist")
        sys.exit(1)

    if not os.path.exists(CORE_NODES_DIR):
        print(f"Error: Core nodes directory {CORE_NODES_DIR} does not exist")
        sys.exit(1)

    # Create config directory if it doesn't exist
    if not os.path.exists(CONFIG_DIR):
        print(f"Creating config directory at {CONFIG_DIR}")
        os.makedirs(CONFIG_DIR, exist_ok=True)

    # Ask for confirmation
    print("\nThis script will:")
    print("1. Identify duplicate files between plugins and core_nodes")
    print("2. Move plugins to their appropriate category directories")
    print("3. Remove duplicates from the root plugins directory")
    print("4. Organize core nodes according to the registry")
    print("5. Update the core nodes registry with any new nodes")
    print("\nAre you sure you want to continue? (y/n)")

    choice = input().lower()
    if choice != "y" and choice != "yes":
        print("Operation cancelled")
        sys.exit(0)

    # Organize plugins
    print("\nOrganizing plugins...")
    organize_plugins()

    # Organize core nodes
    print("\nOrganizing core nodes...")
    organize_core_nodes()

    # Create __init__.py files
    print("\nCreating __init__.py files...")
    create_init_files()

    print("\nOrganization complete!")

if __name__ == "__main__":
    main()
