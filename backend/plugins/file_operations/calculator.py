# backend/plugins/calculator.py
from plugins.base_plugin import BasePlugin

class CalculatorPlugin(BasePlugin):
    """
    Performs basic arithmetic operations
    """

    __plugin_meta__ = {
        "name": "Calculator",
        "category": "Math",
        "description": "Performs basic arithmetic operations",
        "editable": True,
        "generated": False,
        "inputs": {
            "a": "number",
            "b": "number"
        },
        "outputs": {
            "result": "number"
        },
        "configFields": [
            {"name": "operator", "type": "select", "options": ["+", "-", "*", "/"], "label": "Operator"}
        ]
    }

    @classmethod
    def run(cls, inputs, config):
        a = float(inputs.get("a", 0))
        b = float(inputs.get("b", 0))
        op = config.get("operator", "+")

        result = {
            "+": a + b,
            "-": a - b,
            "*": a * b,
            "/": a / b if b != 0 else None
        }.get(op, None)

        return {"result": result}

    @classmethod
    def generate_code(cls, config):
        return f"result = a {config.get('operator', '+')} b"
