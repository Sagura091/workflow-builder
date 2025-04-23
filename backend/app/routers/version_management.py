"""
Version Management Router

This module provides API endpoints for managing component versions.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional

from backend.app.services.version_manager import VersionManager, ComponentType
from backend.app.services.versioned_core_node_registry import VersionedCoreNodeRegistry
from backend.app.dependencies import get_core_node_registry

router = APIRouter(
    prefix="/api/versions",
    tags=["Version Management"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_version_info():
    """Get version information for all components."""
    version_manager = VersionManager()
    
    return {
        "default_preferences": version_manager.default_preferences,
        "mappings": {
            ComponentType.CORE_NODE: version_manager.get_all_mappings(ComponentType.CORE_NODE),
            ComponentType.PLUGIN: version_manager.get_all_mappings(ComponentType.PLUGIN),
            ComponentType.SERVICE: version_manager.get_all_mappings(ComponentType.SERVICE),
            ComponentType.CONTROLLER: version_manager.get_all_mappings(ComponentType.CONTROLLER),
            ComponentType.MODEL: version_manager.get_all_mappings(ComponentType.MODEL)
        }
    }


@router.get("/core-nodes")
async def get_core_node_versions(
    core_node_registry: VersionedCoreNodeRegistry = Depends(get_core_node_registry)
):
    """Get version information for core nodes."""
    # Check if the registry is a versioned registry
    if not isinstance(core_node_registry, VersionedCoreNodeRegistry):
        raise HTTPException(status_code=400, detail="Versioned core node registry not enabled")
    
    # Get all node metadata
    all_metadata = core_node_registry.get_all_node_metadata()
    
    # Get all mappings
    version_manager = VersionManager()
    mappings = version_manager.get_all_mappings(ComponentType.CORE_NODE)
    
    # Get all preferences
    preferences = version_manager.get_all_preferences(ComponentType.CORE_NODE)
    default_preference = version_manager.get_default_preference(ComponentType.CORE_NODE)
    
    # Build result
    result = {
        "default_preference": default_preference,
        "nodes": {}
    }
    
    for node_id in all_metadata.keys():
        # Get available versions
        versions = core_node_registry.get_available_versions(node_id)
        
        # Get current preference
        preference = preferences.get(node_id, default_preference)
        
        # Add to result
        result["nodes"][node_id] = {
            "versions": versions,
            "preference": preference
        }
    
    return result


@router.post("/core-nodes/{node_id}/preference")
async def set_core_node_preference(
    node_id: str,
    preference: str,
    core_node_registry: VersionedCoreNodeRegistry = Depends(get_core_node_registry)
):
    """Set the preference for a core node."""
    # Check if the registry is a versioned registry
    if not isinstance(core_node_registry, VersionedCoreNodeRegistry):
        raise HTTPException(status_code=400, detail="Versioned core node registry not enabled")
    
    # Validate preference
    if preference not in ["legacy", "enhanced"]:
        raise HTTPException(status_code=400, detail="Invalid preference")
    
    # Check if the node exists
    versions = core_node_registry.get_available_versions(node_id)
    if not versions:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")
    
    # Set preference
    core_node_registry.set_node_preference(node_id, preference)
    
    return {"status": "success", "node_id": node_id, "preference": preference}


@router.post("/core-nodes/default-preference")
async def set_default_core_node_preference(
    preference: str,
    core_node_registry: VersionedCoreNodeRegistry = Depends(get_core_node_registry)
):
    """Set the default preference for core nodes."""
    # Check if the registry is a versioned registry
    if not isinstance(core_node_registry, VersionedCoreNodeRegistry):
        raise HTTPException(status_code=400, detail="Versioned core node registry not enabled")
    
    # Validate preference
    if preference not in ["legacy", "enhanced"]:
        raise HTTPException(status_code=400, detail="Invalid preference")
    
    # Set default preference
    core_node_registry.set_default_preference(preference)
    
    return {"status": "success", "preference": preference}


@router.get("/plugins")
async def get_plugin_versions():
    """Get version information for plugins."""
    version_manager = VersionManager()
    
    # Get all mappings
    mappings = version_manager.get_all_mappings(ComponentType.PLUGIN)
    
    # Get all preferences
    preferences = version_manager.get_all_preferences(ComponentType.PLUGIN)
    default_preference = version_manager.get_default_preference(ComponentType.PLUGIN)
    
    return {
        "default_preference": default_preference,
        "mappings": mappings,
        "preferences": preferences
    }


@router.post("/plugins/{plugin_id}/preference")
async def set_plugin_preference(plugin_id: str, preference: str):
    """Set the preference for a plugin."""
    version_manager = VersionManager()
    
    # Validate preference
    if preference not in ["legacy", "enhanced"]:
        raise HTTPException(status_code=400, detail="Invalid preference")
    
    # Set preference
    version_manager.set_preference(ComponentType.PLUGIN, plugin_id, preference)
    
    return {"status": "success", "plugin_id": plugin_id, "preference": preference}


@router.post("/plugins/default-preference")
async def set_default_plugin_preference(preference: str):
    """Set the default preference for plugins."""
    version_manager = VersionManager()
    
    # Validate preference
    if preference not in ["legacy", "enhanced"]:
        raise HTTPException(status_code=400, detail="Invalid preference")
    
    # Set default preference
    version_manager.set_default_preference(ComponentType.PLUGIN, preference)
    
    return {"status": "success", "preference": preference}
