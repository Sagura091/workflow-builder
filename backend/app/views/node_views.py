from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional

from backend.app.controllers.node_controller import NodeController
from backend.app.dependencies import get_node_controller

router = APIRouter(prefix="/api/nodes", tags=["nodes"])

@router.post("/{plugin_id}/preview")
async def preview_node(
    plugin_id: str,
    config: Dict[str, Any],
    sample_inputs: Optional[Dict[str, Any]] = None,
    controller: NodeController = Depends(get_node_controller)
) -> Dict[str, Any]:
    """
    Preview node execution with sample inputs.
    
    Args:
        plugin_id: The ID of the plugin to execute
        config: The node configuration
        sample_inputs: Optional sample inputs
        
    Returns:
        Preview results
    """
    result = controller.preview_node(plugin_id, config, sample_inputs)
    if result.get("status") == "error" and "not found" in result.get("message", ""):
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@router.get("/{plugin_id}/sample-inputs")
async def get_sample_inputs(
    plugin_id: str,
    controller: NodeController = Depends(get_node_controller)
) -> Dict[str, Any]:
    """
    Generate sample inputs for a plugin.
    
    Args:
        plugin_id: The ID of the plugin
        
    Returns:
        Sample inputs for the plugin
    """
    result = controller.get_sample_inputs(plugin_id)
    return {"inputs": result}

@router.post("/{plugin_id}/validate-config")
async def validate_node_config(
    plugin_id: str,
    config: Dict[str, Any],
    controller: NodeController = Depends(get_node_controller)
) -> Dict[str, Any]:
    """
    Validate node configuration.
    
    Args:
        plugin_id: The ID of the plugin
        config: The node configuration
        
    Returns:
        Validation results
    """
    issues = controller.validate_node_config(plugin_id, config)
    return {
        "valid": not any(issue["type"] == "error" for issue in issues),
        "issues": issues
    }
