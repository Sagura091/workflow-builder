"""
Type System Routes

This module provides FastAPI routes for the type system.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.models.responses import StandardResponse
from backend.app.controllers.type_system_controller import TypeSystemController
from backend.app.controllers.type_controller import TypeController
from backend.app.dependencies import get_type_controller

# Create router
router = APIRouter(prefix="/api/type-system", tags=["type-system"])

# Also create a router with the old path for backward compatibility
legacy_router = APIRouter(tags=["type-system"])

# Dependency for TypeSystemController
def get_type_system_controller():
    """Get TypeSystemController instance."""
    return TypeSystemController()

@router.get("/", response_model=StandardResponse)
@legacy_router.get("/type-system", response_model=StandardResponse)
async def get_type_system(
    controller: TypeSystemController = Depends(get_type_system_controller)
) -> StandardResponse:
    """
    Get the type system.

    Returns:
        The type system
    """
    try:
        type_system = controller.get_type_system()
        return StandardResponse.success(data=type_system)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/types/{type_name}", response_model=StandardResponse)
@legacy_router.get("/type-system/types/{type_name}", response_model=StandardResponse)
async def get_type(
    type_name: str,
    controller: TypeController = Depends(get_type_controller)
) -> StandardResponse:
    """
    Get a specific type definition.

    Args:
        type_name: The name of the type

    Returns:
        Type definition
    """
    type_def = controller.get_type(type_name)
    if not type_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Type '{type_name}' not found"
        )
    return StandardResponse.success(data=type_def)

@router.get("/compatibility", response_model=StandardResponse)
@legacy_router.get("/type-system/compatibility", response_model=StandardResponse)
async def check_type_compatibility(
    source: str,
    target: str,
    controller: TypeController = Depends(get_type_controller)
) -> StandardResponse:
    """
    Check if two types are compatible.

    Args:
        source: The source type
        target: The target type

    Returns:
        Compatibility result
    """
    try:
        result = controller.check_compatibility(source, target)
        return StandardResponse.success(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/compatible-types/{type_name}", response_model=StandardResponse)
@legacy_router.get("/type-system/compatible-types/{type_name}", response_model=StandardResponse)
async def get_compatible_types(
    type_name: str,
    as_source: Optional[bool] = True,
    controller: TypeController = Depends(get_type_controller)
) -> StandardResponse:
    """
    Get all types compatible with the given type.

    Args:
        type_name: The type name
        as_source: Whether to check compatibility as source (True) or target (False)

    Returns:
        List of compatible types
    """
    compatible_types = controller.get_compatible_types(type_name, as_source)
    return StandardResponse.success(data=compatible_types)
