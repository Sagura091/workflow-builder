"""
Boolean Converter Node

This node converts various data types to booleans.
"""

from typing import Dict, Any, Optional
from backend.core_nodes.base_node import BaseNode
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class BooleanConverter(BaseNode):
    """
    Converts various data types to booleans.
    """

    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.boolean_converter",
            name="Boolean Converter",
            version="1.0.0",
            description="Converts various data types to booleans",
            author="Workflow Builder",
            category=NodeCategory.CONVERTERS,
            tags=["boolean", "convert", "type", "core"],
            inputs=[
                PortDefinition(
                    id="input",
                    name="Input",
                    type="any",
                    description="Value to convert to boolean",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="default",
                    name="Default",
                    type="boolean",
                    description="Default value if conversion fails",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="boolean",
                    name="Boolean",
                    type="boolean",
                    description="Converted boolean value",
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
                "color": "#e74c3c",
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
        default_value = inputs.get("default", False)

        try:
            # Handle different types
            if input_value is None:
                result = False
            elif isinstance(input_value, bool):
                result = input_value
            elif isinstance(input_value, (int, float)):
                result = bool(input_value)
            elif isinstance(input_value, str):
                # Handle common string representations of booleans
                lower_str = input_value.lower().strip()
                if lower_str in ("true", "yes", "y", "1", "t"):
                    result = True
                elif lower_str in ("false", "no", "n", "0", "f"):
                    result = False
                else:
                    # Non-empty string is True, empty string is False
                    result = bool(input_value)
            elif isinstance(input_value, (list, tuple, dict)):
                # Non-empty collections are True, empty collections are False
                result = bool(input_value)
            else:
                # Default behavior for other types
                result = bool(input_value)

            return {
                "boolean": result,
                "success": True,
                "error": ""
            }
        except Exception as e:
            return {
                "boolean": default_value,
                "success": False,
                "error": str(e)
            }
