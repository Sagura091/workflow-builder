"""
Node Validation Router

This module provides API endpoints for node validation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional

from backend.app.models.responses import StandardResponse
from backend.app.models.node_validation import NodeValidationRequest, NodeValidationResponse
from backend.app.controllers.node_validation_controller import NodeValidationController
from backend.app.dependencies import get_node_registry, get_type_registry
from backend.app.services.node_registry import NodeRegistry
from backend.app.services.type_registry import TypeRegistry
from backend.app.exceptions import ValidationError

# Create router with API versioning
router = APIRouter(prefix="/api/v1/node-validation", tags=["Node Validation"])

# Dependency for NodeValidationController
def get_node_validation_controller(
    node_registry: NodeRegistry = Depends(get_node_registry),
    type_registry: TypeRegistry = Depends(get_type_registry)
):
    """Get NodeValidationController instance."""
    return NodeValidationController(node_registry, type_registry)

@router.post("/validate", response_model=StandardResponse)
async def validate_node(
    validation_request: NodeValidationRequest,
    controller: NodeValidationController = Depends(get_node_validation_controller)
) -> StandardResponse:
    """
    Validate a node.
    
    Args:
        validation_request: The validation request
        
    Returns:
        StandardResponse: Response containing the validation result
    """
    try:
        validation_result = await controller.validate_node(validation_request)
        return StandardResponse.success(data=validation_result)
    except ValidationError as e:
        return StandardResponse.error(message=str(e), data={"errors": e.errors})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/validate-connection", response_model=StandardResponse)
async def validate_connection(
    source_node_id: str,
    source_port: str,
    target_node_id: str,
    target_port: str,
    controller: NodeValidationController = Depends(get_node_validation_controller)
) -> StandardResponse:
    """
    Validate a connection between two nodes.
    
    Args:
        source_node_id: The ID of the source node
        source_port: The port on the source node
        target_node_id: The ID of the target node
        target_port: The port on the target node
        
    Returns:
        StandardResponse: Response containing the validation result
    """
    try:
        validation_result = controller.validate_connection(
            source_node_id, source_port, target_node_id, target_port
        )
        return StandardResponse.success(data=validation_result)
    except ValidationError as e:
        return StandardResponse.error(message=str(e), data={"errors": e.errors})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/validate-workflow", response_model=StandardResponse)
async def validate_workflow(
    workflow: Dict[str, Any],
    controller: NodeValidationController = Depends(get_node_validation_controller)
) -> StandardResponse:
    """
    Validate an entire workflow.
    
    Args:
        workflow: The workflow to validate
        
    Returns:
        StandardResponse: Response containing the validation result
    """
    try:
        validation_result = controller.validate_workflow(workflow)
        return StandardResponse.success(data=validation_result)
    except ValidationError as e:
        return StandardResponse.error(message=str(e), data={"errors": e.errors})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
