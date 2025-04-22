from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class MathOperations(BaseNode):
    """
    A core node for performing mathematical operations.
    
    This node can perform various mathematical calculations.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.math_operations",
            name="Math Operations",
            version="1.0.0",
            description="Perform mathematical operations",
            author="Workflow Builder",
            category=NodeCategory.MATH,
            tags=["math", "arithmetic", "calculation", "core"],
            inputs=[
                PortDefinition(
                    id="a",
                    name="A",
                    type="number",
                    description="First operand",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="b",
                    name="B",
                    type="number",
                    description="Second operand",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="c",
                    name="C",
                    type="number",
                    description="Third operand (for some operations)",
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
                    type="number",
                    description="The result of the operation",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if the operation failed",
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
                    description="The mathematical operation to perform",
                    required=True,
                    default_value="add",
                    options=[
                        {"label": "Add (A + B)", "value": "add"},
                        {"label": "Subtract (A - B)", "value": "subtract"},
                        {"label": "Multiply (A * B)", "value": "multiply"},
                        {"label": "Divide (A / B)", "value": "divide"},
                        {"label": "Power (A ^ B)", "value": "power"},
                        {"label": "Modulo (A % B)", "value": "modulo"},
                        {"label": "Square Root (√A)", "value": "sqrt"},
                        {"label": "Absolute (|A|)", "value": "abs"},
                        {"label": "Round", "value": "round"},
                        {"label": "Floor", "value": "floor"},
                        {"label": "Ceiling", "value": "ceil"},
                        {"label": "Sine (sin A)", "value": "sin"},
                        {"label": "Cosine (cos A)", "value": "cos"},
                        {"label": "Tangent (tan A)", "value": "tan"},
                        {"label": "Minimum (min(A, B))", "value": "min"},
                        {"label": "Maximum (max(A, B))", "value": "max"},
                        {"label": "Average ((A + B) / 2)", "value": "average"},
                        {"label": "Random (between A and B)", "value": "random"},
                        {"label": "Linear Interpolation", "value": "lerp"}
                    ]
                ),
                ConfigField(
                    id="default_b",
                    name="Default B",
                    type="number",
                    description="Default value for B if not provided",
                    required=False,
                    default_value=0
                ),
                ConfigField(
                    id="default_c",
                    name="Default C",
                    type="number",
                    description="Default value for C if not provided",
                    required=False,
                    default_value=0
                ),
                ConfigField(
                    id="precision",
                    name="Precision",
                    type="number",
                    description="Number of decimal places in the result",
                    required=False,
                    default_value=2
                ),
                ConfigField(
                    id="radians",
                    name="Use Radians",
                    type="boolean",
                    description="Whether to use radians instead of degrees for trigonometric functions",
                    required=False,
                    default_value=False
                )
            ],
            ui_properties={
                "color": "#9b59b6",
                "icon": "calculator",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the math operations node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The result of the operation
        """
        import math
        import random
        
        # Get inputs
        a = inputs.get("a")
        b = inputs.get("b")
        c = inputs.get("c")
        
        # Get configuration
        operation = config.get("operation", "add")
        default_b = config.get("default_b", 0)
        default_c = config.get("default_c", 0)
        precision = int(config.get("precision", 2))
        use_radians = config.get("radians", False)
        
        # Use default values if inputs are not provided
        if a is None:
            return {
                "result": None,
                "error": "Input A is required"
            }
        
        if b is None:
            b = default_b
        
        if c is None:
            c = default_c
        
        # Convert inputs to numbers
        try:
            a = float(a)
            b = float(b)
            c = float(c)
        except (ValueError, TypeError):
            return {
                "result": None,
                "error": "Inputs must be numbers"
            }
        
        # Perform the operation
        result = None
        error = None
        
        try:
            if operation == "add":
                result = a + b
            
            elif operation == "subtract":
                result = a - b
            
            elif operation == "multiply":
                result = a * b
            
            elif operation == "divide":
                if b == 0:
                    error = "Division by zero"
                else:
                    result = a / b
            
            elif operation == "power":
                result = a ** b
            
            elif operation == "modulo":
                if b == 0:
                    error = "Modulo by zero"
                else:
                    result = a % b
            
            elif operation == "sqrt":
                if a < 0:
                    error = "Cannot take square root of negative number"
                else:
                    result = math.sqrt(a)
            
            elif operation == "abs":
                result = abs(a)
            
            elif operation == "round":
                result = round(a, int(b))
            
            elif operation == "floor":
                result = math.floor(a)
            
            elif operation == "ceil":
                result = math.ceil(a)
            
            elif operation == "sin":
                if not use_radians:
                    a = math.radians(a)
                result = math.sin(a)
            
            elif operation == "cos":
                if not use_radians:
                    a = math.radians(a)
                result = math.cos(a)
            
            elif operation == "tan":
                if not use_radians:
                    a = math.radians(a)
                result = math.tan(a)
            
            elif operation == "min":
                result = min(a, b)
            
            elif operation == "max":
                result = max(a, b)
            
            elif operation == "average":
                result = (a + b) / 2
            
            elif operation == "random":
                min_val = min(a, b)
                max_val = max(a, b)
                result = random.uniform(min_val, max_val)
            
            elif operation == "lerp":
                # Linear interpolation: a + (b - a) * c
                # a = start value, b = end value, c = interpolation factor (0-1)
                result = a + (b - a) * c
            
            else:
                error = f"Unknown operation: {operation}"
        
        except Exception as e:
            error = str(e)
        
        # Round the result to the specified precision
        if result is not None:
            try:
                result = round(result, precision)
                # Convert to int if it's a whole number
                if result == int(result):
                    result = int(result)
            except:
                pass
        
        return {
            "result": result,
            "error": error
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        operation = config.get("operation", "")
        if not operation:
            return "Operation is required"
        
        try:
            precision = int(config.get("precision", 2))
            if precision < 0:
                return "Precision must be a non-negative integer"
        except ValueError:
            return "Precision must be a number"
        
        return None
