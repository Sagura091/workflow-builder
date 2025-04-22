"""
Node Types Controller

This module provides controllers for node types.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from backend.app.services.node_registry import NodeRegistry

class NodeTypesController:
    """Controller for node types operations."""

    def __init__(self, node_registry: NodeRegistry):
        self.node_registry = node_registry

    def get_node_types(self) -> Dict[str, Any]:
        """
        Get all node types.

        Returns:
            dict: A dictionary of all node types
        """
        return self.node_registry.get_node_types()

    def get_core_nodes(self) -> List[Dict[str, Any]]:
        """
        Get all core nodes.

        Returns:
            list: A list of all core nodes
        """
        node_types = self.node_registry.get_node_types()
        return node_types.get("coreNodes", [])

    def get_plugins(self) -> List[Dict[str, Any]]:
        """
        Get all plugins.

        Returns:
            list: A list of all plugins
        """
        node_types = self.node_registry.get_node_types()
        return node_types.get("plugins", [])

    def get_core_nodes_by_directory(self) -> Dict[str, List[Dict[str, Any]]]:
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

        # Get all core nodes from the node registry
        node_types = self.node_registry.get_node_types()
        core_nodes = node_types.get("coreNodes", [])

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

    def get_node_type(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node type by ID.

        Args:
            node_id (str): The ID of the node type

        Returns:
            dict: The node type, or None if not found
        """
        node_types = self.node_registry.get_node_types()

        # Check core nodes
        for node in node_types.get("coreNodes", []):
            if node.get("id") == node_id:
                return node

        # Check plugins
        for node in node_types.get("plugins", []):
            if node.get("id") == node_id:
                return node

        return None
