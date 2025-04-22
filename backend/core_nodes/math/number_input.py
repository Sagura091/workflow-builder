from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class NumberInput(BaseNode):
    """
    A core node for providing number input.
    
    This node allows users to enter numbers manually or calculate them.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.number_input",
            name="Number Input",
            version="1.0.0",
            description="Enter numbers manually",
            author="Workflow Builder",
            category=NodeCategory.MATH,
            tags=["number", "input", "numeric", "core"],
            inputs=[
                PortDefinition(
                    id="override",
                    name="Override",
                    type="number",
                    description="Number to override the configured value",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="factor",
                    name="Factor",
                    type="number",
                    description="Factor to multiply the number by",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="number",
                    name="Number",
                    type="number",
                    description="The output number",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="is_integer",
                    name="Is Integer",
                    type="boolean",
                    description="Whether the number is an integer",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="is_positive",
                    name="Is Positive",
                    type="boolean",
                    description="Whether the number is positive",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="value",
                    name="Value",
                    type="number",
                    description="The number value",
                    required=True,
                    default_value=0
                ),
                ConfigField(
                    id="min",
                    name="Minimum",
                    type="number",
                    description="Minimum allowed value",
                    required=False
                ),
                ConfigField(
                    id="max",
                    name="Maximum",
                    type="number",
                    description="Maximum allowed value",
                    required=False
                ),
                ConfigField(
                    id="step",
                    name="Step",
                    type="number",
                    description="Step size for the number input",
                    required=False,
                    default_value=1
                ),
                ConfigField(
                    id="round",
                    name="Round",
                    type="select",
                    description="How to round the number",
                    required=False,
                    default_value="none",
                    options=[
                        {"label": "None", "value": "none"},
                        {"label": "Round", "value": "round"},
                        {"label": "Floor", "value": "floor"},
                        {"label": "Ceiling", "value": "ceil"}
                    ]
                ),
                ConfigField(
                    id="precision",
                    name="Precision",
                    type="number",
                    description="Number of decimal places",
                    required=False,
                    default_value=2
                )
            ],
            ui_properties={
                "color": "#f39c12",
                "icon": "calculator",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the number input node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The number output
        """
        import math
        
        # Get inputs
        override = inputs.get("override")
        factor = inputs.get("factor")
        
        # Get configuration
        value = config.get("value", 0)
        min_value = config.get("min")
        max_value = config.get("max")
        round_mode = config.get("round", "none")
        precision = int(config.get("precision", 2))
        
        # Use override if provided
        if override is not None:
            try:
                value = float(override)
            except (ValueError, TypeError):
                pass
        
        # Apply factor if provided
        if factor is not None:
            try:
                value = value * float(factor)
            except (ValueError, TypeError):
                pass
        
        # Apply min/max constraints
        if min_value is not None:
            value = max(float(min_value), value)
        if max_value is not None:
            value = min(float(max_value), value)
        
        # Apply rounding
        if round_mode == "round":
            value = round(value, precision)
        elif round_mode == "floor":
            if precision == 0:
                value = math.floor(value)
            else:
                factor = 10 ** precision
                value = math.floor(value * factor) / factor
        elif round_mode == "ceil":
            if precision == 0:
                value = math.ceil(value)
            else:
                factor = 10 ** precision
                value = math.ceil(value * factor) / factor
        
        # Check if integer
        is_integer = value == int(value)
        
        # Check if positive
        is_positive = value > 0
        
        # Convert to int if it's a whole number
        if is_integer:
            value = int(value)
        
        return {
            "number": value,
            "is_integer": is_integer,
            "is_positive": is_positive
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        try:
            value = float(config.get("value", 0))
        except (ValueError, TypeError):
            return "Value must be a number"
        
        # Validate min/max
        min_value = config.get("min")
        max_value = config.get("max")
        
        if min_value is not None:
            try:
                min_value = float(min_value)
            except (ValueError, TypeError):
                return "Minimum must be a number"
        
        if max_value is not None:
            try:
                max_value = float(max_value)
            except (ValueError, TypeError):
                return "Maximum must be a number"
        
        if min_value is not None and max_value is not None and min_value > max_value:
            return "Minimum cannot be greater than maximum"
        
        # Validate precision
        try:
            precision = int(config.get("precision", 2))
            if precision < 0:
                return "Precision must be a non-negative integer"
        except (ValueError, TypeError):
            return "Precision must be a number"
        
        return None
