"""
Versioned Core Node Registry

This module provides a core node registry that supports both legacy and
enhanced versions of core nodes, using the version manager to determine
which version to use.
"""

import os
import sys
import json
import logging
import importlib.util
import inspect
from typing import Dict, Any, List, Optional, Type, Set, Tuple

from backend.app.services.core_node_registry import CoreNodeRegistry
from backend.app.services.enhanced_core_node_registry import EnhancedCoreNodeRegistry
from backend.app.services.version_manager import VersionManager, ComponentType
from backend.core_nodes.enhanced_base_node import EnhancedBaseNode

# Configure logger
logger = logging.getLogger("workflow_builder")


class VersionedCoreNodeRegistry:
    """
    Core node registry that supports both legacy and enhanced versions.
    
    This registry uses the version manager to determine which version of a
    core node to use based on user preferences.
    """
    
    _instance = None
    
    def __new__(cls):
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super(VersionedCoreNodeRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry."""
        if self._initialized:
            return
        
        # Initialize registries
        self.legacy_registry = CoreNodeRegistry()
        self.enhanced_registry = EnhancedCoreNodeRegistry()
        
        # Initialize version manager
        self.version_manager = VersionManager()
        
        # Node cache
        self.node_cache = {}
        
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
        
        # Initialize legacy registry
        self.legacy_registry.initialize()
        
        # Initialize enhanced registry
        self.enhanced_registry.initialize(core_nodes_dir, registry_file)
        
        # Register mappings with version manager
        self._register_mappings()
        
        self._initialized = True
        logger.info("Versioned core node registry initialized")
    
    def _register_mappings(self) -> None:
        """Register mappings between legacy and enhanced nodes."""
        # Get all enhanced nodes
        enhanced_nodes = self.enhanced_registry.get_all_node_metadata()
        
        # Register mappings
        for enhanced_id, metadata in enhanced_nodes.items():
            # Check if this is an enhanced version of a legacy node
            if enhanced_id.startswith("core.enhanced_"):
                # Get the legacy ID
                legacy_id = enhanced_id.replace("enhanced_", "")
                
                # Check if the legacy node exists
                if self.legacy_registry.get_node_class(legacy_id):
                    # Register mapping
                    self.version_manager.register_mapping(
                        ComponentType.CORE_NODE,
                        legacy_id,
                        enhanced_id
                    )
    
    def get_node_class(self, node_id: str) -> Optional[Type]:
        """
        Get a node class by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node class or None if not found
        """
        # Check cache
        if node_id in self.node_cache:
            return self.node_cache[node_id]
        
        # Get the appropriate node ID based on preferences
        resolved_id = self.version_manager.get_component_id(ComponentType.CORE_NODE, node_id)
        
        # Check if this is an enhanced node
        if resolved_id.startswith("core.enhanced_"):
            node_class = self.enhanced_registry.get_node(resolved_id)
        else:
            node_class = self.legacy_registry.get_node_class(resolved_id)
        
        # Cache the result
        self.node_cache[node_id] = node_class
        
        return node_class
    
    def get_node_metadata(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get node metadata by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node metadata or None if not found
        """
        # Get the appropriate node ID based on preferences
        resolved_id = self.version_manager.get_component_id(ComponentType.CORE_NODE, node_id)
        
        # Check if this is an enhanced node
        if resolved_id.startswith("core.enhanced_"):
            metadata = self.enhanced_registry.get_node_metadata(resolved_id)
            if metadata:
                return metadata.dict()
        else:
            return self.legacy_registry.get_node_metadata(resolved_id)
        
        return None
    
    def get_all_node_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all nodes.
        
        Returns:
            Dictionary of node metadata
        """
        result = {}
        
        # Get all legacy nodes
        legacy_metadata = self.legacy_registry.get_all_node_metadata()
        
        # Get all enhanced nodes
        enhanced_metadata = self.enhanced_registry.get_all_node_metadata()
        
        # Get all mappings
        mappings = self.version_manager.get_all_mappings(ComponentType.CORE_NODE)
        
        # Get all preferences
        preferences = self.version_manager.get_all_preferences(ComponentType.CORE_NODE)
        
        # Add legacy nodes that don't have enhanced versions
        for node_id, metadata in legacy_metadata.items():
            if node_id not in mappings:
                result[node_id] = metadata
        
        # Add enhanced nodes that don't have legacy versions
        for node_id, metadata in enhanced_metadata.items():
            legacy_id = self.version_manager.get_legacy_id(ComponentType.CORE_NODE, node_id)
            if not legacy_id:
                result[node_id] = metadata.dict()
        
        # Add nodes based on preferences
        for legacy_id, enhanced_id in mappings.items():
            preference = preferences.get(legacy_id, self.version_manager.get_default_preference(ComponentType.CORE_NODE))
            
            if preference == "enhanced":
                # Use enhanced version
                if enhanced_id in enhanced_metadata:
                    result[legacy_id] = enhanced_metadata[enhanced_id].dict()
            else:
                # Use legacy version
                if legacy_id in legacy_metadata:
                    result[legacy_id] = legacy_metadata[legacy_id]
        
        return result
    
    def get_node_categories(self) -> Dict[str, List[str]]:
        """
        Get node categories.
        
        Returns:
            Dictionary of categories and their nodes
        """
        result = {}
        
        # Get all node metadata
        all_metadata = self.get_all_node_metadata()
        
        # Group by category
        for node_id, metadata in all_metadata.items():
            category = metadata.get("category", "CUSTOM").upper()
            
            if category not in result:
                result[category] = []
                
            result[category].append(node_id)
        
        return result
    
    def execute_node(self, node_id: str, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a node.
        
        Args:
            node_id: Node ID
            inputs: Input values
            config: Node configuration
            
        Returns:
            Output values
            
        Raises:
            Exception: If the node execution fails
        """
        # Get the appropriate node ID based on preferences
        resolved_id = self.version_manager.get_component_id(ComponentType.CORE_NODE, node_id)
        
        # Check if this is an enhanced node
        if resolved_id.startswith("core.enhanced_"):
            # Get node instance
            node_instance = self.enhanced_registry.get_node_instance(resolved_id)
            
            if node_instance:
                # Execute the node
                result = node_instance.safe_execute(config, inputs)
                
                # Return outputs
                return result.outputs
            else:
                raise Exception(f"Node not found: {resolved_id}")
        else:
            # Execute legacy node
            return self.legacy_registry.execute_node(resolved_id, inputs, config)
    
    def set_node_preference(self, node_id: str, preference: str) -> None:
        """
        Set the preference for a node.
        
        Args:
            node_id: Node ID
            preference: Preference ("legacy" or "enhanced")
        """
        self.version_manager.set_preference(ComponentType.CORE_NODE, node_id, preference)
        
        # Clear cache
        if node_id in self.node_cache:
            del self.node_cache[node_id]
    
    def get_node_preference(self, node_id: str) -> str:
        """
        Get the preference for a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            Preference ("legacy" or "enhanced")
        """
        return self.version_manager.get_preference(ComponentType.CORE_NODE, node_id)
    
    def set_default_preference(self, preference: str) -> None:
        """
        Set the default preference for core nodes.
        
        Args:
            preference: Preference ("legacy" or "enhanced")
        """
        self.version_manager.set_default_preference(ComponentType.CORE_NODE, preference)
        
        # Clear cache
        self.node_cache.clear()
    
    def get_default_preference(self) -> str:
        """
        Get the default preference for core nodes.
        
        Returns:
            Preference ("legacy" or "enhanced")
        """
        return self.version_manager.get_default_preference(ComponentType.CORE_NODE)
    
    def get_available_versions(self, node_id: str) -> Dict[str, str]:
        """
        Get available versions for a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            Dictionary of available versions
        """
        result = {}
        
        # Check if this is a legacy node with an enhanced version
        enhanced_id = self.version_manager.get_enhanced_id(ComponentType.CORE_NODE, node_id)
        
        if enhanced_id:
            # This is a legacy node
            result["legacy"] = node_id
            result["enhanced"] = enhanced_id
            return result
        
        # Check if this is an enhanced node with a legacy version
        legacy_id = self.version_manager.get_legacy_id(ComponentType.CORE_NODE, node_id)
        
        if legacy_id:
            # This is an enhanced node
            result["legacy"] = legacy_id
            result["enhanced"] = node_id
            return result
        
        # No mapping found, return the original ID as the only version
        if node_id.startswith("core.enhanced_"):
            result["enhanced"] = node_id
        else:
            result["legacy"] = node_id
            
        return result
