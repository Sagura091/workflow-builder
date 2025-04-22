import os
from typing import Dict, List, Any, Optional
from backend.app.services.plugin_manager import PluginManager
from backend.app.models.plugin_metadata import PluginMetadata

class PluginController:
    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager

    def get_all_plugins(self) -> List[Dict[str, Any]]:
        """Get all available plugins with their metadata."""
        plugins = []
        for plugin_id, metadata in self.plugin_manager.get_all_plugin_metadata().items():
            plugins.append(self._format_plugin_metadata(metadata))
        return plugins

    def get_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific plugin with its metadata."""
        metadata = self.plugin_manager.get_plugin_metadata(plugin_id)
        if metadata:
            return self._format_plugin_metadata(metadata)
        return None

    def get_plugin_ui_schema(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get UI schema for a specific plugin."""
        metadata = self.plugin_manager.get_plugin_metadata(plugin_id)
        if not metadata:
            return None

        return {
            "id": metadata.id,
            "name": metadata.name,
            "category": metadata.category,
            "render": {
                "component": "StandardNode",  # or "CustomNode" if plugin has custom UI
                "props": {
                    "color": metadata.ui_properties.get("color", "#3498db"),
                    "icon": metadata.ui_properties.get("icon", "puzzle-piece"),
                    "width": metadata.ui_properties.get("width", 240),
                    "height": metadata.ui_properties.get("height", "auto"),
                    "headerComponent": metadata.ui_properties.get("headerComponent", "DefaultHeader"),
                    "bodyComponent": metadata.ui_properties.get("bodyComponent", "DefaultBody"),
                    "footerComponent": metadata.ui_properties.get("footerComponent", "DefaultFooter"),
                }
            },
            "ports": {
                "inputs": [
                    {
                        "id": port.id,
                        "name": port.name,
                        "type": port.type,
                        "position": port.ui_properties.get("position", "left-center"),
                        "color": self._get_type_color(port.type),
                        "tooltip": port.description,
                        "required": port.required,
                        "acceptsMultiple": port.accepts_multiple
                    } for port in metadata.inputs
                ],
                "outputs": [
                    {
                        "id": port.id,
                        "name": port.name,
                        "type": port.type,
                        "position": port.ui_properties.get("position", "right-center"),
                        "color": self._get_type_color(port.type),
                        "tooltip": port.description
                    } for port in metadata.outputs
                ]
            },
            "configForm": {
                "layout": metadata.ui_properties.get("form_layout", "standard"),
                "sections": metadata.ui_properties.get("form_sections", [
                    {
                        "id": "main",
                        "title": "Configuration",
                        "fields": [field.id for field in metadata.config_fields]
                    }
                ]),
                "fields": {
                    field.id: {
                        "type": field.type,
                        "label": field.name,
                        "description": field.description,
                        "default": field.default_value,
                        "required": field.required,
                        "options": field.options,
                        "validation": field.validation,
                        "ui": field.ui_properties
                    } for field in metadata.config_fields
                }
            }
        }

    def validate_plugin_config(self, plugin_id: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate plugin configuration."""
        issues = []

        # Get plugin metadata
        metadata = self.plugin_manager.get_plugin_metadata(plugin_id)
        if not metadata:
            issues.append({
                "type": "error",
                "message": f"Plugin '{plugin_id}' not found",
                "field": None
            })
            return issues

        # Check required fields
        for field in metadata.config_fields:
            if field.required and (field.id not in config or config[field.id] is None):
                issues.append({
                    "type": "error",
                    "message": f"Required field '{field.name}' is missing",
                    "field": field.id
                })

        # Validate field values
        for field_id, value in config.items():
            field = next((f for f in metadata.config_fields if f.id == field_id), None)
            if not field:
                issues.append({
                    "type": "warning",
                    "message": f"Unknown field '{field_id}'",
                    "field": field_id
                })
                continue

            # Type validation
            if field.type == "number" and not isinstance(value, (int, float)):
                issues.append({
                    "type": "error",
                    "message": f"Field '{field.name}' must be a number",
                    "field": field_id
                })
            elif field.type == "boolean" and not isinstance(value, bool):
                issues.append({
                    "type": "error",
                    "message": f"Field '{field.name}' must be a boolean",
                    "field": field_id
                })
            elif field.type == "select" and field.options and value not in [opt.get("value") for opt in field.options]:
                issues.append({
                    "type": "error",
                    "message": f"Field '{field.name}' has an invalid value",
                    "field": field_id
                })

            # Custom validation
            if field.validation:
                if "min" in field.validation and value < field.validation["min"]:
                    issues.append({
                        "type": "error",
                        "message": f"Field '{field.name}' must be at least {field.validation['min']}",
                        "field": field_id
                    })
                if "max" in field.validation and value > field.validation["max"]:
                    issues.append({
                        "type": "error",
                        "message": f"Field '{field.name}' must be at most {field.validation['max']}",
                        "field": field_id
                    })
                if "pattern" in field.validation and isinstance(value, str):
                    import re
                    if not re.match(field.validation["pattern"], value):
                        issues.append({
                            "type": "error",
                            "message": f"Field '{field.name}' has an invalid format",
                            "field": field_id
                        })

        return issues

    def _format_plugin_metadata(self, metadata: PluginMetadata) -> Dict[str, Any]:
        """Format plugin metadata for API response."""
        return {
            "id": metadata.id,
            "name": metadata.name,
            "version": metadata.version,
            "description": metadata.description,
            "author": metadata.author,
            "category": metadata.category,
            "tags": metadata.tags,
            "inputs": [
                {
                    "id": port.id,
                    "name": port.name,
                    "type": port.type,
                    "description": port.description,
                    "required": port.required
                } for port in metadata.inputs
            ],
            "outputs": [
                {
                    "id": port.id,
                    "name": port.name,
                    "type": port.type,
                    "description": port.description
                } for port in metadata.outputs
            ],
            "configFields": [
                {
                    "id": field.id,
                    "name": field.name,
                    "type": field.type,
                    "description": field.description,
                    "required": field.required,
                    "default": field.default_value,
                    "options": field.options
                } for field in metadata.config_fields
            ]
        }

    def _get_type_color(self, type_name: str) -> str:
        """Get color for a data type."""
        type_colors = {
            "string": "#2ecc71",
            "number": "#3498db",
            "boolean": "#9b59b6",
            "object": "#e67e22",
            "array": "#f1c40f",
            "file": "#1abc9c",
            "image": "#34495e",
            "dataset": "#e74c3c",
            "model": "#8e44ad",
            "features": "#d35400",
            "predictions": "#16a085",
            "any": "#7f8c8d"
        }
        return type_colors.get(type_name, "#7f8c8d")

    def create_plugin(self, plugin_id: str, plugin_code: str) -> Dict[str, Any]:
        """Create a new plugin."""
        # This method would be implemented to save a new plugin file
        # and then load it using the plugin manager
        # For now, we'll just return None
        return None
