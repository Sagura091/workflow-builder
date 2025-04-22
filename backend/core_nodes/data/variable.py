from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class Variable(BaseNode):
    """
    A core node for storing and retrieving variables.
    
    This node can store values and make them available to other nodes.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.variable",
            name="Variable",
            version="1.0.0",
            description="Store and retrieve variables",
            author="Workflow Builder",
            category=NodeCategory.DATA,
            tags=["variable", "storage", "data", "core"],
            inputs=[
                PortDefinition(
                    id="value",
                    name="Value",
                    type="any",
                    description="The value to store",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="set",
                    name="Set",
                    type="trigger",
                    description="Trigger to set the variable",
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
                    description="The stored value",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="is_set",
                    name="Is Set",
                    type="boolean",
                    description="Whether the variable has been set",
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
                    description="Name of the variable",
                    required=True
                ),
                ConfigField(
                    id="scope",
                    name="Scope",
                    type="select",
                    description="Scope of the variable",
                    required=False,
                    default_value="workflow",
                    options=[
                        {"label": "Workflow", "value": "workflow"},
                        {"label": "Global", "value": "global"}
                    ]
                ),
                ConfigField(
                    id="initial_value",
                    name="Initial Value",
                    type="code",
                    description="Initial value of the variable (JSON format)",
                    required=False,
                    default_value="null"
                ),
                ConfigField(
                    id="persist",
                    name="Persist",
                    type="boolean",
                    description="Whether to persist the variable between workflow runs",
                    required=False,
                    default_value=False
                )
            ],
            ui_properties={
                "color": "#f39c12",
                "icon": "database",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the variable node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The variable value
        """
        import json
        
        # Get configuration
        var_name = config.get("name", "var")
        scope = config.get("scope", "workflow")
        initial_value_str = config.get("initial_value", "null")
        persist = config.get("persist", False)
        
        # Parse initial value
        try:
            initial_value = json.loads(initial_value_str)
        except json.JSONDecodeError:
            initial_value = None
        
        # Get workflow context
        context = inputs.get("__context__", {})
        
        # Get variable storage based on scope
        if scope == "global":
            # Global variables are stored in a global context
            var_storage = context.get("global_variables", {})
        else:
            # Workflow variables are stored in the workflow context
            var_storage = context.get("workflow_variables", {})
        
        # Check if variable exists
        var_key = f"var_{var_name}"
        is_set = var_key in var_storage
        
        # Get current value or use initial value
        current_value = var_storage.get(var_key, initial_value)
        
        # Check if we should set a new value
        set_trigger = inputs.get("set", False)
        new_value = inputs.get("value")
        
        if set_trigger and new_value is not None:
            # Update the value
            current_value = new_value
            is_set = True
            
            # Update the storage
            var_storage[var_key] = current_value
            
            # Update the context
            if scope == "global":
                context["global_variables"] = var_storage
            else:
                context["workflow_variables"] = var_storage
        
        return {
            "value": current_value,
            "is_set": is_set,
            "__context__": context
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        var_name = config.get("name", "")
        if not var_name:
            return "Variable name is required"
        
        initial_value_str = config.get("initial_value", "null")
        try:
            json.loads(initial_value_str)
        except json.JSONDecodeError as e:
            return f"Invalid JSON in Initial Value: {str(e)}"
        
        return None
