from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional

from backend.app.controllers.type_controller import TypeController
from backend.app.dependencies import get_type_controller

router = APIRouter(prefix="/api/type-system", tags=["type-system"])

@router.get("/")
async def get_type_system(
    controller: TypeController = Depends(get_type_controller)
) -> Dict[str, Any]:
    """Get the entire type system."""
    return controller.get_type_system()

@router.get("/types/{type_name}")
async def get_type(
    type_name: str,
    controller: TypeController = Depends(get_type_controller)
) -> Dict[str, Any]:
    """Get a specific type definition."""
    type_def = controller.get_type(type_name)
    if not type_def:
        raise HTTPException(status_code=404, detail=f"Type '{type_name}' not found")
    return type_def

@router.get("/check-compatibility")
async def check_compatibility(
    source_type: str,
    target_type: str,
    controller: TypeController = Depends(get_type_controller)
) -> Dict[str, Any]:
    """Check if two types are compatible."""
    return controller.check_compatibility(source_type, target_type)

@router.get("/compatible-types/{type_name}")
async def get_compatible_types(
    type_name: str,
    as_source: Optional[bool] = True,
    controller: TypeController = Depends(get_type_controller)
) -> List[str]:
    """Get all types compatible with the given type."""
    return controller.get_compatible_types(type_name, as_source)
