"""
Plugins Router

This module provides API endpoints for plugins.
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from typing import Dict, List, Any, Optional

from backend.app.models.responses import StandardResponse
from backend.app.controllers.plugin_controller import PluginController
from backend.app.services.plugin_manager import PluginManager
from backend.app.dependencies import get_plugin_manager
from backend.app.exceptions import NotFoundError, PluginLoadError

# Create router with API versioning
router = APIRouter(prefix="/api/v1/plugins", tags=["Plugins"])

# Dependency for PluginController
def get_plugin_controller(
    plugin_manager: PluginManager = Depends(get_plugin_manager)
):
    """Get PluginController instance."""
    return PluginController(plugin_manager)

@router.get("/", response_model=StandardResponse)
async def get_all_plugins(
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Get all plugins.
    
    Returns:
        StandardResponse: Response containing all plugins
    """
    plugins = controller.get_all_plugins()
    return StandardResponse.success(data=plugins)

@router.get("/categories", response_model=StandardResponse)
async def get_plugin_categories(
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Get all plugin categories.
    
    Returns:
        StandardResponse: Response containing all plugin categories
    """
    categories = controller.get_plugin_categories()
    return StandardResponse.success(data=categories)

@router.get("/categories/{category}", response_model=StandardResponse)
async def get_plugins_by_category(
    category: str,
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Get all plugins in a category.
    
    Args:
        category: The category to get plugins for
        
    Returns:
        StandardResponse: Response containing plugins in the specified category
    """
    try:
        plugins = controller.get_plugins_by_category(category)
        return StandardResponse.success(data=plugins)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{plugin_id}", response_model=StandardResponse)
async def get_plugin(
    plugin_id: str,
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Get a specific plugin by ID.
    
    Args:
        plugin_id: The ID of the plugin to get
        
    Returns:
        StandardResponse: Response containing the specified plugin
    """
    try:
        plugin = controller.get_plugin(plugin_id)
        return StandardResponse.success(data=plugin)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/", response_model=StandardResponse)
async def create_plugin(
    plugin_code: str = Form(...),
    plugin_name: str = Form(...),
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Create a new plugin.
    
    Args:
        plugin_code: The code for the plugin
        plugin_name: The name of the plugin
        
    Returns:
        StandardResponse: Response containing the created plugin
    """
    try:
        plugin = controller.create_plugin(plugin_name, plugin_code)
        return StandardResponse.success(
            message=f"Plugin {plugin_name} created successfully",
            data=plugin
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{plugin_id}", response_model=StandardResponse)
async def update_plugin(
    plugin_id: str,
    plugin_code: str = Form(...),
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Update a plugin.
    
    Args:
        plugin_id: The ID of the plugin to update
        plugin_code: The new code for the plugin
        
    Returns:
        StandardResponse: Response containing the updated plugin
    """
    try:
        plugin = controller.update_plugin(plugin_id, plugin_code)
        return StandardResponse.success(
            message=f"Plugin {plugin_id} updated successfully",
            data=plugin
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{plugin_id}", response_model=StandardResponse)
async def delete_plugin(
    plugin_id: str,
    controller: PluginController = Depends(get_plugin_controller)
) -> StandardResponse:
    """
    Delete a plugin.
    
    Args:
        plugin_id: The ID of the plugin to delete
        
    Returns:
        StandardResponse: Response indicating success or failure
    """
    try:
        success = controller.delete_plugin(plugin_id)
        if success:
            return StandardResponse.success(message=f"Plugin {plugin_id} deleted successfully")
        else:
            return StandardResponse.error(message=f"Failed to delete plugin {plugin_id}")
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
