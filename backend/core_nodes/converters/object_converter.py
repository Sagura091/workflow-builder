"""
Object Converter Node

This node converts various data types to objects.
"""

from typing import Dict, Any, Optional
from backend.core_nodes.base_node import BaseNode
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
import json

class ObjectConverter(BaseNode):
    """
    Converts various data types to objects.
    """

    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.object_converter",
            name="Object Converter",
            version="1.0.0",
            description="Converts various data types to objects",
            author="Workflow Builder",
            category=NodeCategory.CONVERTERS,
            tags=["object", "convert", "type", "core"],
            inputs=[
                PortDefinition(
                    id="input",
                    name="Input",
                    type="any",
                    description="Value to convert to object",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="key",
                    name="Key",
                    type="string",
                    description="Key to use for non-object values",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="object",
                    name="Object",
                    type="object",
                    description="Converted object value",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="keys",
                    name="Keys",
                    type="array",
                    description="Array of object keys",
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
                "color": "#e67e22",
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
        key = inputs.get("key", "value")

        try:
            # Handle different types
            if input_value is None:
                result = {}
            elif isinstance(input_value, dict):
                result = input_value
            elif isinstance(input_value, str):
                # Try to parse as JSON
                try:
                    result = json.loads(input_value)
                    if not isinstance(result, dict):
                        result = {key: result}
                except json.JSONDecodeError:
                    # If not valid JSON, use as a simple value
                    result = {key: input_value}
            elif isinstance(input_value, (list, tuple)):
                # Convert array to object with indices as keys
                result = {str(i): value for i, value in enumerate(input_value)}
            else:
                # Wrap single value in object
                result = {key: input_value}

            return {
                "object": result,
                "keys": list(result.keys()),
                "success": True,
                "error": ""
            }
        except Exception as e:
            return {
                "object": {},
                "keys": [],
                "success": False,
                "error": str(e)
            }
