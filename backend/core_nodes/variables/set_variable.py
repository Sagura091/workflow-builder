"""
Set Variable Node

This node sets a variable in the workflow context.
"""

from backend.core_nodes.base_node import BaseNode

class SetVariable(BaseNode):
    """
    Sets a variable in the workflow context.
    """
    
    def __init__(self):
        super().__init__()
        self.id = "core.set_variable"
        self.name = "Set Variable"
        self.category = "VARIABLES"
        self.description = "Set a variable value"
        self.inputs = [
            {
                "id": "value",
                "name": "Value",
                "type": "any",
                "description": "Value to store",
                "required": True
            },
            {
                "id": "trigger",
                "name": "Trigger",
                "type": "trigger",
                "description": "Execution trigger",
                "required": False
            }
        ]
        self.outputs = [
            {
                "id": "value",
                "name": "Value",
                "type": "any",
                "description": "The stored value"
            },
            {
                "id": "completed",
                "name": "Completed",
                "type": "trigger",
                "description": "Triggered when variable is set"
            }
        ]
        self.config_fields = [
            {
                "name": "variable_name",
                "type": "string",
                "label": "Variable Name",
                "default": "myVariable"
            }
        ]
        self.ui_properties = {
            "color": "#3498db",
            "icon": "database",
            "width": 240
        }
    
    def execute(self, inputs, config, workflow_context=None):
        """
        Execute the node.
        
        Args:
            inputs (dict): The input values.
            config (dict): The node configuration.
            workflow_context (WorkflowContext, optional): The workflow context.
            
        Returns:
            dict: The output values.
        """
        value = inputs.get("value")
        variable_name = config.get("variable_name", "myVariable")
        
        # Store the variable in the workflow context if available
        if workflow_context and hasattr(workflow_context, "variables"):
            workflow_context.variables.set(variable_name, value)
        
        return {
            "value": value,
            "completed": True
        }
