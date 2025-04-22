"""
Node Types Routes

This module provides FastAPI routes for node types.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.models.responses import StandardResponse
from backend.app.controllers.node_types_controller import NodeTypesController
from backend.app.services.node_registry import NodeRegistry

# Create router
router = APIRouter(prefix="/api/node-types", tags=["node-types"])

# Dependency for NodeTypesController
def get_node_types_controller():
    """Get NodeTypesController instance."""
    registry = NodeRegistry()
    return NodeTypesController(registry)

@router.get("/", response_model=StandardResponse)
async def get_node_types(
    controller: NodeTypesController = Depends(get_node_types_controller)
) -> StandardResponse:
    """
    Get all node types.

    Returns:
        All node types
    """
    node_types = controller.get_node_types()
    return StandardResponse.success(data=node_types)

@router.get("/core-nodes", response_model=StandardResponse)
async def get_core_nodes(
    controller: NodeTypesController = Depends(get_node_types_controller)
) -> StandardResponse:
    """
    Get all core nodes.

    Returns:
        List of all core nodes
    """
    core_nodes = controller.get_core_nodes()
    return StandardResponse.success(data=core_nodes)

@router.get("/core-nodes/directories", response_model=StandardResponse)
async def get_core_nodes_by_directory(
    controller: NodeTypesController = Depends(get_node_types_controller)
) -> StandardResponse:
    """
    Get all core nodes organized by directory.

    Returns:
        Dictionary mapping directory names to lists of core nodes
    """
    nodes_by_directory = controller.get_core_nodes_by_directory()
    return StandardResponse.success(data=nodes_by_directory)

@router.get("/plugins", response_model=StandardResponse)
async def get_plugins(
    controller: NodeTypesController = Depends(get_node_types_controller)
) -> StandardResponse:
    """
    Get all plugins.

    Returns:
        List of all plugins
    """
    plugins = controller.get_plugins()
    return StandardResponse.success(data=plugins)

@router.get("/{node_id}", response_model=StandardResponse)
async def get_node_type(
    node_id: str,
    controller: NodeTypesController = Depends(get_node_types_controller)
) -> StandardResponse:
    """
    Get a node type by ID.

    Args:
        node_id: The ID of the node type

    Returns:
        Node type metadata
    """
    node_type = controller.get_node_type(node_id)
    if not node_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node type not found: {node_id}"
        )
    return StandardResponse.success(data=node_type)
