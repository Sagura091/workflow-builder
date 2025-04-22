#!/usr/bin/env python
"""
Script to generate metadata for all nodes (core nodes and plugins) in a format that the frontend can use.
This script will:
1. Load all core nodes from the core_nodes_registry.json file
2. Load all plugins from the plugins directory
3. Generate metadata for each node
4. Save the metadata to a JSON file that the frontend can use
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional

# Define the root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the directories
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
CORE_NODES_DIR = os.path.join(ROOT_DIR, "core_nodes")
PLUGINS_DIR = os.path.join(ROOT_DIR, "plugins")

# Define the output file
OUTPUT_FILE = os.path.join(CONFIG_DIR, "node_types.json")

# Path to the core nodes registry
CORE_NODES_REGISTRY_PATH = os.path.join(CONFIG_DIR, "core_nodes_registry.json")

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

def get_core_node_metadata(node_id: str, category: str) -> Optional[Dict[str, Any]]:
    """Get metadata for a core node."""
    # Construct the path to the core node file
    category_dir = os.path.join(CORE_NODES_DIR, category)
    file_name = f"{node_id.split('.')[-1]}.py"
    file_path = os.path.join(category_dir, file_name)
    
    if not os.path.exists(file_path):
        print(f"Warning: Core node file not found at {file_path}")
        return None
    
    # For now, return a basic metadata structure
    # In a real implementation, you would parse the Python file to extract the metadata
    return {
        "id": node_id,
        "name": node_id.split('.')[-1].replace('_', ' ').title(),
        "category": category.upper(),
        "description": f"Core node: {node_id}",
        "inputs": [],
        "outputs": [],
        "ui_properties": {
            "color": "#3498db",
            "icon": "cog",
            "width": 240
        }
    }

def generate_core_nodes_metadata() -> List[Dict[str, Any]]:
    """Generate metadata for all core nodes."""
    core_nodes = []
    registry = load_core_nodes_registry()
    
    for node in registry:
        node_id = node.get("id")
        category = node.get("category")
        
        if not node_id or not category:
            continue
        
        metadata = get_core_node_metadata(node_id, category)
        if metadata:
            core_nodes.append(metadata)
    
    return core_nodes

def generate_plugins_metadata() -> List[Dict[str, Any]]:
    """Generate metadata for all plugins."""
    # In a real implementation, you would use the PluginManager to load and extract metadata
    # For now, return a basic list of plugins
    return [
        {
            "id": "text_processing.text_analyzer",
            "name": "Text Analyzer",
            "category": "TEXT_PROCESSING",
            "description": "Analyze text and extract information",
            "inputs": [
                { "id": "text", "name": "Text", "type": "string", "required": True, "ui_properties": { "position": "left-top" } }
            ],
            "outputs": [
                { "id": "word_count", "name": "Word Count", "type": "number", "ui_properties": { "position": "right-top" } },
                { "id": "sentiment", "name": "Sentiment", "type": "number", "ui_properties": { "position": "right-center" } }
            ],
            "ui_properties": {
                "color": "#3498db",
                "icon": "font",
                "width": 240
            }
        },
        {
            "id": "data_handling.data_filter",
            "name": "Data Filter",
            "category": "DATA_HANDLING",
            "description": "Filter data based on conditions",
            "inputs": [
                { "id": "data", "name": "Data", "type": "array", "required": True, "ui_properties": { "position": "left-top" } },
                { "id": "condition", "name": "Condition", "type": "string", "ui_properties": { "position": "left-center" } }
            ],
            "outputs": [
                { "id": "filtered_data", "name": "Filtered Data", "type": "array", "ui_properties": { "position": "right-top" } }
            ],
            "ui_properties": {
                "color": "#e67e22",
                "icon": "filter",
                "width": 240
            }
        },
        {
            "id": "web_api.http_request",
            "name": "HTTP Request",
            "category": "WEB_API",
            "description": "Make HTTP requests to external APIs",
            "inputs": [
                { "id": "url", "name": "URL", "type": "string", "required": True, "ui_properties": { "position": "left-top" } },
                { "id": "method", "name": "Method", "type": "string", "ui_properties": { "position": "left-center" } },
                { "id": "headers", "name": "Headers", "type": "object", "ui_properties": { "position": "left-bottom" } }
            ],
            "outputs": [
                { "id": "response", "name": "Response", "type": "object", "ui_properties": { "position": "right-top" } },
                { "id": "status", "name": "Status", "type": "number", "ui_properties": { "position": "right-center" } }
            ],
            "ui_properties": {
                "color": "#9b59b6",
                "icon": "globe",
                "width": 240
            }
        }
    ]

def generate_node_types_json():
    """Generate the node_types.json file."""
    # Generate metadata for core nodes and plugins
    core_nodes = generate_core_nodes_metadata()
    plugins = generate_plugins_metadata()
    
    # Create the node_types.json structure
    node_types = {
        "coreNodes": core_nodes,
        "plugins": plugins
    }
    
    # Save the node_types.json file
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(node_types, f, indent=2)
        print(f"Successfully generated node_types.json at {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving node_types.json: {e}")

def main():
    """Main function."""
    print("Generating node metadata...")
    
    # Create config directory if it doesn't exist
    if not os.path.exists(CONFIG_DIR):
        print(f"Creating config directory at {CONFIG_DIR}")
        os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Generate the node_types.json file
    generate_node_types_json()
    
    print("Node metadata generation complete!")

if __name__ == "__main__":
    main()
