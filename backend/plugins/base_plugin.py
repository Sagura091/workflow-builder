from typing import Dict, Any, List, Optional
from backend.app.services.node_registry import NodeRegistry

class BasePlugin:
    """Base class for all plugins."""

    # Node registry instance for accessing core nodes
    _node_registry = NodeRegistry()

    @classmethod
    def get_meta(cls) -> Dict[str, Any]:
        """Get plugin metadata."""
        if not hasattr(cls, "__plugin_meta__"):
            raise NotImplementedError("Plugin must define __plugin_meta__")

        return cls.__plugin_meta__

    @classmethod
    def run(cls, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the plugin."""
        raise NotImplementedError("Plugin must implement run method")

    @classmethod
    def generate_code(cls, config: Dict[str, Any]) -> str:
        """Generate code for the plugin."""
        raise NotImplementedError("Plugin must implement generate_code method")

    @classmethod
    def get_core_node(cls, node_id: str) -> Any:
        """
        Get a core node instance by ID.

        Args:
            node_id (str): The ID of the core node (e.g., "core.text_input")

        Returns:
            object: An instance of the core node, or None if not found
        """
        node_class = cls._node_registry.get_node(node_id)
        if node_class:
            return node_class()
        return None

    @classmethod
    def execute_core_node(cls, node_id: str, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a core node with the given inputs and configuration.

        Args:
            node_id (str): The ID of the core node to execute
            inputs (dict): Input values for the core node
            config (dict): Configuration values for the core node

        Returns:
            dict: Output values from the core node, or empty dict if the node was not found
        """
        node = cls.get_core_node(node_id)
        if node and hasattr(node, 'execute'):
            return node.execute(inputs, config)
        return {}

    @staticmethod
    def create_plugin_template(
        name: str,
        category: str,
        description: str,
        inputs: Dict[str, str],
        outputs: Dict[str, str],
        config_fields: List[Dict[str, Any]] = None
    ) -> str:
        """Create a plugin template."""
        if config_fields is None:
            config_fields = []

        template = f'''from plugins.base_plugin import BasePlugin

class {name.replace(" ", "")}Plugin(BasePlugin):
    """
    {description}
    """

    __plugin_meta__ = {{
        "name": "{name}",
        "category": "{category}",
        "description": "{description}",
        "editable": True,
        "generated": True,
        "inputs": {inputs},
        "outputs": {outputs},
        "configFields": {config_fields}
    }}

    @classmethod
    def run(cls, inputs, config):
        """Run the plugin."""
        # TODO: Implement plugin logic
        result = {{}}

        # Process inputs
        {cls._generate_input_processing(inputs)}

        # TODO: Add your processing logic here

        # Return outputs
        {cls._generate_output_processing(outputs)}

        return result

    @classmethod
    def generate_code(cls, config):
        """Generate code for the plugin."""
        # TODO: Implement code generation
        return "# Generated code for {name}"
'''

        return template

    @staticmethod
    def _generate_input_processing(inputs: Dict[str, str]) -> str:
        """Generate code for processing inputs."""
        if not inputs:
            return "# No inputs to process"

        lines = []
        for input_name, input_type in inputs.items():
            lines.append(f"{input_name} = inputs.get('{input_name}')")

            # Add type checking based on input type
            if input_type == "number":
                lines.append(f"if {input_name} is not None:")
                lines.append(f"    {input_name} = float({input_name})")

        return "\n".join(lines)

    @staticmethod
    def _generate_output_processing(outputs: Dict[str, str]) -> str:
        """Generate code for processing outputs."""
        if not outputs:
            return "# No outputs to process"

        lines = []
        for output_name, output_type in outputs.items():
            lines.append(f"# TODO: Set {output_name} value")
            lines.append(f"result['{output_name}'] = None  # Replace with actual value")

        return "\n".join(lines)
