from typing import Dict, Any, Optional, List
from backend.app.services.node_preview_service import NodePreviewService
from backend.app.services.plugin_manager import PluginManager
from backend.app.services.type_registry import TypeRegistry

class NodeController:
    def __init__(self, plugin_manager: PluginManager, type_registry: TypeRegistry):
        self.plugin_manager = plugin_manager
        self.type_registry = type_registry
        self.preview_service = NodePreviewService(plugin_manager, type_registry)
    
    def preview_node(self, plugin_id: str, config: Dict[str, Any], 
                    sample_inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Preview node execution with sample inputs.
        
        Args:
            plugin_id: The ID of the plugin to execute
            config: The node configuration
            sample_inputs: Optional sample inputs
            
        Returns:
            Preview results
        """
        return self.preview_service.preview_node(plugin_id, config, sample_inputs)
    
    def get_sample_inputs(self, plugin_id: str) -> Dict[str, Any]:
        """
        Generate sample inputs for a plugin.
        
        Args:
            plugin_id: The ID of the plugin
            
        Returns:
            Sample inputs for the plugin
        """
        metadata = self.plugin_manager.get_plugin_metadata(plugin_id)
        if not metadata:
            return {}
        
        return self.preview_service._generate_sample_inputs(metadata)
    
    def validate_node_config(self, plugin_id: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate node configuration.
        
        Args:
            plugin_id: The ID of the plugin
            config: The node configuration
            
        Returns:
            List of validation issues
        """
        # Get plugin metadata
        metadata = self.plugin_manager.get_plugin_metadata(plugin_id)
        if not metadata:
            return [{
                "type": "error",
                "message": f"Plugin '{plugin_id}' not found",
                "field": None
            }]
        
        issues = []
        
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
