"""
Versioning Integration Module

This module provides utilities for integrating the versioning system
with the existing backend.
"""

import logging
import importlib
from typing import Any, Dict, List, Optional, Type

from fastapi import FastAPI

from .version_manager import version_manager, VersionedFeature
from .middleware import VersionHeaderMiddleware
from .api import include_router as include_version_api

logger = logging.getLogger(__name__)

def integrate_with_existing_app(app: FastAPI):
    """
    Integrate the versioning system with an existing FastAPI application.
    
    Args:
        app: The existing FastAPI application
    """
    logger.info("Integrating versioning system with existing application")
    
    # Add version header middleware
    app.add_middleware(
        VersionHeaderMiddleware,
        default_version=version_manager.current_version
    )
    
    # Include version API
    include_version_api(app)
    
    # Set up version-aware routes
    _setup_version_aware_routes(app)
    
    logger.info("Versioning system integrated successfully")

def _setup_version_aware_routes(app: FastAPI):
    """
    Set up version-aware routes for the existing application.
    
    This function adds version information to the OpenAPI schema
    and ensures that all routes are properly versioned.
    
    Args:
        app: The existing FastAPI application
    """
    # Add version information to OpenAPI schema
    if app.openapi_schema:
        openapi_schema = app.openapi_schema
    else:
        openapi_schema = app.openapi()
    
    # Add version information to info section
    if "info" in openapi_schema:
        info = openapi_schema["info"]
        info["x-versions"] = version_manager.list_available_versions()
        info["x-current-version"] = version_manager.current_version
    
    # Update OpenAPI schema
    app.openapi_schema = openapi_schema

def get_versioned_component(
    feature: VersionedFeature,
    component_name: str,
    version: Optional[str] = None
) -> Any:
    """
    Get a versioned component from the existing backend.
    
    This function attempts to import a component from the appropriate
    version directory. If the component is not found, it falls back
    to the existing implementation.
    
    Args:
        feature: The feature area the component belongs to
        component_name: The name of the component to import
        version: The version to use (defaults to current)
        
    Returns:
        The imported component (class, function, or module)
    """
    version = version or version_manager.current_version
    feature_version = version_manager.get_feature_version(feature, version)
    
    # Try to import from versioned directory
    try:
        import_path = f"backend.app.{feature.value}.v{feature_version.replace('.', '_')}.{component_name}"
        return importlib.import_module(import_path)
    except ImportError:
        # Fall back to existing implementation
        try:
            import_path = f"backend.app.{feature.value}.{component_name}"
            return importlib.import_module(import_path)
        except ImportError:
            logger.warning(
                f"Could not import {component_name} from {feature.value} "
                f"(version {feature_version})"
            )
            return None

def register_existing_components():
    """
    Register existing components with the versioning system.
    
    This function scans the existing backend for components and
    registers them with the versioning system.
    """
    logger.info("Registering existing components with versioning system")
    
    # Register existing core nodes
    _register_existing_core_nodes()
    
    # Register existing types
    _register_existing_types()
    
    logger.info("Existing components registered successfully")

def _register_existing_core_nodes():
    """Register existing core nodes with the versioning system."""
    from backend.app.services.core_node_registry import CoreNodeRegistry
    from .registry import core_node_registry, VersionedCoreNode
    
    # Get existing core nodes
    existing_registry = CoreNodeRegistry()
    existing_registry.initialize()
    existing_nodes = existing_registry.get_all_nodes()
    
    logger.info(f"Found {len(existing_nodes)} existing core nodes")
    
    # Register each node with the versioning system
    for node_id, node_info in existing_nodes.items():
        # Create a versioned core node
        versioned_node = VersionedCoreNode(
            id=node_id,
            name=node_info.get("name", node_id),
            version="0.1.0",
            introduced_in="0.1.0",
            category=node_info.get("category", "Uncategorized"),
            description=node_info.get("description", ""),
            inputs=node_info.get("inputs", {}),
            outputs=node_info.get("outputs", {}),
            config_schema=node_info.get("config_schema", {})
        )
        
        # Register the node
        core_node_registry.register_node(versioned_node)
    
    logger.info(f"Registered {len(existing_nodes)} existing core nodes")

def _register_existing_types():
    """Register existing types with the versioning system."""
    from backend.app.services.type_registry import TypeRegistry
    from .registry import type_registry, VersionedType
    
    # Get existing types
    existing_registry = TypeRegistry()
    existing_registry.initialize()
    existing_types = existing_registry.get_all_types()
    
    logger.info(f"Found {len(existing_types)} existing types")
    
    # Register each type with the versioning system
    for type_id, type_info in existing_types.items():
        # Create a versioned type
        versioned_type = VersionedType(
            id=type_id,
            name=type_info.get("name", type_id),
            version="0.1.0",
            introduced_in="0.1.0",
            base_type=type_info.get("base_type"),
            validators=[],
            converters={}
        )
        
        # Register the type
        type_registry.register_type(versioned_type)
    
    logger.info(f"Registered {len(existing_types)} existing types")
