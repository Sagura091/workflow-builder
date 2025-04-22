"""
Core Node Registry Service

This module provides a registry for core nodes with directory-based organization.
"""

import json
import logging
import importlib.util
import inspect
from typing import Dict, List, Any, Optional, Type
from pathlib import Path

logger = logging.getLogger("workflow_builder")

class CoreNodeRegistry:
    """Registry for core nodes with directory-based organization."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CoreNodeRegistry, cls).__new__(cls)
            cls._instance.nodes = {}
            cls._instance.node_directories = {}
            cls._instance.node_metadata = {}
            cls._instance.initialized = False
        return cls._instance

    def initialize(self, core_nodes_dir: str = None):
        """Initialize the registry."""
        if self.initialized:
            return

        # Get the path to the core_nodes directory
        if core_nodes_dir is None:
            current_dir = Path(__file__).parent.parent.parent
            core_nodes_dir = current_dir / "core_nodes"
        else:
            core_nodes_dir = Path(core_nodes_dir)

        logger.info(f"Initializing core node registry from {core_nodes_dir}")

        # Load the core nodes registry for additional metadata
        registry_path = Path(__file__).parent.parent.parent / "config" / "core_nodes_registry.json"
        node_types_path = Path(__file__).parent.parent.parent / "config" / "node_types.json"
        registry_data = {}
        node_types_data = {}

        try:
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry_data = json.load(f)
                    logger.info(f"Loaded core nodes registry from {registry_path}")
        except Exception as e:
            logger.error(f"Error loading core nodes registry: {e}")

        try:
            if node_types_path.exists():
                with open(node_types_path, 'r') as f:
                    node_types_data = json.load(f)
                    logger.info(f"Loaded node types from {node_types_path}")
        except Exception as e:
            logger.error(f"Error loading node types: {e}")

        # Walk through the core_nodes directory
        if core_nodes_dir.exists():
            for category_dir in core_nodes_dir.iterdir():
                if category_dir.is_dir() and not category_dir.name.startswith('__'):
                    category_name = category_dir.name
                    logger.info(f"Loading core nodes from category: {category_name}")

                    # Create directory entry
                    if category_name not in self.node_directories:
                        self.node_directories[category_name] = []

                    # Load nodes from this category
                    for file_path in category_dir.glob("*.py"):
                        if file_path.name.startswith('__'):
                            continue

                        try:
                            # Load the module
                            module_name = file_path.stem
                            spec = importlib.util.spec_from_file_location(module_name, file_path)
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)

                            # Find node classes in the module
                            for name, obj in inspect.getmembers(module):
                                if (inspect.isclass(obj) and
                                    hasattr(obj, 'execute') and
                                    inspect.isfunction(getattr(obj, 'execute'))):

                                    # Create an instance to get the ID
                                    try:
                                        instance = obj()
                                        node_id = None

                                        # Try to get ID from get_metadata method first (preferred)
                                        if hasattr(instance, 'get_metadata'):
                                            try:
                                                metadata = instance.get_metadata()
                                                if hasattr(metadata, 'id') and metadata.id:
                                                    node_id = metadata.id
                                            except Exception as e:
                                                logger.debug(f"Error getting metadata for {name}: {e}")

                                        # Try to get ID from instance attributes if not found
                                        if not node_id and hasattr(instance, 'id') and instance.id:
                                            node_id = instance.id

                                        # Try to get ID from metadata if not found
                                        if not node_id and hasattr(instance, '__plugin_meta__') and hasattr(instance.__plugin_meta__, 'id'):
                                            node_id = instance.__plugin_meta__.id

                                        # Generate ID based on category and module name if not found
                                        if not node_id:
                                            node_id = f"core.{module_name}"

                                        # Register the node
                                        self.register_node(node_id, obj, category_name)
                                        logger.info(f"Registered core node: {node_id} in category {category_name}")
                                    except Exception as e:
                                        logger.error(f"Error instantiating node class {name} from {file_path}: {e}")
                        except Exception as e:
                            logger.error(f"Error loading module {file_path}: {e}")

        # Update registry with node metadata from registry file
        if "core_nodes" in registry_data:
            for node_data in registry_data["core_nodes"]:
                node_id = node_data.get("id")
                if node_id in self.nodes:
                    # Store metadata
                    self.node_metadata[node_id] = node_data

                    # Update directory if needed
                    category = node_data.get("category")
                    if category and category not in self.node_directories:
                        self.node_directories[category] = []

                    # Add to directory if not already there
                    if category and node_id not in self.node_directories[category]:
                        self.node_directories[category].append(node_id)

        # Update registry with node metadata from node_types.json file
        if "coreNodes" in node_types_data:
            for node_data in node_types_data["coreNodes"]:
                node_id = node_data.get("id")
                if node_id:
                    # Store metadata
                    self.node_metadata[node_id] = node_data

                    # Update directory if needed
                    category = node_data.get("category")
                    if category and category not in self.node_directories:
                        self.node_directories[category] = []

                    # Add to directory if not already there
                    if category and node_id not in self.node_directories[category]:
                        self.node_directories[category].append(node_id)

        self.initialized = True
        logger.info(f"Core node registry initialized with {len(self.nodes)} nodes in {len(self.node_directories)} categories")

    def register_node(self, node_id: str, node_class: Type, directory: str = None):
        """Register a node with the registry."""
        self.nodes[node_id] = node_class

        if directory:
            if directory not in self.node_directories:
                self.node_directories[directory] = []
            if node_id not in self.node_directories[directory]:
                self.node_directories[directory].append(node_id)

    def get_node(self, node_id: str) -> Optional[Type]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> Dict[str, Type]:
        """Get all nodes."""
        return self.nodes

    def get_nodes_by_directory(self, directory: str = None) -> Dict[str, List[str]]:
        """Get all nodes in a directory."""
        if directory:
            return {
                directory: self.node_directories.get(directory, [])
            }

        return self.node_directories

    def get_node_metadata(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a node."""
        if node_id in self.node_metadata:
            return self.node_metadata[node_id]

        # Try to get metadata from node instance
        node_class = self.get_node(node_id)
        if node_class:
            try:
                instance = node_class()
                metadata = None

                # Try to get metadata from get_metadata method first (preferred)
                if hasattr(instance, 'get_metadata'):
                    try:
                        metadata = instance.get_metadata()
                        if metadata:
                            # Convert Pydantic model to dict if needed
                            if hasattr(metadata, "model_dump"):
                                # Pydantic v2
                                metadata_dict = metadata.model_dump()
                            elif hasattr(metadata, "dict"):
                                # Pydantic v1
                                metadata_dict = metadata.dict()
                            else:
                                # Use as is
                                metadata_dict = metadata

                            self.node_metadata[node_id] = metadata_dict
                            return metadata_dict
                    except Exception as e:
                        logger.debug(f"Error getting metadata from get_metadata for node {node_id}: {e}")

                # Try to get metadata from __plugin_meta__ attribute
                if not metadata and hasattr(instance, '__plugin_meta__'):
                    metadata = instance.__plugin_meta__
                    if metadata:
                        self.node_metadata[node_id] = metadata
                        return metadata

                # Try to create metadata from instance attributes
                if not metadata and hasattr(instance, '_create_metadata_from_attributes'):
                    try:
                        metadata = instance._create_metadata_from_attributes()
                        if metadata:
                            self.node_metadata[node_id] = metadata
                            return metadata
                    except Exception as e:
                        logger.debug(f"Error creating metadata from attributes for node {node_id}: {e}")
            except Exception as e:
                logger.error(f"Error getting metadata for node {node_id}: {e}")

        return None

    def get_all_node_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all nodes."""
        result = {}

        for node_id in self.nodes:
            metadata = self.get_node_metadata(node_id)
            if metadata:
                result[node_id] = metadata

        return result
