from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

from backend.app.controllers.plugin_controller import PluginController
from backend.app.dependencies import get_plugin_controller

router = APIRouter(prefix="/plugins", tags=["plugins"])

@router.get("/")
async def get_all_plugins(
    controller: PluginController = Depends(get_plugin_controller)
) -> List[Dict[str, Any]]:
    """Get all available plugins."""
    return controller.get_all_plugins()

@router.get("/{plugin_id}")
async def get_plugin(
    plugin_id: str,
    controller: PluginController = Depends(get_plugin_controller)
) -> Dict[str, Any]:
    """Get a specific plugin by ID."""
    plugin = controller.get_plugin(plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")
    return plugin

@router.get("/{plugin_id}/ui-schema")
async def get_plugin_ui_schema(
    plugin_id: str,
    controller: PluginController = Depends(get_plugin_controller)
) -> Dict[str, Any]:
    """Get UI schema for a specific plugin."""
    schema = controller.get_plugin_ui_schema(plugin_id)
    if not schema:
        raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")
    return schema

@router.post("/{plugin_id}/validate-config")
async def validate_plugin_config(
    plugin_id: str,
    config: Dict[str, Any],
    controller: PluginController = Depends(get_plugin_controller)
) -> List[Dict[str, Any]]:
    """Validate plugin configuration."""
    return controller.validate_plugin_config(plugin_id, config)
