"""
Type System Router

This module provides API endpoints for the type system.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional

from backend.app.models.responses import StandardResponse
from backend.app.controllers.type_system_controller import TypeSystemController
from backend.app.controllers.type_controller import TypeController
from backend.app.dependencies import get_type_registry
from backend.app.services.type_registry import TypeRegistry
from backend.app.exceptions import NotFoundError

# Create router with API versioning
router = APIRouter(prefix="/api/v1/type-system", tags=["Type System"])

# Dependency for TypeController
def get_type_controller(
    type_registry: TypeRegistry = Depends(get_type_registry)
):
    """Get TypeController instance."""
    return TypeController(type_registry)

@router.get("/", response_model=StandardResponse)
async def get_type_system(
    controller: TypeController = Depends(get_type_controller)
) -> StandardResponse:
    """
    Get the entire type system.
    
    Returns:
        StandardResponse: Response containing the type system
    """
    type_system = controller.get_type_system()
    return StandardResponse.success(data=type_system)

@router.get("/types", response_model=StandardResponse)
async def get_all_types(
    controller: TypeController = Depends(get_type_controller)
) -> StandardResponse:
    """
    Get all types.
    
    Returns:
        StandardResponse: Response containing all types
    """
    types = controller.get_all_types()
    return StandardResponse.success(data=types)

@router.get("/types/{type_name}", response_model=StandardResponse)
async def get_type(
    type_name: str,
    controller: TypeController = Depends(get_type_controller)
) -> StandardResponse:
    """
    Get a specific type by name.
    
    Args:
        type_name: The name of the type to get
        
    Returns:
        StandardResponse: Response containing the specified type
    """
    try:
        type_def = controller.get_type(type_name)
        if type_def is None:
            raise NotFoundError(f"Type '{type_name}' not found")
        return StandardResponse.success(data=type_def)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/rules", response_model=StandardResponse)
async def get_all_rules(
    controller: TypeController = Depends(get_type_controller)
) -> StandardResponse:
    """
    Get all type compatibility rules.
    
    Returns:
        StandardResponse: Response containing all type compatibility rules
    """
    rules = controller.get_all_rules()
    return StandardResponse.success(data=rules)

@router.get("/compatibility", response_model=StandardResponse)
async def check_type_compatibility(
    source_type: str,
    target_type: str,
    controller: TypeController = Depends(get_type_controller)
) -> StandardResponse:
    """
    Check if two types are compatible.
    
    Args:
        source_type: The source type
        target_type: The target type
        
    Returns:
        StandardResponse: Response indicating whether the types are compatible
    """
    compatibility = controller.check_compatibility(source_type, target_type)
    return StandardResponse.success(data=compatibility)

@router.get("/hierarchy", response_model=StandardResponse)
async def get_type_hierarchy(
    controller: TypeController = Depends(get_type_controller)
) -> StandardResponse:
    """
    Get the type hierarchy.
    
    Returns:
        StandardResponse: Response containing the type hierarchy
    """
    hierarchy = controller.get_type_hierarchy()
    return StandardResponse.success(data=hierarchy)

@router.get("/hierarchy/{type_name}", response_model=StandardResponse)
async def get_type_hierarchy_for_type(
    type_name: str,
    controller: TypeController = Depends(get_type_controller)
) -> StandardResponse:
    """
    Get the type hierarchy for a specific type.
    
    Args:
        type_name: The name of the type to get the hierarchy for
        
    Returns:
        StandardResponse: Response containing the type hierarchy for the specified type
    """
    try:
        hierarchy = controller.get_type_hierarchy_for_type(type_name)
        return StandardResponse.success(data=hierarchy)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
