from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class Conditional(BaseNode):
    """
    A core node for conditional branching.
    
    This node evaluates a condition and routes data accordingly.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.conditional",
            name="Conditional",
            version="1.0.0",
            description="Branch workflow based on conditions",
            author="Workflow Builder",
            category=NodeCategory.CONTROL_FLOW,
            tags=["conditional", "if", "branch", "control flow", "core"],
            inputs=[
                PortDefinition(
                    id="value",
                    name="Value",
                    type="any",
                    description="The value to evaluate",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="compare_to",
                    name="Compare To",
                    type="any",
                    description="The value to compare against",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="true_output",
                    name="True",
                    type="any",
                    description="Output when condition is true",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="false_output",
                    name="False",
                    type="any",
                    description="Output when condition is false",
                    ui_properties={
                        "position": "right-bottom"
                    }
                ),
                PortDefinition(
                    id="result",
                    name="Result",
                    type="boolean",
                    description="The result of the condition evaluation",
                    ui_properties={
                        "position": "right-center"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="operator",
                    name="Operator",
                    type="select",
                    description="The comparison operator",
                    required=True,
                    default_value="eq",
                    options=[
                        {"label": "Equals", "value": "eq"},
                        {"label": "Not Equals", "value": "neq"},
                        {"label": "Greater Than", "value": "gt"},
                        {"label": "Less Than", "value": "lt"},
                        {"label": "Greater Than or Equal", "value": "gte"},
                        {"label": "Less Than or Equal", "value": "lte"},
                        {"label": "Contains", "value": "contains"},
                        {"label": "Starts With", "value": "startswith"},
                        {"label": "Ends With", "value": "endswith"},
                        {"label": "Is Empty", "value": "empty"},
                        {"label": "Is Not Empty", "value": "not_empty"},
                        {"label": "Is True", "value": "is_true"},
                        {"label": "Is False", "value": "is_false"}
                    ]
                ),
                ConfigField(
                    id="case_sensitive",
                    name="Case Sensitive",
                    type="boolean",
                    description="Whether string comparisons are case sensitive",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="pass_through",
                    name="Pass Through Value",
                    type="select",
                    description="Which value to pass through the outputs",
                    required=False,
                    default_value="value",
                    options=[
                        {"label": "Input Value", "value": "value"},
                        {"label": "Compare To Value", "value": "compare_to"},
                        {"label": "Custom Value", "value": "custom"}
                    ]
                ),
                ConfigField(
                    id="custom_value",
                    name="Custom Value",
                    type="string",
                    description="Custom value to pass through (when Pass Through Value is 'custom')",
                    required=False
                )
            ],
            ui_properties={
                "color": "#e74c3c",
                "icon": "code-branch",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the conditional branching.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The branched outputs
        """
        # Get input values
        value = inputs.get("value")
        compare_to = inputs.get("compare_to")
        
        # Get configuration
        operator = config.get("operator", "eq")
        case_sensitive = config.get("case_sensitive", False)
        pass_through = config.get("pass_through", "value")
        custom_value = config.get("custom_value", "")
        
        # Determine which value to pass through
        if pass_through == "value":
            pass_value = value
        elif pass_through == "compare_to":
            pass_value = compare_to
        else:  # custom
            pass_value = custom_value
        
        # Evaluate condition
        result = self._evaluate_condition(value, compare_to, operator, case_sensitive)
        
        # Return branched outputs
        return {
            "true_output": pass_value if result else None,
            "false_output": None if result else pass_value,
            "result": result
        }
    
    def _evaluate_condition(self, value: Any, compare_to: Any, operator: str, case_sensitive: bool) -> bool:
        """Evaluate a condition based on the operator."""
        # Handle special operators that don't need compare_to
        if operator == "empty":
            if value is None:
                return True
            if isinstance(value, str):
                return value.strip() == ""
            if isinstance(value, (list, dict)):
                return len(value) == 0
            return False
        
        elif operator == "not_empty":
            if value is None:
                return False
            if isinstance(value, str):
                return value.strip() != ""
            if isinstance(value, (list, dict)):
                return len(value) > 0
            return True
        
        elif operator == "is_true":
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ["true", "yes", "1", "y"]
            if isinstance(value, (int, float)):
                return value != 0
            return bool(value)
        
        elif operator == "is_false":
            if isinstance(value, bool):
                return not value
            if isinstance(value, str):
                return value.lower() in ["false", "no", "0", "n"]
            if isinstance(value, (int, float)):
                return value == 0
            return not bool(value)
        
        # Handle operators that need compare_to
        # String operations
        if isinstance(value, str) and isinstance(compare_to, str):
            if not case_sensitive:
                value = value.lower()
                compare_to = compare_to.lower()
            
            if operator == "eq":
                return value == compare_to
            elif operator == "neq":
                return value != compare_to
            elif operator == "contains":
                return compare_to in value
            elif operator == "startswith":
                return value.startswith(compare_to)
            elif operator == "endswith":
                return value.endswith(compare_to)
        
        # Numeric operations
        if isinstance(value, (int, float)) and isinstance(compare_to, (int, float)):
            if operator == "eq":
                return value == compare_to
            elif operator == "neq":
                return value != compare_to
            elif operator == "gt":
                return value > compare_to
            elif operator == "lt":
                return value < compare_to
            elif operator == "gte":
                return value >= compare_to
            elif operator == "lte":
                return value <= compare_to
        
        # Default comparison
        if operator == "eq":
            return value == compare_to
        elif operator == "neq":
            return value != compare_to
        
        return False
