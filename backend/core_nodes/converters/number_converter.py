"""
Number Converter Node

This node converts various data types to numbers.
"""

from typing import Dict, Any, Optional
from backend.core_nodes.base_node import BaseNode
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class NumberConverter(BaseNode):
    """
    Converts various data types to numbers.
    """

    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.number_converter",
            name="Number Converter",
            version="1.0.0",
            description="Converts various data types to numbers",
            author="Workflow Builder",
            category=NodeCategory.CONVERTERS,
            tags=["number", "convert", "type", "core"],
            inputs=[
                PortDefinition(
                    id="input",
                    name="Input",
                    type="any",
                    description="Value to convert to number",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="default",
                    name="Default",
                    type="number",
                    description="Default value if conversion fails",
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
                    description="Converted number value",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="integer",
                    name="Integer",
                    type="number",
                    description="Converted value as integer",
                    ui_properties={
                        "position": "right-center-top"
                    }
                ),
                PortDefinition(
                    id="float",
                    name="Float",
                    type="number",
                    description="Converted value as float",
                    ui_properties={
                        "position": "right-center-bottom"
                    }
                ),
                PortDefinition(
                    id="success",
                    name="Success",
                    type="boolean",
                    description="Whether the conversion was successful",
                    ui_properties={
                        "position": "right-bottom"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if conversion failed",
                    ui_properties={
                        "position": "right-bottom-extra"
                    }
                )
            ],
            config_fields=[],
            ui_properties={
                "color": "#9b59b6",
                "icon": "exchange-alt",
                "width": 240
            }
        )

    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node.

        Args:
            config: The node configuration
            inputs: The input values

        Returns:
            The output values
        """
        input_value = inputs.get("input")
        default_value = inputs.get("default", 0)

        try:
            # Handle different types
            if input_value is None:
                raise ValueError("Cannot convert None to number")
            elif isinstance(input_value, (int, float)):
                number = float(input_value)
            elif isinstance(input_value, str):
                # Try to convert string to number
                if input_value.strip() == "":
                    raise ValueError("Cannot convert empty string to number")

                # Handle percentage strings
                if input_value.strip().endswith("%"):
                    number = float(input_value.strip()[:-1]) / 100
                else:
                    number = float(input_value)
            elif isinstance(input_value, bool):
                number = 1 if input_value else 0
            elif isinstance(input_value, (list, tuple)) and len(input_value) > 0:
                # Take the first element if it's a list or tuple
                number = float(input_value[0])
            else:
                raise ValueError(f"Cannot convert {type(input_value).__name__} to number")

            return {
                "number": number,
                "integer": int(number),
                "float": float(number),
                "success": True,
                "error": ""
            }
        except Exception as e:
            return {
                "number": default_value,
                "integer": int(default_value),
                "float": float(default_value),
                "success": False,
                "error": str(e)
            }
