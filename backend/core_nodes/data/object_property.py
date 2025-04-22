from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class ObjectProperty(BaseNode):
    """
    A core node for accessing and modifying object properties.
    
    This node can get, set, or delete properties of objects.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.object_property",
            name="Object Property",
            version="1.0.0",
            description="Access and modify object properties",
            author="Workflow Builder",
            category=NodeCategory.DATA,
            tags=["object", "property", "data", "core"],
            inputs=[
                PortDefinition(
                    id="object",
                    name="Object",
                    type="object",
                    description="The object to access",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="value",
                    name="Value",
                    type="any",
                    description="The value to set (for set operation)",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="property_name",
                    name="Property Name",
                    type="string",
                    description="The name of the property to access (overrides config)",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="result",
                    name="Result",
                    type="any",
                    description="The result of the operation",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="modified_object",
                    name="Modified Object",
                    type="object",
                    description="The modified object (for set/delete operations)",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="exists",
                    name="Exists",
                    type="boolean",
                    description="Whether the property exists",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="operation",
                    name="Operation",
                    type="select",
                    description="The operation to perform",
                    required=True,
                    default_value="get",
                    options=[
                        {"label": "Get Property", "value": "get"},
                        {"label": "Set Property", "value": "set"},
                        {"label": "Delete Property", "value": "delete"},
                        {"label": "Check Property Exists", "value": "exists"}
                    ]
                ),
                ConfigField(
                    id="property",
                    name="Property",
                    type="string",
                    description="The property to access (can be a nested path like 'user.address.city')",
                    required=True
                ),
                ConfigField(
                    id="default_value",
                    name="Default Value",
                    type="code",
                    description="Default value to return if property doesn't exist (JSON format)",
                    required=False,
                    default_value="null"
                ),
                ConfigField(
                    id="create_path",
                    name="Create Path",
                    type="boolean",
                    description="Whether to create the path if it doesn't exist (for set operation)",
                    required=False,
                    default_value=False
                )
            ],
            ui_properties={
                "color": "#3498db",
                "icon": "key",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the object property node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The result of the operation
        """
        import json
        import copy
        
        # Get inputs
        obj = inputs.get("object")
        value = inputs.get("value")
        input_property = inputs.get("property_name")
        
        # Get configuration
        operation = config.get("operation", "get")
        property_path = input_property or config.get("property", "")
        default_value_str = config.get("default_value", "null")
        create_path = config.get("create_path", False)
        
        # Parse default value
        try:
            default_value = json.loads(default_value_str)
        except json.JSONDecodeError:
            default_value = None
        
        # Check if object is valid
        if obj is None or not isinstance(obj, dict):
            return {
                "result": default_value,
                "modified_object": {},
                "exists": False
            }
        
        # Make a copy of the object to avoid modifying the original
        obj_copy = copy.deepcopy(obj)
        
        # Split property path
        path_parts = property_path.split(".")
        
        # Function to get a nested property
        def get_nested_property(obj, path_parts):
            current = obj
            for part in path_parts:
                if not isinstance(current, dict) or part not in current:
                    return None, False
                current = current[part]
            return current, True
        
        # Function to set a nested property
        def set_nested_property(obj, path_parts, value, create_path):
            current = obj
            for i, part in enumerate(path_parts[:-1]):
                if part not in current:
                    if create_path:
                        current[part] = {}
                    else:
                        return False
                if not isinstance(current[part], dict):
                    if create_path:
                        current[part] = {}
                    else:
                        return False
                current = current[part]
            current[path_parts[-1]] = value
            return True
        
        # Function to delete a nested property
        def delete_nested_property(obj, path_parts):
            current = obj
            for i, part in enumerate(path_parts[:-1]):
                if not isinstance(current, dict) or part not in current:
                    return False
                current = current[part]
            if path_parts[-1] in current:
                del current[path_parts[-1]]
                return True
            return False
        
        # Perform the operation
        if operation == "get":
            result, exists = get_nested_property(obj_copy, path_parts)
            return {
                "result": result if exists else default_value,
                "modified_object": obj_copy,
                "exists": exists
            }
        
        elif operation == "set":
            success = set_nested_property(obj_copy, path_parts, value, create_path)
            result, exists = get_nested_property(obj_copy, path_parts)
            return {
                "result": result,
                "modified_object": obj_copy,
                "exists": exists
            }
        
        elif operation == "delete":
            success = delete_nested_property(obj_copy, path_parts)
            return {
                "result": success,
                "modified_object": obj_copy,
                "exists": False
            }
        
        elif operation == "exists":
            _, exists = get_nested_property(obj_copy, path_parts)
            return {
                "result": exists,
                "modified_object": obj_copy,
                "exists": exists
            }
        
        return {
            "result": None,
            "modified_object": obj_copy,
            "exists": False
        }
