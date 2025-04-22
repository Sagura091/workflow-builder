"""
Compare Node

This node compares two values and outputs a boolean result.
"""

from backend.core_nodes.base_node import BaseNode

class Compare(BaseNode):
    """
    Compares two values and outputs a boolean result.
    """
    
    def __init__(self):
        super().__init__()
        self.id = "core.compare"
        self.name = "Compare"
        self.category = "CONTROL_FLOW"
        self.description = "Compare two values and output a boolean result"
        self.inputs = [
            {
                "id": "value_a",
                "name": "Value A",
                "type": "any",
                "description": "First value to compare",
                "required": True
            },
            {
                "id": "value_b",
                "name": "Value B",
                "type": "any",
                "description": "Second value to compare",
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
                "id": "result",
                "name": "Result",
                "type": "boolean",
                "description": "Comparison result"
            },
            {
                "id": "true_output",
                "name": "True",
                "type": "trigger",
                "description": "Triggered if comparison is true"
            },
            {
                "id": "false_output",
                "name": "False",
                "type": "trigger",
                "description": "Triggered if comparison is false"
            }
        ]
        self.config_fields = [
            {
                "name": "operator",
                "type": "select",
                "label": "Operator",
                "options": [
                    {"label": "Equal (==)", "value": "eq"},
                    {"label": "Not Equal (!=)", "value": "ne"},
                    {"label": "Greater Than (>)", "value": "gt"},
                    {"label": "Greater Than or Equal (>=)", "value": "ge"},
                    {"label": "Less Than (<)", "value": "lt"},
                    {"label": "Less Than or Equal (<=)", "value": "le"},
                    {"label": "Contains", "value": "contains"},
                    {"label": "Starts With", "value": "startswith"},
                    {"label": "Ends With", "value": "endswith"}
                ],
                "default": "eq"
            },
            {
                "name": "result_variable",
                "type": "string",
                "label": "Result Variable Name",
                "default": "comparison_result"
            }
        ]
        self.ui_properties = {
            "color": "#f39c12",
            "icon": "equals",
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
        value_a = inputs.get("value_a")
        value_b = inputs.get("value_b")
        operator = config.get("operator", "eq")
        result_var_name = config.get("result_variable", "comparison_result")
        
        # Perform the comparison
        result = False
        
        try:
            if operator == "eq":
                result = value_a == value_b
            elif operator == "ne":
                result = value_a != value_b
            elif operator == "gt":
                result = value_a > value_b
            elif operator == "ge":
                result = value_a >= value_b
            elif operator == "lt":
                result = value_a < value_b
            elif operator == "le":
                result = value_a <= value_b
            elif operator == "contains":
                if isinstance(value_a, str) and isinstance(value_b, str):
                    result = value_b in value_a
                elif hasattr(value_a, "__contains__"):
                    result = value_b in value_a
                else:
                    result = False
            elif operator == "startswith":
                if isinstance(value_a, str) and isinstance(value_b, str):
                    result = value_a.startswith(value_b)
                else:
                    result = False
            elif operator == "endswith":
                if isinstance(value_a, str) and isinstance(value_b, str):
                    result = value_a.endswith(value_b)
                else:
                    result = False
        except Exception as e:
            print(f"Error comparing values: {e}")
            result = False
        
        # Store result in a variable if configured
        if workflow_context and result_var_name:
            workflow_context.variables.set(result_var_name, result)
        
        return {
            "result": result,
            "true_output": result,
            "false_output": not result
        }
