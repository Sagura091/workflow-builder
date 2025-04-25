"""
Standalone Plugins Router

This module provides API routes for standalone plugins.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from backend.app.controllers.standalone_plugin_controller import StandalonePluginController
from backend.app.services.plugin_loader import PluginLoader
from backend.app.dependencies import get_plugin_loader
from backend.app.models.responses import StandardResponse

# Create router
router = APIRouter(prefix="/standalone-plugins", tags=["standalone-plugins"])

# Models
class PluginExecutionRequest(BaseModel):
    """Request model for executing a standalone plugin."""
    inputs: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    execution_mode: str = "direct"

# Dependency for StandalonePluginController
def get_standalone_plugin_controller(
    plugin_loader: PluginLoader = Depends(get_plugin_loader)
):
    """Get StandalonePluginController instance."""
    return StandalonePluginController(plugin_loader)

@router.get("/", response_model=StandardResponse)
async def get_all_standalone_plugins(
    controller: StandalonePluginController = Depends(get_standalone_plugin_controller)
) -> StandardResponse:
    """
    Get all standalone plugins.
    
    Returns:
        StandardResponse: Response containing all standalone plugins
    """
    plugins = controller.get_all_standalone_plugins()
    return StandardResponse.success(data=plugins)

@router.get("/{plugin_id}", response_model=StandardResponse)
async def get_standalone_plugin(
    plugin_id: str,
    controller: StandalonePluginController = Depends(get_standalone_plugin_controller)
) -> StandardResponse:
    """
    Get a standalone plugin by ID.
    
    Args:
        plugin_id: ID of the plugin to get
        
    Returns:
        StandardResponse: Response containing the plugin metadata
    """
    plugin = controller.get_standalone_plugin(plugin_id)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Standalone plugin '{plugin_id}' not found"
        )
    return StandardResponse.success(data=plugin)

@router.post("/{plugin_id}/execute", response_model=StandardResponse)
async def execute_standalone_plugin(
    plugin_id: str,
    request: PluginExecutionRequest,
    controller: StandalonePluginController = Depends(get_standalone_plugin_controller)
) -> StandardResponse:
    """
    Execute a standalone plugin.
    
    Args:
        plugin_id: ID of the plugin to execute
        request: Execution request
        
    Returns:
        StandardResponse: Response containing the execution result
    """
    try:
        result = controller.execute_standalone_plugin(
            plugin_id=plugin_id,
            inputs=request.inputs,
            config=request.config,
            execution_mode=request.execution_mode
        )
        return StandardResponse.success(
            data=result,
            message=f"Plugin '{plugin_id}' executed successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing plugin: {str(e)}"
        )
