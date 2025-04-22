"""
Node Validation Routes

This module provides FastAPI routes for validating node definitions.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.models.responses import StandardResponse
from backend.app.controllers.node_validation_controller import NodeValidationController
from backend.app.models.node_validation import NodeValidationRequest
from backend.app.services.node_registry import NodeRegistry
from backend.app.services.type_registry import TypeRegistry
from backend.app.dependencies import get_node_registry, get_type_registry

# Create models
class NodeDefinition(BaseModel):
    """Node definition model."""
    id: str
    name: str
    category: str
    description: Optional[str] = None
    inputs: Optional[List[Dict[str, Any]]] = []
    outputs: Optional[List[Dict[str, Any]]] = []
    ui_properties: Optional[Dict[str, Any]] = {}

# Create router
router = APIRouter(prefix="/api/nodes", tags=["nodes"])

# Also create a router with the old path for backward compatibility
legacy_router = APIRouter(tags=["nodes"])

# Dependency for NodeValidationController
def get_node_validation_controller():
    """Get NodeValidationController instance."""
    return NodeValidationController()

@router.post("/validate", response_model=StandardResponse)
@legacy_router.post("/nodes/validate", response_model=StandardResponse)
async def validate_node_definition(
    node_def: NodeDefinition,
    controller: NodeValidationController = Depends(get_node_validation_controller)
) -> StandardResponse:
    """
    Validate a node definition.

    Args:
        node_def: The node definition to validate

    Returns:
        Validation result
    """
    result = controller.validate_node_definition(node_def.model_dump())

    # If validation was successful and we have an updated node definition, return it
    if result.get('valid') and 'node_def' in result:
        return StandardResponse.success(
            data={
                "valid": True,
                "node_def": result['node_def']
            },
            message="Node definition validation completed"
        )

    return StandardResponse.success(
        data=result,
        message="Node definition validation completed"
    )

@router.post("/validate-connection", response_model=StandardResponse)
@legacy_router.post("/nodes/validate-connection", response_model=StandardResponse)
async def validate_node_connection(
    validation_request: NodeValidationRequest,
    node_registry: NodeRegistry = Depends(get_node_registry),
    type_registry: TypeRegistry = Depends(get_type_registry)
) -> StandardResponse:
    """
    Validate a node connection.

    Args:
        validation_request: The validation request

    Returns:
        Validation results
    """
    controller = NodeValidationController(node_registry, type_registry)
    result = await controller.validate_node(validation_request)
    return StandardResponse.success(
        data=result,
        message="Node connection validation completed"
    )
