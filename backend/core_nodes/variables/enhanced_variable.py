"""
Enhanced Variable Node

This module provides an enhanced variable node for storing and retrieving
values in the workflow.
"""

import json
from typing import Dict, Any, Optional, ClassVar, List, Union

from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.enhanced_base_node import EnhancedBaseNode


class EnhancedVariable(EnhancedBaseNode):
    """
    Enhanced variable node for storing and retrieving values.
    
    This node can store values in the workflow context and retrieve them later.
    """
    
    # Class variables
    __node_id__: ClassVar[str] = "core.variable"
    __node_version__: ClassVar[str] = "1.0.0"
    __node_category__: ClassVar[str] = NodeCategory.DATA_HANDLING
    __node_description__: ClassVar[str] = "Store and retrieve values in the workflow"
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id=self.__node_id__,
            name="Variable",
            version=self.__node_version__,
            description=self.__node_description__,
            author="Workflow Builder",
            category=self.__node_category__,
            tags=["variable", "storage", "data", "state", "core"],
            inputs=[
                PortDefinition(
                    id="value",
                    name="Value",
                    type="any",
                    description="The value to store",
                    required=False,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="set",
                    name="Set",
                    type="trigger",
                    description="Trigger to set the variable value",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="reset",
                    name="Reset",
                    type="trigger",
                    description="Reset the variable to its default value",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="value",
                    name="Value",
                    type="any",
                    description="The current value of the variable",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="has_value",
                    name="Has Value",
                    type="boolean",
                    description="Whether the variable has a value",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="type",
                    name="Type",
                    type="string",
                    description="The type of the variable value",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="name",
                    name="Variable Name",
                    type="string",
                    description="The name of the variable",
                    required=True,
                    default_value="my_variable"
                ),
                ConfigField(
                    id="scope",
                    name="Scope",
                    type="select",
                    description="The scope of the variable",
                    required=True,
                    default_value="workflow",
                    options=[
                        {"label": "Workflow", "value": "workflow"},
                        {"label": "Global", "value": "global"},
                        {"label": "Local", "value": "local"}
                    ]
                ),
                ConfigField(
                    id="default_value",
                    name="Default Value",
                    type="code",
                    description="The default value of the variable (JSON format)",
                    required=False,
                    default_value="null"
                ),
                ConfigField(
                    id="type",
                    name="Type",
                    type="select",
                    description="The type of the variable",
                    required=False,
                    default_value="any",
                    options=[
                        {"label": "Any", "value": "any"},
                        {"label": "String", "value": "string"},
                        {"label": "Number", "value": "number"},
                        {"label": "Boolean", "value": "boolean"},
                        {"label": "Object", "value": "object"},
                        {"label": "Array", "value": "array"}
                    ]
                ),
                ConfigField(
                    id="persistent",
                    name="Persistent",
                    type="boolean",
                    description="Whether the variable should persist between workflow runs",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="description",
                    name="Description",
                    type="text",
                    description="Description of the variable",
                    required=False
                )
            ],
            ui_properties={
                "color": "#9b59b6",
                "icon": "database",
                "width": 240
            }
        )
    
    def initialize(self) -> bool:
        """Initialize the node."""
        super().initialize()
        self._value = None
        self._has_value = False
        return True
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the variable node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The variable outputs
        """
        # Get configuration
        variable_name = config.get("name", "my_variable")
        scope = config.get("scope", "workflow")
        default_value_str = config.get("default_value", "null")
        variable_type = config.get("type", "any")
        persistent = config.get("persistent", False)
        
        # Parse default value
        try:
            default_value = json.loads(default_value_str)
        except json.JSONDecodeError:
            default_value = None
        
        # Get workflow context
        context = inputs.get("__context__", {})
        
        # Get variable storage based on scope
        if scope == "workflow":
            storage = context.get("variables", {})
        elif scope == "global":
            storage = context.get("global_variables", {})
        else:  # local
            storage = {}
        
        # Check for reset trigger
        if inputs.get("reset", False):
            self._value = default_value
            self._has_value = default_value is not None
            
            # Update storage
            if scope != "local":
                storage[variable_name] = default_value
                
                # Update context
                if scope == "workflow":
                    context["variables"] = storage
                else:  # global
                    context["global_variables"] = storage
        
        # Check for set trigger
        elif inputs.get("set", False) and "value" in inputs:
            value = inputs["value"]
            
            # Validate type if specified
            if variable_type != "any" and value is not None:
                value = self._convert_to_type(value, variable_type)
            
            self._value = value
            self._has_value = value is not None
            
            # Update storage
            if scope != "local":
                storage[variable_name] = value
                
                # Update context
                if scope == "workflow":
                    context["variables"] = storage
                else:  # global
                    context["global_variables"] = storage
        
        # If no value yet, check storage or use default
        elif not self._has_value:
            if variable_name in storage:
                self._value = storage[variable_name]
                self._has_value = self._value is not None
            else:
                self._value = default_value
                self._has_value = default_value is not None
                
                # Update storage with default value
                if scope != "local" and self._has_value:
                    storage[variable_name] = default_value
                    
                    # Update context
                    if scope == "workflow":
                        context["variables"] = storage
                    else:  # global
                        context["global_variables"] = storage
        
        # Determine value type
        value_type = self._get_value_type(self._value)
        
        return {
            "value": self._value,
            "has_value": self._has_value,
            "type": value_type,
            "__context__": context
        }
    
    def _convert_to_type(self, value: Any, target_type: str) -> Any:
        """
        Convert a value to the specified type.
        
        Args:
            value: The value to convert
            target_type: The target type
            
        Returns:
            The converted value
        """
        if target_type == "string":
            return str(value)
        elif target_type == "number":
            try:
                if isinstance(value, str):
                    if "." in value:
                        return float(value)
                    else:
                        return int(value)
                elif isinstance(value, (int, float)):
                    return value
                else:
                    return float(value)
            except (ValueError, TypeError):
                return 0
        elif target_type == "boolean":
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                return value.lower() in ["true", "yes", "1", "y"]
            elif isinstance(value, (int, float)):
                return value != 0
            else:
                return bool(value)
        elif target_type == "object":
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return {}
            else:
                return {}
        elif target_type == "array":
            if isinstance(value, (list, tuple)):
                return list(value)
            elif isinstance(value, str):
                try:
                    result = json.loads(value)
                    if isinstance(result, list):
                        return result
                    else:
                        return [result]
                except json.JSONDecodeError:
                    return [value]
            else:
                return [value]
        else:  # any
            return value
    
    def _get_value_type(self, value: Any) -> str:
        """
        Get the type of a value.
        
        Args:
            value: The value to check
            
        Returns:
            The type of the value
        """
        if value is None:
            return "null"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "unknown"
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the node configuration.
        
        Args:
            config: The node configuration
            
        Returns:
            The validated and normalized configuration
            
        Raises:
            ValueError: If the configuration is invalid
        """
        # Validate variable name
        name = config.get("name", "my_variable")
        if not name or not isinstance(name, str):
            raise ValueError("Variable name must be a non-empty string")
        
        # Validate scope
        scope = config.get("scope", "workflow")
        if scope not in ["workflow", "global", "local"]:
            raise ValueError(f"Invalid scope: {scope}")
        
        # Validate type
        variable_type = config.get("type", "any")
        if variable_type not in ["any", "string", "number", "boolean", "object", "array"]:
            raise ValueError(f"Invalid type: {variable_type}")
        
        # Validate default value
        default_value_str = config.get("default_value", "null")
        try:
            json.loads(default_value_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid default value JSON: {str(e)}")
        
        return config
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the node inputs.
        
        Args:
            inputs: The input values
            
        Returns:
            The validated and normalized inputs
            
        Raises:
            ValueError: If the inputs are invalid
        """
        # Ensure set and reset are booleans
        if "set" in inputs and not isinstance(inputs["set"], bool):
            inputs["set"] = bool(inputs["set"])
        
        if "reset" in inputs and not isinstance(inputs["reset"], bool):
            inputs["reset"] = bool(inputs["reset"])
        
        return inputs
