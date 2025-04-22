"""
Node Registry

This module provides a registry for all nodes (core and plugins) in the system.
"""

import json
from pathlib import Path

class NodeRegistry:
    """
    Registry for all nodes (core and plugins) in the system.

    This is implemented as a singleton to ensure there's only one registry
    throughout the application.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NodeRegistry, cls).__new__(cls)
            cls._instance.nodes = {}
        return cls._instance

    def register_node(self, node_id, node_class):
        """
        Register a node class with the registry.

        Args:
            node_id (str): The ID of the node (e.g., "core.text_input")
            node_class (class): The node class to register
        """
        self.nodes[node_id] = node_class

    def get_node(self, node_id):
        """
        Get a node class from the registry.

        Args:
            node_id (str): The ID of the node to retrieve

        Returns:
            class: The node class, or None if not found
        """
        return self.nodes.get(node_id)

    def get_all_nodes(self):
        """
        Get all registered nodes.

        Returns:
            dict: A dictionary mapping node IDs to node classes
        """
        return self.nodes

    def get_nodes_by_category(self, category):
        """
        Get all nodes in a specific category.

        Args:
            category (str): The category to filter by

        Returns:
            dict: A dictionary mapping node IDs to node classes for nodes in the category
        """
        return {
            node_id: node_class
            for node_id, node_class in self.nodes.items()
            if hasattr(node_class, 'category') and node_class.category == category
        }

    def get_node_types(self):
        """
        Get all node types from the config file.

        Returns:
            dict: A dictionary containing all node types
        """
        try:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'node_types.json'
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading node types: {e}")
            return {"coreNodes": [], "plugins": []}
