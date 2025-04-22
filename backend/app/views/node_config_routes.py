"""
Node Configuration Routes

This module provides API routes for accessing node configurations.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List

from backend.app.models.plugin_metadata import PluginMetadata

from backend.app.services.core_node_registry import CoreNodeRegistry
from backend.app.services.plugin_manager import PluginManager
from backend.app.dependencies import get_core_node_registry, get_plugin_manager
from backend.app.models.responses import StandardResponse

# Create router
router = APIRouter(prefix="/api/node-configs", tags=["node-configs"])

# Also create a router with the old path for backward compatibility
legacy_router = APIRouter(tags=["node-configs"])

def convert_plugin_config_fields(metadata: PluginMetadata) -> List[Dict[str, Any]]:
    """Convert plugin config fields to a dictionary format."""
    try:
        if not hasattr(metadata, 'config_fields'):
            return []

        return [
            {
                "id": field.id,
                "name": field.name,
                "type": field.type,
                "description": field.description,
                "required": field.required,
                "default_value": field.default_value,
                "options": field.options,
                "validation": field.validation,
                "ui_properties": field.ui_properties
            }
            for field in metadata.config_fields
        ]
    except Exception as e:
        print(f"Error converting plugin config fields: {str(e)}")
        return []

@router.get("", response_model=StandardResponse)
@legacy_router.get("/node-configs", response_model=StandardResponse)
async def get_all_node_configs(
    core_node_registry: CoreNodeRegistry = Depends(get_core_node_registry),
    plugin_manager: PluginManager = Depends(get_plugin_manager)
) -> StandardResponse:
    """
    Get configuration schemas for all nodes (core nodes and plugins).

    Returns:
        A dictionary with node IDs as keys and their configuration schemas as values
    """
    result = {}

    # Get core node configurations
    for node_id in core_node_registry.get_all_nodes():
        metadata = core_node_registry.get_node_metadata(node_id)
        if metadata:
            # Core node metadata might be a dictionary or a PluginMetadata object
            try:
                # Try to access as dictionary
                if hasattr(metadata, 'get'):
                    config_fields = metadata.get("config_fields", [])
                    category = metadata.get("category", "UNKNOWN").upper()
                else:
                    # Try to access as object
                    config_fields = getattr(metadata, "config_fields", [])
                    category = getattr(metadata, "category", "UNKNOWN")
                    if hasattr(category, 'value'):
                        category = category.value.upper()
                    else:
                        category = str(category).upper()

                result[node_id] = {
                    "config_fields": config_fields,
                    "is_core": True,
                    "category": category
                }
            except Exception as e:
                print(f"Error processing core node {node_id}: {str(e)}")
                result[node_id] = {
                    "config_fields": [],
                    "is_core": True,
                    "category": "UNKNOWN"
                }

    # Get plugin configurations
    for plugin_id, metadata in plugin_manager.get_all_plugin_metadata().items():
        # Plugin metadata is a PluginMetadata object
        config_fields = convert_plugin_config_fields(metadata)

        category = "UNKNOWN"
        if hasattr(metadata, 'category') and metadata.category:
            category = metadata.category.value

        result[plugin_id] = {
            "config_fields": config_fields,
            "is_core": False,
            "category": category
        }

    return StandardResponse.success(
        data=result,
        message="Node configurations retrieved successfully"
    )

@router.get("/{node_id}", response_model=StandardResponse)
@legacy_router.get("/node-configs/{node_id}", response_model=StandardResponse)
async def get_node_config(
    node_id: str,
    core_node_registry: CoreNodeRegistry = Depends(get_core_node_registry),
    plugin_manager: PluginManager = Depends(get_plugin_manager)
) -> StandardResponse:
    """
    Get configuration schema for a specific node.

    Args:
        node_id: The ID of the node

    Returns:
        The node's configuration schema
    """
    # Check if it's a core node
    metadata = core_node_registry.get_node_metadata(node_id)
    if metadata:
        # Core node metadata might be a dictionary or a PluginMetadata object
        try:
            # Try to access as dictionary
            if hasattr(metadata, 'get'):
                config_fields = metadata.get("config_fields", [])
                category = metadata.get("category", "UNKNOWN").upper()
            else:
                # Try to access as object
                config_fields = getattr(metadata, "config_fields", [])
                category = getattr(metadata, "category", "UNKNOWN")
                if hasattr(category, 'value'):
                    category = category.value.upper()
                else:
                    category = str(category).upper()

            return StandardResponse.success(
                data={
                    "config_fields": config_fields,
                    "is_core": True,
                    "category": category
                },
                message=f"Configuration for core node '{node_id}' retrieved successfully"
            )
        except Exception as e:
            print(f"Error processing core node {node_id}: {str(e)}")
            return StandardResponse.success(
                data={
                    "config_fields": [],
                    "is_core": True,
                    "category": "UNKNOWN"
                },
                message=f"Configuration for core node '{node_id}' retrieved successfully (with errors)"
            )

    # Check if it's a plugin
    metadata = plugin_manager.get_plugin_metadata(node_id)
    if metadata:
        # Plugin metadata is a PluginMetadata object
        config_fields = convert_plugin_config_fields(metadata)

        category = "UNKNOWN"
        if hasattr(metadata, 'category') and metadata.category:
            category = metadata.category.value

        return StandardResponse.success(
            data={
                "config_fields": config_fields,
                "is_core": False,
                "category": category
            },
            message=f"Configuration for plugin '{node_id}' retrieved successfully"
        )

    # Node not found
    raise HTTPException(
        status_code=404,
        detail=f"Node '{node_id}' not found"
    )
