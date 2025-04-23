"""
Enhanced Core Node Registry

This module provides an enhanced registry for core nodes with improved
discovery, categorization, and management.
"""

import os
import sys
import json
import time
import logging
import importlib.util
import inspect
from typing import Dict, Any, List, Optional, Type, Set, Tuple
from datetime import datetime

from backend.core_nodes.enhanced_base_node import EnhancedBaseNode
from backend.app.models.plugin_metadata import PluginMetadata, NodeCategory

# Configure logger
logger = logging.getLogger("workflow_builder")


class NodeRegistrationError(Exception):
    """Exception raised when a node fails to register."""
    pass


class EnhancedCoreNodeRegistry:
    """Enhanced registry for core nodes."""
    
    _instance = None
    
    def __new__(cls):
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super(EnhancedCoreNodeRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry."""
        if self._initialized:
            return
        
        # Node storage
        self.nodes: Dict[str, Type[EnhancedBaseNode]] = {}
        self.node_instances: Dict[str, EnhancedBaseNode] = {}
        self.node_metadata: Dict[str, PluginMetadata] = {}
        
        # Categorization
        self.categories: Dict[str, List[str]] = {}
        self.tags: Dict[str, List[str]] = {}
        
        # Performance metrics
        self.performance_metrics = {
            "load_time": 0.0,
            "discovery_time": 0.0,
            "node_count": 0,
            "category_count": 0,
            "error_count": 0
        }
        
        # Initialization state
        self._initialized = False
    
    def initialize(self, core_nodes_dir: Optional[str] = None, registry_file: Optional[str] = None) -> None:
        """
        Initialize the registry.
        
        Args:
            core_nodes_dir: Directory containing core nodes
            registry_file: Path to the registry file
        """
        if self._initialized:
            return
        
        start_time = time.time()
        
        # Set default paths if not provided
        if not core_nodes_dir:
            # Get the path to the backend directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            core_nodes_dir = os.path.join(backend_dir, "core_nodes")
        
        if not registry_file:
            # Get the path to the backend directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            registry_file = os.path.join(backend_dir, "config", "core_nodes_registry.json")
        
        # Load registry data
        registry_data = {}
        if os.path.exists(registry_file):
            try:
                with open(registry_file, "r") as f:
                    registry_data = json.load(f)
            except Exception as e:
                logger.error(f"Error loading registry file: {str(e)}")
        
        # Discover and register nodes
        discovery_start_time = time.time()
        self._discover_nodes(core_nodes_dir)
        self.performance_metrics["discovery_time"] = time.time() - discovery_start_time
        
        # Update registry with node metadata from registry file
        if "core_nodes" in registry_data:
            for node_data in registry_data["core_nodes"]:
                node_id = node_data.get("id")
                if node_id in self.nodes:
                    # Update metadata
                    if node_id in self.node_metadata:
                        metadata = self.node_metadata[node_id]
                        
                        # Update metadata with registry data
                        if "description" in node_data:
                            metadata.description = node_data["description"]
                        
                        if "category" in node_data:
                            metadata.category = node_data["category"]
                        
                        if "tags" in node_data:
                            metadata.tags = node_data["tags"]
                    
                    # Update category
                    category = node_data.get("category")
                    if category:
                        self._add_to_category(node_id, category)
        
        # Update performance metrics
        self.performance_metrics["load_time"] = time.time() - start_time
        self.performance_metrics["node_count"] = len(self.nodes)
        self.performance_metrics["category_count"] = len(self.categories)
        
        self._initialized = True
        logger.info(f"Enhanced core node registry initialized with {len(self.nodes)} nodes in {len(self.categories)} categories")
    
    def _discover_nodes(self, core_nodes_dir: str) -> None:
        """
        Discover and register nodes from the core nodes directory.
        
        Args:
            core_nodes_dir: Directory containing core nodes
        """
        if not os.path.exists(core_nodes_dir):
            logger.error(f"Core nodes directory not found: {core_nodes_dir}")
            return
        
        # Discover nodes in the root directory
        self._discover_nodes_in_directory(core_nodes_dir)
        
        # Discover nodes in category subdirectories
        for item in os.listdir(core_nodes_dir):
            category_dir = os.path.join(core_nodes_dir, item)
            if os.path.isdir(category_dir) and not item.startswith("__") and not item == "__pycache__":
                self._discover_nodes_in_directory(category_dir, category=item)
    
    def _discover_nodes_in_directory(self, directory: str, category: Optional[str] = None) -> None:
        """
        Discover and register nodes in a directory.
        
        Args:
            directory: Directory to search
            category: Category for discovered nodes
        """
        # Skip these files
        skip_files = ["__init__.py", "base_node.py", "enhanced_base_node.py"]
        
        for item in os.listdir(directory):
            # Skip special files and directories
            if item.startswith("__") or item in skip_files:
                continue
            
            # Process Python files
            if item.endswith(".py"):
                file_path = os.path.join(directory, item)
                module_name = item[:-3]  # Remove .py extension
                
                try:
                    # Load the module
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec is None:
                        logger.warning(f"Could not create spec for module {module_name}")
                        continue
                        
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    
                    # Find node classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, EnhancedBaseNode) and 
                            obj != EnhancedBaseNode):
                            
                            try:
                                # Register the node
                                self._register_node_class(obj, category)
                            except Exception as e:
                                logger.error(f"Error registering node class {name} from {file_path}: {str(e)}")
                                self.performance_metrics["error_count"] += 1
                
                except Exception as e:
                    logger.error(f"Error loading module {file_path}: {str(e)}")
                    self.performance_metrics["error_count"] += 1
    
    def _register_node_class(self, node_class: Type[EnhancedBaseNode], category: Optional[str] = None) -> None:
        """
        Register a node class.
        
        Args:
            node_class: Node class to register
            category: Category for the node
        """
        try:
            # Create an instance to get metadata
            instance = node_class()
            
            # Get node ID
            node_id = instance.id
            if not node_id:
                # Generate ID based on class name
                node_id = f"core.{node_class.__name__.lower()}"
                instance.id = node_id
            
            # Set category if provided
            if category:
                instance.category = category
            
            # Get metadata
            metadata = instance.get_metadata()
            
            # Register the node
            self.nodes[node_id] = node_class
            self.node_instances[node_id] = instance
            self.node_metadata[node_id] = metadata
            
            # Add to category
            self._add_to_category(node_id, instance.category)
            
            # Add to tags
            for tag in metadata.tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                if node_id not in self.tags[tag]:
                    self.tags[tag].append(node_id)
            
            logger.debug(f"Registered core node: {node_id} in category {instance.category}")
        
        except Exception as e:
            raise NodeRegistrationError(f"Error registering node class {node_class.__name__}: {str(e)}")
    
    def _add_to_category(self, node_id: str, category: str) -> None:
        """
        Add a node to a category.
        
        Args:
            node_id: Node ID
            category: Category
        """
        if not category:
            return
        
        # Normalize category
        category = category.upper()
        
        # Add to category
        if category not in self.categories:
            self.categories[category] = []
        if node_id not in self.categories[category]:
            self.categories[category].append(node_id)
    
    def register_node(self, node_id: str, node_class: Type[EnhancedBaseNode], category: Optional[str] = None) -> None:
        """
        Register a node with the registry.
        
        Args:
            node_id: Node ID
            node_class: Node class
            category: Category for the node
        """
        try:
            # Create an instance
            instance = node_class()
            
            # Set ID and category
            instance.id = node_id
            if category:
                instance.category = category
            
            # Get metadata
            metadata = instance.get_metadata()
            
            # Register the node
            self.nodes[node_id] = node_class
            self.node_instances[node_id] = instance
            self.node_metadata[node_id] = metadata
            
            # Add to category
            self._add_to_category(node_id, instance.category)
            
            # Add to tags
            for tag in metadata.tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                if node_id not in self.tags[tag]:
                    self.tags[tag].append(node_id)
            
            logger.info(f"Registered core node: {node_id} in category {instance.category}")
        
        except Exception as e:
            logger.error(f"Error registering node {node_id}: {str(e)}")
            self.performance_metrics["error_count"] += 1
    
    def get_node(self, node_id: str) -> Optional[Type[EnhancedBaseNode]]:
        """
        Get a node class by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node class or None if not found
        """
        return self.nodes.get(node_id)
    
    def get_node_instance(self, node_id: str) -> Optional[EnhancedBaseNode]:
        """
        Get a node instance by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node instance or None if not found
        """
        return self.node_instances.get(node_id)
    
    def get_node_metadata(self, node_id: str) -> Optional[PluginMetadata]:
        """
        Get node metadata by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node metadata or None if not found
        """
        return self.node_metadata.get(node_id)
    
    def get_all_nodes(self) -> Dict[str, Type[EnhancedBaseNode]]:
        """
        Get all node classes.
        
        Returns:
            Dictionary of node classes
        """
        return self.nodes
    
    def get_all_node_instances(self) -> Dict[str, EnhancedBaseNode]:
        """
        Get all node instances.
        
        Returns:
            Dictionary of node instances
        """
        return self.node_instances
    
    def get_all_node_metadata(self) -> Dict[str, PluginMetadata]:
        """
        Get all node metadata.
        
        Returns:
            Dictionary of node metadata
        """
        return self.node_metadata
    
    def get_nodes_by_category(self, category: str) -> List[str]:
        """
        Get nodes in a category.
        
        Args:
            category: Category
            
        Returns:
            List of node IDs
        """
        # Normalize category
        category = category.upper()
        
        return self.categories.get(category, [])
    
    def get_nodes_by_tag(self, tag: str) -> List[str]:
        """
        Get nodes with a tag.
        
        Args:
            tag: Tag
            
        Returns:
            List of node IDs
        """
        return self.tags.get(tag, [])
    
    def get_all_categories(self) -> List[str]:
        """
        Get all categories.
        
        Returns:
            List of categories
        """
        return list(self.categories.keys())
    
    def get_all_tags(self) -> List[str]:
        """
        Get all tags.
        
        Returns:
            List of tags
        """
        return list(self.tags.keys())
    
    def search_nodes(self, query: str) -> List[str]:
        """
        Search for nodes.
        
        Args:
            query: Search query
            
        Returns:
            List of matching node IDs
        """
        query = query.lower()
        results = []
        
        for node_id, metadata in self.node_metadata.items():
            # Check ID
            if query in node_id.lower():
                results.append(node_id)
                continue
            
            # Check name
            if query in metadata.name.lower():
                results.append(node_id)
                continue
            
            # Check description
            if query in metadata.description.lower():
                results.append(node_id)
                continue
            
            # Check tags
            for tag in metadata.tags:
                if query in tag.lower():
                    results.append(node_id)
                    break
        
        return results
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        return self.performance_metrics
