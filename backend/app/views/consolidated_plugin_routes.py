"""
Plugin Routes

This module provides FastAPI routes for plugins.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.app.models.responses import StandardResponse
from backend.app.controllers.plugin_controller import PluginController
from backend.app.dependencies import get_plugin_controller

# Create models
class PluginCode(BaseModel):
    """Request model for creating a plugin."""
    code: str

# Create router
router = APIRouter(prefix="/api/plugins", tags=["plugins"])

@router.get("/", response_model=StandardResponse)
async def get_all_plugins(
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Get all available plugins.
    
    Returns:
        List of all plugins
    """
    plugins = controller.get_all_plugins()
    return StandardResponse.success(data=plugins)

@router.get("/{plugin_id}", response_model=StandardResponse)
async def get_plugin(
    plugin_id: str,
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Get a specific plugin by ID.
    
    Args:
        plugin_id: The ID of the plugin
        
    Returns:
        Plugin metadata
    """
    plugin = controller.get_plugin(plugin_id)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found"
        )
    return StandardResponse.success(data=plugin)

@router.get("/{plugin_id}/ui-schema", response_model=StandardResponse)
async def get_plugin_ui_schema(
    plugin_id: str,
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Get UI schema for a specific plugin.
    
    Args:
        plugin_id: The ID of the plugin
        
    Returns:
        UI schema for the plugin
    """
    schema = controller.get_plugin_ui_schema(plugin_id)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_id}' not found"
        )
    return StandardResponse.success(data=schema)

@router.post("/{plugin_id}/validate-config", response_model=StandardResponse)
async def validate_plugin_config(
    plugin_id: str,
    config: Dict[str, Any],
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Validate plugin configuration.
    
    Args:
        plugin_id: The ID of the plugin
        config: The configuration to validate
        
    Returns:
        Validation results
    """
    results = controller.validate_plugin_config(plugin_id, config)
    return StandardResponse.success(data=results)

@router.post("/{plugin_id}", status_code=status.HTTP_201_CREATED, response_model=StandardResponse)
async def create_plugin(
    plugin_id: str,
    plugin: PluginCode,
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Create a new plugin.
    
    Args:
        plugin_id: The ID of the plugin
        plugin: The plugin code
        
    Returns:
        Created plugin metadata
    """
    result = controller.create_plugin(plugin_id, plugin.code)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create plugin"
        )
    return StandardResponse.success(
        data=result,
        message=f"Plugin '{plugin_id}' created successfully"
    )
