"""
Core Node Routes

This module provides FastAPI routes for core nodes.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.models.responses import StandardResponse
from backend.app.controllers.core_node_controller import CoreNodeController
from backend.app.services.core_node_registry import CoreNodeRegistry
from backend.app.exceptions import NotFoundError

# Create router
router = APIRouter(prefix="/api/core-nodes", tags=["core-nodes"])

# Dependency for CoreNodeController
def get_core_node_controller():
    """Get CoreNodeController instance."""
    registry = CoreNodeRegistry()
    if not registry.initialized:
        registry.initialize()
    return CoreNodeController(registry)

@router.get("/", response_model=StandardResponse)
async def get_all_core_nodes(
    controller: CoreNodeController = Depends(get_core_node_controller)
) -> StandardResponse:
    """
    Get all core nodes.
    
    Returns:
        List of all core nodes
    """
    nodes = controller.get_all_nodes()
    return StandardResponse.success(data=nodes)

@router.get("/directories", response_model=StandardResponse)
async def get_core_nodes_by_directory(
    controller: CoreNodeController = Depends(get_core_node_controller)
) -> StandardResponse:
    """
    Get all core nodes organized by directory.
    
    Returns:
        Dictionary mapping directory names to lists of core nodes
    """
    nodes_by_directory = controller.get_nodes_by_directory()
    return StandardResponse.success(data=nodes_by_directory)

@router.get("/categories/{category}", response_model=StandardResponse)
async def get_core_nodes_by_category(
    category: str,
    controller: CoreNodeController = Depends(get_core_node_controller)
) -> StandardResponse:
    """
    Get all core nodes in a category.
    
    Args:
        category: The category name
        
    Returns:
        List of core nodes in the category
    """
    nodes = controller.get_nodes_by_category(category)
    return StandardResponse.success(data=nodes)

@router.get("/{node_id}", response_model=StandardResponse)
async def get_core_node(
    node_id: str,
    controller: CoreNodeController = Depends(get_core_node_controller)
) -> StandardResponse:
    """
    Get a core node by ID.
    
    Args:
        node_id: The ID of the node
        
    Returns:
        Node metadata
    """
    try:
        node = controller.get_node(node_id)
        return StandardResponse.success(data=node)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
