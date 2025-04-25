"""
Version-Aware Component Registry

This module provides registries for versioned components like core nodes,
plugins, and types.
"""

import importlib
import inspect
import logging
import os
import pkgutil
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

from pydantic import BaseModel, Field

from .version_manager import version_manager, VersionedFeature

logger = logging.getLogger(__name__)


class VersionedComponent(BaseModel):
    """Base model for versioned components."""
    id: str
    name: str
    version: str
    introduced_in: str
    deprecated_in: Optional[str] = None
    removed_in: Optional[str] = None
    
    def is_available(self, system_version: str) -> bool:
        """Check if this component is available in the given system version."""
        import semver
        
        if semver.compare(system_version, self.introduced_in) < 0:
            return False
        
        if self.removed_in and semver.compare(system_version, self.removed_in) >= 0:
            return False
            
        return True
    
    def is_deprecated(self, system_version: str) -> bool:
        """Check if this component is deprecated in the given system version."""
        if not self.deprecated_in:
            return False
            
        import semver
        return (semver.compare(system_version, self.deprecated_in) >= 0 and 
                (not self.removed_in or semver.compare(system_version, self.removed_in) < 0))


class VersionedCoreNode(VersionedComponent):
    """Model for a versioned core node."""
    category: str
    description: str
    inputs: Dict[str, str] = Field(default_factory=dict)
    outputs: Dict[str, str] = Field(default_factory=dict)
    config_schema: Dict[str, Any] = Field(default_factory=dict)
    implementation: Optional[Callable] = None
    
    class Config:
        arbitrary_types_allowed = True


class VersionedType(VersionedComponent):
    """Model for a versioned type."""
    base_type: Optional[str] = None
    validators: List[Callable] = Field(default_factory=list)
    converters: Dict[str, Callable] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class VersionedCoreNodeRegistry:
    """
    Registry for versioned core nodes.
    
    This registry manages different versions of core nodes and provides
    version-aware access to them.
    """
    
    def __init__(self):
        self.nodes: Dict[str, Dict[str, VersionedCoreNode]] = {}
        self.categories: Set[str] = set()
    
    def register_node(self, node: VersionedCoreNode):
        """Register a core node with version information."""
        if node.id not in self.nodes:
            self.nodes[node.id] = {}
        
        self.nodes[node.id][node.version] = node
        self.categories.add(node.category)
        
        logger.info(f"Registered core node {node.id} version {node.version}")
    
    def get_node(self, 
                node_id: str, 
                version: Optional[str] = None,
                system_version: Optional[str] = None) -> VersionedCoreNode:
        """
        Get a core node by ID and version.
        
        Args:
            node_id: The ID of the node
            version: Specific node version to get (optional)
            system_version: System version to check against (defaults to current)
            
        Returns:
            The versioned core node
        """
        system_version = system_version or version_manager.current_version
        
        if node_id not in self.nodes:
            raise ValueError(f"Core node {node_id} not found")
        
        # If specific version requested, return it if available
        if version:
            if version not in self.nodes[node_id]:
                raise ValueError(f"Version {version} of core node {node_id} not found")
            
            node = self.nodes[node_id][version]
            if not node.is_available(system_version):
                raise ValueError(
                    f"Version {version} of core node {node_id} is not available in system version {system_version}"
                )
            
            return node
        
        # Find the latest version available in the given system version
        available_versions = []
        for node_version, node in self.nodes[node_id].items():
            if node.is_available(system_version):
                available_versions.append((node_version, node))
        
        if not available_versions:
            raise ValueError(
                f"No version of core node {node_id} is available in system version {system_version}"
            )
        
        # Return the latest available version
        import semver
        latest_version, latest_node = max(
            available_versions,
            key=lambda item: semver.VersionInfo.parse(item[0])
        )
        
        return latest_node
    
    def list_nodes(self, 
                  category: Optional[str] = None,
                  system_version: Optional[str] = None) -> List[VersionedCoreNode]:
        """
        List all core nodes available in the given system version.
        
        Args:
            category: Filter by category (optional)
            system_version: System version to check against (defaults to current)
            
        Returns:
            List of available core nodes
        """
        system_version = system_version or version_manager.current_version
        result = []
        
        for node_id, versions in self.nodes.items():
            # Get the latest available version for each node
            try:
                node = self.get_node(node_id, system_version=system_version)
                if category is None or node.category == category:
                    result.append(node)
            except ValueError:
                # Skip nodes not available in this version
                continue
        
        return result
    
    def list_categories(self, system_version: Optional[str] = None) -> List[str]:
        """
        List all node categories available in the given system version.
        
        Args:
            system_version: System version to check against (defaults to current)
            
        Returns:
            List of available categories
        """
        system_version = system_version or version_manager.current_version
        
        # Get all nodes available in this version
        nodes = self.list_nodes(system_version=system_version)
        
        # Extract unique categories
        return list(set(node.category for node in nodes))
    
    def discover_nodes(self, base_path: str = "backend/core_nodes"):
        """
        Discover and register core nodes from the filesystem.
        
        This method scans the core_nodes directory for node implementations
        and registers them with version information.
        
        Args:
            base_path: Base path to scan for core nodes
        """
        # Normalize path
        base_path = os.path.normpath(base_path)
        
        # Walk through the directory structure
        for root, dirs, files in os.walk(base_path):
            # Skip __pycache__ directories
            if "__pycache__" in root:
                continue
            
            # Check if this is a version directory
            version_match = os.path.basename(root).startswith("v")
            if version_match and "node_info.py" in files:
                # Extract version from directory name
                version_dir = os.path.basename(root)
                version = version_dir[1:].replace("_", ".")
                
                # Import the node_info module
                relative_path = os.path.relpath(root, os.path.dirname(base_path))
                module_path = f"backend.core_nodes.{relative_path.replace(os.path.sep, '.')}.node_info"
                
                try:
                    module = importlib.import_module(module_path)
                    
                    # Look for NODE_INFO dictionary
                    if hasattr(module, "NODE_INFO"):
                        for node_id, info in module.NODE_INFO.items():
                            # Create and register the node
                            node = VersionedCoreNode(
                                id=node_id,
                                name=info.get("name", node_id),
                                version=version,
                                introduced_in=info.get("introduced_in", version),
                                deprecated_in=info.get("deprecated_in"),
                                removed_in=info.get("removed_in"),
                                category=info.get("category", "Uncategorized"),
                                description=info.get("description", ""),
                                inputs=info.get("inputs", {}),
                                outputs=info.get("outputs", {}),
                                config_schema=info.get("config_schema", {})
                            )
                            
                            # Try to get the implementation
                            if hasattr(module, "get_implementation"):
                                try:
                                    node.implementation = module.get_implementation(node_id)
                                except Exception as e:
                                    logger.error(f"Error getting implementation for {node_id}: {e}")
                            
                            self.register_node(node)
                except Exception as e:
                    logger.error(f"Error importing {module_path}: {e}")


