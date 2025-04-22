"""
API Routes

This module defines the API routes for the workflow builder.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any, Optional
from backend.app.dependencies import get_node_registry, get_plugin_manager, get_type_registry
from backend.app.controllers.node_types_controller import NodeTypesController
from backend.app.controllers.plugin_controller import PluginController
from backend.app.controllers.type_system_controller import TypeSystemController
from backend.app.controllers.node_validation_controller import NodeValidationController
from backend.app.models.node_validation import NodeValidationRequest, NodeValidationResponse
from backend.app.services.node_registry import NodeRegistry
from backend.app.services.plugin_manager import PluginManager
from backend.app.services.type_registry import TypeRegistry

router = APIRouter(prefix="/api")

# Node Types Routes
@router.get("/node-types", response_model=Dict[str, Any], tags=["Node Types"])
async def get_node_types(
    node_registry: NodeRegistry = Depends(get_node_registry)
):
    """
    Get all node types.
    """
    controller = NodeTypesController(node_registry)
    return controller.get_node_types()

@router.get("/node-types/{node_id}", response_model=Dict[str, Any], tags=["Node Types"])
async def get_node_type(
    node_id: str,
    node_registry: NodeRegistry = Depends(get_node_registry)
):
    """
    Get a specific node type by ID.
    """
    controller = NodeTypesController(node_registry)
    node_type = controller.get_node_type(node_id)
    if not node_type:
        raise HTTPException(status_code=404, detail=f"Node type '{node_id}' not found")
    return {"status": "success", "data": node_type}

# Plugin Routes
@router.get("/plugins", response_model=Dict[str, Any], tags=["Plugins"])
async def get_plugins(
    plugin_manager: PluginManager = Depends(get_plugin_manager)
):
    """
    Get all plugins.
    """
    controller = PluginController(plugin_manager)
    return {"status": "success", "data": controller.get_all_plugins()}

@router.get("/plugins/{plugin_id}", response_model=Dict[str, Any], tags=["Plugins"])
async def get_plugin(
    plugin_id: str,
    plugin_manager: PluginManager = Depends(get_plugin_manager)
):
    """
    Get a specific plugin by ID.
    """
    controller = PluginController(plugin_manager)
    plugin = controller.get_plugin(plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")
    return {"status": "success", "data": plugin}

# Type System Routes
@router.get("/type-system", response_model=Dict[str, Any], tags=["Type System"])
async def get_type_system(
    type_registry: TypeRegistry = Depends(get_type_registry)
):
    """
    Get the type system.
    """
    controller = TypeSystemController()
    return controller.get_type_system()

@router.get("/type-system/compatibility", response_model=Dict[str, Any], tags=["Type System"])
async def check_type_compatibility(
    source_type: str,
    target_type: str,
    type_registry: TypeRegistry = Depends(get_type_registry)
):
    """
    Check if two types are compatible.
    """
    controller = TypeSystemController()
    return controller.check_type_compatibility(source_type, target_type)

# Node Validation Routes
@router.post("/nodes/validate", response_model=NodeValidationResponse, tags=["Node Validation"])
async def validate_node(
    validation_request: NodeValidationRequest,
    node_registry: NodeRegistry = Depends(get_node_registry),
    type_registry: TypeRegistry = Depends(get_type_registry)
):
    """
    Validate a node.
    """
    controller = NodeValidationController(node_registry, type_registry)
    return await controller.validate_node(validation_request)
