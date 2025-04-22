"""
Array Converter Node

This node converts various data types to arrays.
"""

from typing import Dict, Any, Optional
from backend.core_nodes.base_node import BaseNode
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class ArrayConverter(BaseNode):
    """
    Converts various data types to arrays.
    """

    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.array_converter",
            name="Array Converter",
            version="1.0.0",
            description="Converts various data types to arrays",
            author="Workflow Builder",
            category=NodeCategory.CONVERTERS,
            tags=["array", "convert", "type", "core"],
            inputs=[
                PortDefinition(
                    id="input",
                    name="Input",
                    type="any",
                    description="Value to convert to array",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="delimiter",
                    name="Delimiter",
                    type="string",
                    description="Delimiter for splitting strings (default: comma)",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="array",
                    name="Array",
                    type="array",
                    description="Converted array value",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="length",
                    name="Length",
                    type="number",
                    description="Length of the array",
                    ui_properties={
                        "position": "right-center"
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
                "color": "#f1c40f",
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
        delimiter = inputs.get("delimiter", ",")

        try:
            # Handle different types
            if input_value is None:
                result = []
            elif isinstance(input_value, (list, tuple)):
                result = list(input_value)
            elif isinstance(input_value, str):
                # Split string by delimiter
                result = [item.strip() for item in input_value.split(delimiter)]
            elif isinstance(input_value, dict):
                # Convert dict to array of key-value pairs
                result = [[key, value] for key, value in input_value.items()]
            else:
                # Wrap single value in array
                result = [input_value]

            return {
                "array": result,
                "length": len(result),
                "success": True,
                "error": ""
            }
        except Exception as e:
            return {
                "array": [],
                "length": 0,
                "success": False,
                "error": str(e)
            }
