"""
String Converter Node

This node converts various data types to strings.
"""

from typing import Dict, Any, Optional
from backend.core_nodes.base_node import BaseNode
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class StringConverter(BaseNode):
    """
    Converts various data types to strings.
    """

    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.string_converter",
            name="String Converter",
            version="1.0.0",
            description="Converts various data types to strings",
            author="Workflow Builder",
            category=NodeCategory.CONVERTERS,
            tags=["string", "convert", "type", "core"],
            inputs=[
                PortDefinition(
                    id="input",
                    name="Input",
                    type="any",
                    description="Value to convert to string",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="format",
                    name="Format",
                    type="string",
                    description="Optional format string (for numbers, dates, etc.)",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="string",
                    name="String",
                    type="string",
                    description="Converted string value",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="success",
                    name="Success",
                    type="boolean",
                    description="Whether the conversion was successful",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if conversion failed",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[],
            ui_properties={
                "color": "#3498db",
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
        format_str = inputs.get("format", "")

        try:
            # Handle different types
            if input_value is None:
                result = "null"
            elif isinstance(input_value, str):
                result = input_value
            elif isinstance(input_value, (int, float)):
                if format_str:
                    try:
                        result = format_str.format(input_value)
                    except:
                        result = str(input_value)
                else:
                    result = str(input_value)
            elif isinstance(input_value, bool):
                result = str(input_value).lower()
            elif isinstance(input_value, (list, tuple)):
                result = ", ".join(str(item) for item in input_value)
            elif isinstance(input_value, dict):
                try:
                    import json
                    result = json.dumps(input_value, indent=2)
                except:
                    result = str(input_value)
            else:
                result = str(input_value)

            return {
                "string": result,
                "success": True,
                "error": ""
            }
        except Exception as e:
            return {
                "string": "",
                "success": False,
                "error": str(e)
            }
