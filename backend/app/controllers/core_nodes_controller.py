"""
Core Nodes Controller

This module provides controllers for core nodes.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

class CoreNodesController:
    """Controller for core nodes operations."""
    
    @staticmethod
    def get_core_nodes_by_directory() -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all core nodes organized by their directory structure.
        
        Returns:
            dict: A dictionary mapping directory names to lists of core nodes
        """
        # Get the path to the core_nodes directory
        current_dir = Path(__file__).parent.parent.parent.parent
        core_nodes_dir = current_dir / "core_nodes"
        
        # Load the core nodes registry for additional metadata
        registry_path = current_dir / "config" / "core_nodes_registry.json"
        registry_data = {}
        
        try:
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry_data = json.load(f)
        except Exception as e:
            print(f"Error loading core nodes registry: {e}")
        
        # Load node types from the config directory
        node_types_file = current_dir / "config" / "node_types.json"
        core_nodes = []
        
        try:
            if node_types_file.exists():
                with open(node_types_file, 'r') as f:
                    node_types = json.load(f)
                    core_nodes = node_types.get("coreNodes", [])
        except Exception as e:
            print(f"Error loading node types: {e}")
        
        # Create a mapping of node IDs to node definitions
        node_map = {node.get("id"): node for node in core_nodes}
        
        # Organize nodes by directory
        result = {}
        
        # Walk through the core_nodes directory
        if core_nodes_dir.exists():
            for item in core_nodes_dir.iterdir():
                if item.is_dir() and not item.name.startswith('__'):
                    category_name = item.name
                    result[category_name] = []
                    
                    # Find all nodes in this category
                    for node_id, node in node_map.items():
                        # Check if this node belongs to this category
                        # First check the registry
                        node_belongs_to_category = False
                        
                        # Check in registry data
                        if "core_nodes" in registry_data:
                            for reg_node in registry_data["core_nodes"]:
                                if reg_node.get("id") == node_id and reg_node.get("category") == category_name:
                                    node_belongs_to_category = True
                                    break
                        
                        # If not found in registry, check by ID prefix
                        if not node_belongs_to_category:
                            # Node IDs are typically in the format 'core.category.name'
                            # or sometimes just 'core.name' where the category is implied
                            parts = node_id.split('.')
                            if len(parts) > 2:
                                if parts[1] == category_name:
                                    node_belongs_to_category = True
                        
                        if node_belongs_to_category:
                            result[category_name].append(node)
        
        return result
