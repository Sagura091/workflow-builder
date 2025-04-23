"""
Core Nodes Router

This module provides API endpoints for core nodes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Dict, List, Any, Optional

from backend.app.models.responses import StandardResponse
from backend.app.controllers.core_node_controller import CoreNodeController
from backend.app.services.core_node_registry import CoreNodeRegistry
from backend.app.exceptions import NotFoundError

# Create router with API versioning
router = APIRouter(prefix="/api/v1/core-nodes", tags=["Core Nodes"])

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
        StandardResponse: Response containing all core nodes
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
        StandardResponse: Response containing core nodes organized by directory
    """
    nodes_by_directory = controller.get_nodes_by_directory()
    return StandardResponse.success(data=nodes_by_directory)

@router.get("/categories", response_model=StandardResponse)
async def get_node_categories(
    controller: CoreNodeController = Depends(get_core_node_controller)
) -> StandardResponse:
    """
    Get all node categories.
    
    Returns:
        StandardResponse: Response containing all node categories
    """
    directories = controller.get_nodes_by_directory()
    return StandardResponse.success(data=list(directories.keys()))

@router.get("/categories/{category}", response_model=StandardResponse)
async def get_nodes_by_category(
    category: str,
    full_metadata: bool = Query(False, description="Whether to include full metadata"),
    controller: CoreNodeController = Depends(get_core_node_controller)
) -> StandardResponse:
    """
    Get all nodes in a category.
    
    Args:
        category: The category to get nodes for
        full_metadata: Whether to include full metadata
        
    Returns:
        StandardResponse: Response containing nodes in the specified category
    """
    try:
        nodes = controller.get_nodes_by_category(category, full_metadata)
        return StandardResponse.success(data=nodes)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{node_id}", response_model=StandardResponse)
async def get_core_node(
    node_id: str,
    controller: CoreNodeController = Depends(get_core_node_controller)
) -> StandardResponse:
    """
    Get a specific core node by ID.
    
    Args:
        node_id: The ID of the node to get
        
    Returns:
        StandardResponse: Response containing the specified node
    """
    try:
        node = controller.get_node(node_id)
        return StandardResponse.success(data=node)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
