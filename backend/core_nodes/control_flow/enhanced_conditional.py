"""
Enhanced Conditional Node

This module provides an enhanced conditional node for branching workflow
execution based on conditions.
"""

from typing import Dict, Any, Optional, ClassVar, List

from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.enhanced_base_node import EnhancedBaseNode


class EnhancedConditional(EnhancedBaseNode):
    """
    Enhanced conditional node for branching workflow execution.
    
    This node evaluates a condition and routes data accordingly.
    """
    
    # Class variables
    __node_id__: ClassVar[str] = "core.conditional"
    __node_version__: ClassVar[str] = "1.0.0"
    __node_category__: ClassVar[str] = NodeCategory.CONTROL_FLOW
    __node_description__: ClassVar[str] = "Branch workflow based on conditions"
    
    # Supported operators
    OPERATORS = [
        {"value": "eq", "label": "Equal (==)"},
        {"value": "neq", "label": "Not Equal (!=)"},
        {"value": "gt", "label": "Greater Than (>)"},
        {"value": "gte", "label": "Greater Than or Equal (>=)"},
        {"value": "lt", "label": "Less Than (<)"},
        {"value": "lte", "label": "Less Than or Equal (<=)"},
        {"value": "contains", "label": "Contains"},
        {"value": "not_contains", "label": "Does Not Contain"},
        {"value": "startswith", "label": "Starts With"},
        {"value": "endswith", "label": "Ends With"},
        {"value": "empty", "label": "Is Empty"},
        {"value": "not_empty", "label": "Is Not Empty"},
        {"value": "is_true", "label": "Is True"},
        {"value": "is_false", "label": "Is False"},
        {"value": "in", "label": "In (Value is in List)"},
        {"value": "not_in", "label": "Not In (Value is not in List)"},
        {"value": "regex", "label": "Matches Regex"}
    ]
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id=self.__node_id__,
            name="Conditional",
            version=self.__node_version__,
            description=self.__node_description__,
            author="Workflow Builder",
            category=self.__node_category__,
            tags=["conditional", "if", "branch", "condition", "control flow", "core"],
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
                        "position": "left-center"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="true_output",
                    name="True",
                    type="any",
                    description="Output when the condition is true",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="false_output",
                    name="False",
                    type="any",
                    description="Output when the condition is false",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="result",
                    name="Result",
                    type="boolean",
                    description="The result of the condition evaluation",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="operator",
                    name="Operator",
                    type="select",
                    description="The operator to use for comparison",
                    required=True,
                    default_value="eq",
                    options=[op for op in self.OPERATORS]
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
                ),
                ConfigField(
                    id="regex_flags",
                    name="Regex Flags",
                    type="string",
                    description="Flags for regex matching (e.g., 'i' for case-insensitive)",
                    required=False,
                    default_value=""
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
        regex_flags = config.get("regex_flags", "")
        
        # Determine which value to pass through
        if pass_through == "value":
            pass_value = value
        elif pass_through == "compare_to":
            pass_value = compare_to
        else:  # custom
            pass_value = custom_value
        
        # Evaluate condition
        result = self._evaluate_condition(value, compare_to, operator, case_sensitive, regex_flags)
        
        # Return branched outputs
        return {
            "true_output": pass_value if result else None,
            "false_output": None if result else pass_value,
            "result": result
        }
    
    def _evaluate_condition(
        self, 
        value: Any, 
        compare_to: Any, 
        operator: str, 
        case_sensitive: bool,
        regex_flags: str
    ) -> bool:
        """
        Evaluate a condition based on the operator.
        
        Args:
            value: The value to evaluate
            compare_to: The value to compare against
            operator: The operator to use
            case_sensitive: Whether string comparisons are case sensitive
            regex_flags: Flags for regex matching
            
        Returns:
            The result of the condition evaluation
        """
        import re
        
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
                value_str = value.lower()
                compare_to_str = compare_to.lower()
            else:
                value_str = value
                compare_to_str = compare_to
            
            if operator == "eq":
                return value_str == compare_to_str
            elif operator == "neq":
                return value_str != compare_to_str
            elif operator == "contains":
                return compare_to_str in value_str
            elif operator == "not_contains":
                return compare_to_str not in value_str
            elif operator == "startswith":
                return value_str.startswith(compare_to_str)
            elif operator == "endswith":
                return value_str.endswith(compare_to_str)
            elif operator == "regex":
                try:
                    # Apply regex flags
                    flags = 0
                    if 'i' in regex_flags:
                        flags |= re.IGNORECASE
                    if 'm' in regex_flags:
                        flags |= re.MULTILINE
                    if 's' in regex_flags:
                        flags |= re.DOTALL
                    
                    return bool(re.search(compare_to, value, flags))
                except re.error:
                    return False
        
        # Numeric operations
        if isinstance(value, (int, float)) and isinstance(compare_to, (int, float)):
            if operator == "eq":
                return value == compare_to
            elif operator == "neq":
                return value != compare_to
            elif operator == "gt":
                return value > compare_to
            elif operator == "gte":
                return value >= compare_to
            elif operator == "lt":
                return value < compare_to
            elif operator == "lte":
                return value <= compare_to
        
        # List operations
        if operator == "in" and isinstance(compare_to, (list, tuple, set)):
            return value in compare_to
        elif operator == "not_in" and isinstance(compare_to, (list, tuple, set)):
            return value not in compare_to
        
        # Boolean operations
        if isinstance(value, bool) and isinstance(compare_to, bool):
            if operator == "eq":
                return value == compare_to
            elif operator == "neq":
                return value != compare_to
        
        # Default equality check for other types
        if operator == "eq":
            return value == compare_to
        elif operator == "neq":
            return value != compare_to
        
        # Default to false for unsupported operations
        return False
    
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
        # Validate operator
        operator = config.get("operator", "eq")
        valid_operators = [op["value"] for op in self.OPERATORS]
        if operator not in valid_operators:
            raise ValueError(f"Invalid operator: {operator}")
        
        # Validate pass_through
        pass_through = config.get("pass_through", "value")
        if pass_through not in ["value", "compare_to", "custom"]:
            raise ValueError(f"Invalid pass_through value: {pass_through}")
        
        # Validate regex_flags
        regex_flags = config.get("regex_flags", "")
        if regex_flags and not all(flag in "imsx" for flag in regex_flags):
            raise ValueError(f"Invalid regex flags: {regex_flags}")
        
        return config
