"""
Node Configuration Router

This module provides API endpoints for node configurations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional

from backend.app.models.responses import StandardResponse
from backend.app.controllers.node_config_controller import NodeConfigController
from backend.app.services.core_node_registry import CoreNodeRegistry
from backend.app.services.plugin_manager import PluginManager
from backend.app.dependencies import get_core_node_registry, get_plugin_manager
from backend.app.exceptions import NotFoundError

# Create router with API versioning
router = APIRouter(prefix="/api/v1/node-config", tags=["Node Configuration"])

# Dependency for NodeConfigController
def get_node_config_controller(
    core_node_registry: CoreNodeRegistry = Depends(get_core_node_registry),
    plugin_manager: PluginManager = Depends(get_plugin_manager)
):
    """Get NodeConfigController instance."""
    return NodeConfigController(core_node_registry, plugin_manager)

@router.get("/", response_model=StandardResponse)
async def get_all_node_configs(
    controller: NodeConfigController = Depends(get_node_config_controller)
) -> StandardResponse:
    """
    Get all node configurations.
    
    Returns:
        StandardResponse: Response containing all node configurations
    """
    configs = controller.get_all_node_configs()
    return StandardResponse.success(data=configs)

@router.get("/core-nodes", response_model=StandardResponse)
async def get_core_node_configs(
    controller: NodeConfigController = Depends(get_node_config_controller)
) -> StandardResponse:
    """
    Get configurations for all core nodes.
    
    Returns:
        StandardResponse: Response containing configurations for all core nodes
    """
    configs = controller.get_core_node_configs()
    return StandardResponse.success(data=configs)

@router.get("/plugins", response_model=StandardResponse)
async def get_plugin_configs(
    controller: NodeConfigController = Depends(get_node_config_controller)
) -> StandardResponse:
    """
    Get configurations for all plugins.
    
    Returns:
        StandardResponse: Response containing configurations for all plugins
    """
    configs = controller.get_plugin_configs()
    return StandardResponse.success(data=configs)

@router.get("/core-nodes/{node_id}", response_model=StandardResponse)
async def get_core_node_config(
    node_id: str,
    controller: NodeConfigController = Depends(get_node_config_controller)
) -> StandardResponse:
    """
    Get configuration for a specific core node.
    
    Args:
        node_id: The ID of the core node
        
    Returns:
        StandardResponse: Response containing the configuration for the specified core node
    """
    try:
        config = controller.get_core_node_config(node_id)
        return StandardResponse.success(data=config)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/plugins/{plugin_id}", response_model=StandardResponse)
async def get_plugin_config(
    plugin_id: str,
    controller: NodeConfigController = Depends(get_node_config_controller)
) -> StandardResponse:
    """
    Get configuration for a specific plugin.
    
    Args:
        plugin_id: The ID of the plugin
        
    Returns:
        StandardResponse: Response containing the configuration for the specified plugin
    """
    try:
        config = controller.get_plugin_config(plugin_id)
        return StandardResponse.success(data=config)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
