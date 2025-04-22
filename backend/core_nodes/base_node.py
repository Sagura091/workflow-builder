from typing import Dict, Any, Optional, List, Union
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class BaseNode:
    """
    Base class for all core nodes.

    Core nodes are always available in the workflow builder and provide
    essential functionality for building workflows.
    """

    def __init__(self):
        """Initialize the node."""
        # Default attributes that can be overridden by subclasses
        self.id = ""
        self.name = ""
        self.category = ""
        self.description = ""
        self.inputs = []
        self.outputs = []
        self.ui_properties = {}

        # Try to get metadata from the get_metadata method if implemented
        try:
            self.__plugin_meta__ = self.get_metadata()
        except NotImplementedError:
            # If get_metadata is not implemented, create metadata from attributes
            self.__plugin_meta__ = self._create_metadata_from_attributes()

    def _create_metadata_from_attributes(self) -> PluginMetadata:
        """Create metadata from instance attributes."""
        # Convert inputs to PortDefinition objects
        inputs = []
        for input_def in self.inputs:
            if isinstance(input_def, dict):
                inputs.append(PortDefinition(
                    id=input_def.get("id", ""),
                    name=input_def.get("name", ""),
                    type=input_def.get("type", "any"),
                    description=input_def.get("description", ""),
                    required=input_def.get("required", False),
                    ui_properties=input_def.get("ui_properties", {})
                ))
            else:
                inputs.append(input_def)

        # Convert outputs to PortDefinition objects
        outputs = []
        for output_def in self.outputs:
            if isinstance(output_def, dict):
                outputs.append(PortDefinition(
                    id=output_def.get("id", ""),
                    name=output_def.get("name", ""),
                    type=output_def.get("type", "any"),
                    description=output_def.get("description", ""),
                    ui_properties=output_def.get("ui_properties", {})
                ))
            else:
                outputs.append(output_def)

        # Try to convert category string to NodeCategory enum
        try:
            if isinstance(self.category, str):
                # Try direct lookup first
                try:
                    category = NodeCategory[self.category]
                except KeyError:
                    # Try to find a matching category by name
                    category_map = {
                        "CONTROL_FLOW": NodeCategory.CONTROL_FLOW,
                        "CONVERTERS": NodeCategory.CONVERTERS,
                        "DATA": NodeCategory.DATA,
                        "TEXT": NodeCategory.TEXT,
                        "MATH": NodeCategory.MATH,
                        "FILE_STORAGE": NodeCategory.FILE_STORAGE,
                        "WEB_API": NodeCategory.WEB_API,
                        "LOGIC": NodeCategory.LOGIC,
                        "AI_ML": NodeCategory.AI_ML,
                        "UTILITIES": NodeCategory.UTILITIES,
                        "VARIABLES": NodeCategory.VARIABLES
                    }
                    category = category_map.get(self.category, NodeCategory.UTILITIES)
            else:
                category = self.category
        except (TypeError):
            category = NodeCategory.UTILITIES

        # Create and return metadata
        return PluginMetadata(
            id=self.id,
            name=self.name,
            version="1.0.0",
            description=self.description,
            author="Workflow Builder",
            category=category,
            tags=[],
            inputs=inputs,
            outputs=outputs,
            config_fields=[],
            ui_properties=self.ui_properties
        )

    def get_metadata(self) -> PluginMetadata:
        """
        Get the metadata for this node.

        This method should be overridden by subclasses.

        Returns:
            The node metadata
        """
        raise NotImplementedError("Subclasses must implement get_metadata()")

    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node.

        This method should be overridden by subclasses.

        Args:
            config: The node configuration
            inputs: The input values

        Returns:
            The output values
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """
        Validate the node configuration.

        Args:
            config: The node configuration

        Returns:
            An error message if validation fails, None otherwise
        """
        return None
