"""
Get Variable Node

This node gets a variable from the workflow context.
"""

from backend.core_nodes.base_node import BaseNode

class GetVariable(BaseNode):
    """
    Gets a variable from the workflow context.
    """
    
    def __init__(self):
        super().__init__()
        self.id = "core.get_variable"
        self.name = "Get Variable"
        self.category = "VARIABLES"
        self.description = "Get a variable value"
        self.inputs = [
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
                "description": "The variable value"
            },
            {
                "id": "exists",
                "name": "Exists",
                "type": "boolean",
                "description": "Whether the variable exists"
            }
        ]
        self.config_fields = [
            {
                "name": "variable_name",
                "type": "string",
                "label": "Variable Name",
                "default": "myVariable"
            },
            {
                "name": "default_value",
                "type": "string",
                "label": "Default Value",
                "default": ""
            }
        ]
        self.ui_properties = {
            "color": "#2ecc71",
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
        variable_name = config.get("variable_name", "myVariable")
        default_value = config.get("default_value", "")
        
        # Get the variable from the workflow context if available
        if workflow_context and hasattr(workflow_context, "variables"):
            exists = workflow_context.variables.has(variable_name)
            value = workflow_context.variables.get(variable_name, default_value)
        else:
            exists = False
            value = default_value
        
        return {
            "value": value,
            "exists": exists
        }
