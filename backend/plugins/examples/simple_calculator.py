"""
Simple Calculator Plugin

This plugin demonstrates a simple calculator that performs basic math operations.
"""

from backend.plugins.base_plugin import BasePlugin

class SimpleCalculator(BasePlugin):
    """
    A simple calculator plugin that performs basic math operations.
    """

    __plugin_meta__ = {
        "name": "Simple Calculator",
        "category": "MATH",
        "description": "Performs basic math operations",
        "editable": True,
        "inputs": {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"}
        },
        "outputs": {
            "result": {"type": "number", "description": "Calculation result"},
            "operation_text": {"type": "string", "description": "Text representation of the operation"}
        },
        "configFields": [
            {
                "name": "operation",
                "type": "select",
                "label": "Operation",
                "options": [
                    {"label": "Add", "value": "add"},
                    {"label": "Subtract", "value": "subtract"},
                    {"label": "Multiply", "value": "multiply"},
                    {"label": "Divide", "value": "divide"}
                ],
                "default": "add"
            },
            {
                "name": "round_result",
                "type": "boolean",
                "label": "Round Result",
                "default": False
            },
            {
                "name": "decimal_places",
                "type": "number",
                "label": "Decimal Places",
                "default": 2
            }
        ]
    }

    @classmethod
    def run(cls, inputs, config):
        """
        Execute the plugin with the given inputs and configuration.

        Args:
            inputs (dict): Input values from connected nodes
            config (dict): Configuration values set by the user

        Returns:
            dict: Output values to be passed to connected nodes
        """
        a = inputs.get("a", 0)
        b = inputs.get("b", 0)
        operation = config.get("operation", "add")
        round_result = config.get("round_result", False)
        decimal_places = config.get("decimal_places", 2)

        # Perform the operation
        if operation == "add":
            result = a + b
            operation_text = f"{a} + {b} = {result}"
        elif operation == "subtract":
            result = a - b
            operation_text = f"{a} - {b} = {result}"
        elif operation == "multiply":
            result = a * b
            operation_text = f"{a} × {b} = {result}"
        elif operation == "divide":
            if b == 0:
                return {
                    "result": "Error",
                    "operation_text": f"{a} ÷ {b} = Error: Division by zero"
                }
            result = a / b
            operation_text = f"{a} ÷ {b} = {result}"
        else:
            return {
                "result": "Error",
                "operation_text": f"Unknown operation: {operation}"
            }

        # Round the result if configured
        if round_result and isinstance(result, (int, float)):
            result = round(result, decimal_places)
            operation_text = operation_text.split("=")[0] + f"= {result}"

        return {
            "result": result,
            "operation_text": operation_text
        }

    @classmethod
    def generate_code(cls, config):
        """
        Generate code for the plugin.

        Args:
            config (dict): Configuration values set by the user

        Returns:
            str: Generated code
        """
        operation = config.get("operation", "add")
        round_result = config.get("round_result", False)
        decimal_places = config.get("decimal_places", 2)

        operation_symbol = {
            "add": "+",
            "subtract": "-",
            "multiply": "*",
            "divide": "/"
        }.get(operation, "+")

        code = [
            "# Simple Calculator",
            "def calculate(a, b):",
            f"    # Perform {operation} operation",
            f"    result = a {operation_symbol} b"
        ]

        if operation == "divide":
            code.insert(2, "    # Check for division by zero")
            code.insert(3, "    if b == 0:")
            code.insert(4, "        return 'Error: Division by zero'")

        if round_result:
            code.append(f"    # Round the result to {decimal_places} decimal places")
            code.append(f"    result = round(result, {decimal_places})")

        code.append("    return result")

        return "\n".join(code)
