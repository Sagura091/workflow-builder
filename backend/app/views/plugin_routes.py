from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel
from backend.app.controllers.plugin_controller import PluginController
from backend.app.services.plugin_manager import PluginManager
import os
import json

# Initialize the plugin manager and controller
plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "plugins")
plugin_manager = PluginManager(plugin_dir)
plugin_controller = PluginController(plugin_manager)

router = APIRouter()

class PluginCode(BaseModel):
    """Request model for creating a plugin."""
    code: str

@router.get("/plugins/describe")
async def describe_plugins() -> List[Dict[str, Any]]:
    """Get all available plugins."""
    plugins = plugin_controller.get_all_plugins()
    return plugins

@router.get("/node-types")
async def get_node_types():
    """Get all available node types with their connection points."""
    # Load node types from the config directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    node_types_file = os.path.join(project_root, "config", "node_types.json")

    if not os.path.exists(node_types_file):
        raise HTTPException(status_code=404, detail="Node types definition file not found")

    try:
        with open(node_types_file, "r") as f:
            node_types = json.load(f)
        return node_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading node types: {str(e)}")

@router.get("/core-nodes")
async def get_core_nodes():
    """Get all core nodes for the workflow builder."""
    # Load core nodes from the config directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    core_nodes_file = os.path.join(project_root, "config", "core_nodes.json")

    # If the file doesn't exist, return mock data
    if not os.path.exists(core_nodes_file):
        # Return mock core nodes
        return [
            {
                "id": "core.begin",
                "name": "Begin",
                "category": "CONTROL_FLOW",
                "description": "Starting point of the workflow",
                "inputs": [],
                "outputs": [
                    { "id": "trigger", "name": "Trigger", "type": "trigger", "ui_properties": { "position": "right-top" } },
                    { "id": "workflow_id", "name": "Workflow ID", "type": "string", "ui_properties": { "position": "right-center" } },
                    { "id": "timestamp", "name": "Timestamp", "type": "number", "ui_properties": { "position": "right-bottom" } }
                ],
                "ui_properties": {
                    "color": "#2ecc71",
                    "icon": "play",
                    "width": 240
                }
            },
            {
                "id": "core.end",
                "name": "End",
                "category": "CONTROL_FLOW",
                "description": "Ending point of the workflow",
                "inputs": [
                    { "id": "trigger", "name": "Trigger", "type": "trigger", "required": True, "ui_properties": { "position": "left-top" } },
                    { "id": "result", "name": "Result", "type": "any", "ui_properties": { "position": "left-center" } }
                ],
                "outputs": [
                    { "id": "workflow_id", "name": "Workflow ID", "type": "string", "ui_properties": { "position": "right-top" } },
                    { "id": "execution_time", "name": "Execution Time", "type": "number", "ui_properties": { "position": "right-center" } }
                ],
                "ui_properties": {
                    "color": "#e74c3c",
                    "icon": "stop",
                    "width": 240
                }
            },
            {
                "id": "core.conditional",
                "name": "Conditional",
                "category": "CONTROL_FLOW",
                "description": "Branch workflow based on conditions",
                "inputs": [
                    { "id": "value", "name": "Value", "type": "any", "required": True, "ui_properties": { "position": "left-top" } },
                    { "id": "compare_to", "name": "Compare To", "type": "any", "ui_properties": { "position": "left-bottom" } }
                ],
                "outputs": [
                    { "id": "true_output", "name": "True", "type": "any", "ui_properties": { "position": "right-top" } },
                    { "id": "false_output", "name": "False", "type": "any", "ui_properties": { "position": "right-bottom" } },
                    { "id": "result", "name": "Result", "type": "boolean", "ui_properties": { "position": "right-center" } }
                ],
                "ui_properties": {
                    "color": "#e74c3c",
                    "icon": "code-branch",
                    "width": 240
                }
            }
        ]


    try:
        with open(core_nodes_file, "r") as f:
            core_nodes = json.load(f)
        return core_nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading core nodes: {str(e)}")

@router.get("/type-system")
async def get_type_system():
    """Get the type system rules and definitions."""
    # Load type system from the config directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    type_system_file = os.path.join(project_root, "config", "type_system.json")
    type_rules_file = os.path.join(project_root, "config", "type_rules.json")

    if not os.path.exists(type_system_file) or not os.path.exists(type_rules_file):
        raise HTTPException(status_code=404, detail="Type system files not found")

    try:
        with open(type_system_file, "r") as f:
            type_system = json.load(f)

        with open(type_rules_file, "r") as f:
            type_rules = json.load(f)

        # Combine the type system and rules
        return {
            "types": type_system.get("types", {}),
            "rules": type_rules.get("rules", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading type system: {str(e)}")

@router.get("/plugins/{plugin_id}")
async def get_plugin(plugin_id: str) -> Dict[str, Any]:
    """Get a plugin by ID."""
    plugin = plugin_controller.get_plugin(plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin

@router.post("/plugins/{plugin_id}", status_code=status.HTTP_201_CREATED)
async def create_plugin(plugin_id: str, plugin: PluginCode) -> Dict[str, Any]:
    """Create a new plugin."""
    result = plugin_controller.create_plugin(plugin_id, plugin.code)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create plugin")
    return result
