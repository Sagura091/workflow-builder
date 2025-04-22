"""
Type System Routes

This module provides FastAPI routes for the type system.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.models.responses import StandardResponse
from backend.app.controllers.type_system_controller import TypeSystemController

# Create router
router = APIRouter(prefix="/api/type-system", tags=["type-system"])

# Dependency for TypeSystemController
def get_type_system_controller():
    """Get TypeSystemController instance."""
    return TypeSystemController()

@router.get("/", response_model=StandardResponse)
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

@router.get("/compatibility", response_model=StandardResponse)
async def check_type_compatibility(
    source: str,
    target: str,
    controller: TypeSystemController = Depends(get_type_system_controller)
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
        result = controller.check_type_compatibility(source, target)
        return StandardResponse.success(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
