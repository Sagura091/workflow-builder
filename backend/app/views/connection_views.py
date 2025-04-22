from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List

from backend.app.controllers.connection_controller import ConnectionController
from backend.app.dependencies import get_connection_controller

router = APIRouter(prefix="/api/connections", tags=["connections"])

@router.post("/suggest")
async def suggest_connections(
    workflow: Dict[str, Any],
    controller: ConnectionController = Depends(get_connection_controller)
) -> Dict[str, Any]:
    """
    Suggest possible connections in a workflow.
    
    Args:
        workflow: The workflow data
        
    Returns:
        List of connection suggestions
    """
    suggestions = controller.suggest_connections(workflow)
    return {"suggestions": suggestions}

@router.get("/check-compatibility")
async def check_connection_compatibility(
    source_type: str,
    target_type: str,
    controller: ConnectionController = Depends(get_connection_controller)
) -> Dict[str, Any]:
    """
    Check if two types are compatible for connection.
    
    Args:
        source_type: Source port type
        target_type: Target port type
        
    Returns:
        Compatibility information
    """
    return controller.check_connection_compatibility(source_type, target_type)

@router.post("/validate")
async def validate_connection(
    connection: Dict[str, Any],
    workflow: Dict[str, Any],
    controller: ConnectionController = Depends(get_connection_controller)
) -> Dict[str, Any]:
    """
    Validate a connection in a workflow.
    
    Args:
        connection: The connection to validate
        workflow: The workflow data
        
    Returns:
        Validation results
    """
    return controller.validate_connection(connection, workflow)