class VersionedTypeRegistry:
    """
    Registry for versioned types.
    
    This registry manages different versions of types and provides
    version-aware access to them.
    """
    
    def __init__(self):
        self.types: Dict[str, Dict[str, VersionedType]] = {}
    
    def register_type(self, type_def: VersionedType):
        """Register a type with version information."""
        if type_def.id not in self.types:
            self.types[type_def.id] = {}
        
        self.types[type_def.id][type_def.version] = type_def
        logger.info(f"Registered type {type_def.id} version {type_def.version}")
    
    def get_type(self, 
                type_id: str, 
                version: Optional[str] = None,
                system_version: Optional[str] = None) -> VersionedType:
        """
        Get a type by ID and version.
        
        Args:
            type_id: The ID of the type
            version: Specific type version to get (optional)
            system_version: System version to check against (defaults to current)
            
        Returns:
            The versioned type
        """
        system_version = system_version or version_manager.current_version
        
        if type_id not in self.types:
            raise ValueError(f"Type {type_id} not found")
        
        # If specific version requested, return it if available
        if version:
            if version not in self.types[type_id]:
                raise ValueError(f"Version {version} of type {type_id} not found")
            
            type_def = self.types[type_id][version]
            if not type_def.is_available(system_version):
                raise ValueError(
                    f"Version {version} of type {type_id} is not available in system version {system_version}"
                )
            
            return type_def
        
        # Find the latest version available in the given system version
        available_versions = []
        for type_version, type_def in self.types[type_id].items():
            if type_def.is_available(system_version):
                available_versions.append((type_version, type_def))
        
        if not available_versions:
            raise ValueError(
                f"No version of type {type_id} is available in system version {system_version}"
            )
        
        # Return the latest available version
        import semver
        latest_version, latest_type = max(
            available_versions,
            key=lambda item: semver.VersionInfo.parse(item[0])
        )
        
        return latest_type
    
    def list_types(self, system_version: Optional[str] = None) -> List[VersionedType]:
        """
        List all types available in the given system version.
        
        Args:
            system_version: System version to check against (defaults to current)
            
        Returns:
            List of available types
        """
        system_version = system_version or version_manager.current_version
        result = []
        
        for type_id, versions in self.types.items():
            # Get the latest available version for each type
            try:
                type_def = self.get_type(type_id, system_version=system_version)
                result.append(type_def)
            except ValueError:
                # Skip types not available in this version
                continue
        
        return result
    
    def discover_types(self, base_path: str = "backend/app/types"):
        """
        Discover and register types from the filesystem.
        
        This method scans the types directory for type definitions
        and registers them with version information.
        
        Args:
            base_path: Base path to scan for types
        """
        # Normalize path
        base_path = os.path.normpath(base_path)
        
        # Walk through the directory structure
        for root, dirs, files in os.walk(base_path):
            # Skip __pycache__ directories
            if "__pycache__" in root:
                continue
            
            # Check if this is a version directory
            version_match = os.path.basename(root).startswith("v")
            if version_match and "type_defs.py" in files:
                # Extract version from directory name
                version_dir = os.path.basename(root)
                version = version_dir[1:].replace("_", ".")
                
                # Import the type_defs module
                relative_path = os.path.relpath(root, os.path.dirname(base_path))
                module_path = f"backend.app.types.{relative_path.replace(os.path.sep, '.')}.type_defs"
                
                try:
                    module = importlib.import_module(module_path)
                    
                    # Look for TYPE_DEFS dictionary
                    if hasattr(module, "TYPE_DEFS"):
                        for type_id, info in module.TYPE_DEFS.items():
                            # Create and register the type
                            type_def = VersionedType(
                                id=type_id,
                                name=info.get("name", type_id),
                                version=version,
                                introduced_in=info.get("introduced_in", version),
                                deprecated_in=info.get("deprecated_in"),
                                removed_in=info.get("removed_in"),
                                base_type=info.get("base_type"),
                                validators=info.get("validators", []),
                                converters=info.get("converters", {})
                            )
                            
                            self.register_type(type_def)
                except Exception as e:
                    logger.error(f"Error importing {module_path}: {e}")


# Create singleton instances
core_node_registry = VersionedCoreNodeRegistry()
type_registry = VersionedTypeRegistry()
