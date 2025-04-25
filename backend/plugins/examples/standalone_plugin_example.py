"""
Standalone Plugin Example

This is an example plugin that demonstrates the standalone plugin capabilities.
"""

from typing import Dict, Any, ClassVar, List
from backend.plugins.pdk import StandalonePluginBase, PluginMetadata, PortDefinition, ConfigField

class StandalonePluginExample(StandalonePluginBase):
    """
    Example plugin that demonstrates standalone execution capabilities.
    
    This plugin can be executed independently without requiring begin and end nodes
    from the core system.
    """
    
    # Plugin metadata
    __plugin_meta__ = PluginMetadata(
        id="examples.standalone_plugin_example",
        name="Standalone Plugin Example",
        version="1.0.0",
        description="Example plugin that demonstrates standalone execution capabilities",
        author="Workflow Builder Team",
        category="examples",
        tags=["example", "standalone", "plugin"],
        inputs=[
            PortDefinition(
                id="text",
                name="Text",
                type="string",
                description="Text to process",
                required=True
            ),
            PortDefinition(
                id="count",
                name="Count",
                type="number",
                description="Number of times to repeat the text",
                required=False
            )
        ],
        outputs=[
            PortDefinition(
                id="result",
                name="Result",
                type="string",
                description="Processed text",
                required=True
            ),
            PortDefinition(
                id="length",
                name="Length",
                type="number",
                description="Length of the processed text",
                required=True
            )
        ],
        config_fields=[
            ConfigField(
                id="prefix",
                name="Prefix",
                type="string",
                description="Prefix to add to the text",
                required=False,
                default_value=""
            ),
            ConfigField(
                id="suffix",
                name="Suffix",
                type="string",
                description="Suffix to add to the text",
                required=False,
                default_value=""
            ),
            ConfigField(
                id="uppercase",
                name="Uppercase",
                type="boolean",
                description="Convert text to uppercase",
                required=False,
                default_value=False
            )
        ]
    )
    
    # Plugin version
    __plugin_version__: ClassVar[str] = "1.0.0"
    
    # Plugin dependencies
    __plugin_dependencies__: ClassVar[List[str]] = []
    
    # Plugin author
    __plugin_author__: ClassVar[str] = "Workflow Builder Team"
    
    # Plugin license
    __plugin_license__: ClassVar[str] = "MIT"
    
    # Standalone execution flag
    __standalone_capable__: ClassVar[bool] = True
    
    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plugin.
        
        Args:
            inputs: Dictionary of input values
            config: Dictionary of configuration values
            
        Returns:
            Dictionary of output values
        """
        # Get inputs
        text = inputs.get("text", "")
        count = inputs.get("count", 1)
        
        # Get config
        prefix = config.get("prefix", "")
        suffix = config.get("suffix", "")
        uppercase = config.get("uppercase", False)
        
        # Process text
        result = text * int(count)
        
        # Apply prefix and suffix
        result = f"{prefix}{result}{suffix}"
        
        # Apply uppercase
        if uppercase:
            result = result.upper()
        
        # Return outputs
        return {
            "result": result,
            "length": len(result)
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize plugin configuration.
        
        Args:
            config: Dictionary of configuration values
            
        Returns:
            Validated and normalized configuration
        """
        # Ensure prefix and suffix are strings
        if "prefix" in config and not isinstance(config["prefix"], str):
            config["prefix"] = str(config["prefix"])
        
        if "suffix" in config and not isinstance(config["suffix"], str):
            config["suffix"] = str(config["suffix"])
        
        # Ensure uppercase is a boolean
        if "uppercase" in config and not isinstance(config["uppercase"], bool):
            config["uppercase"] = bool(config["uppercase"])
        
        return config
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize plugin inputs.
        
        Args:
            inputs: Dictionary of input values
            
        Returns:
            Validated and normalized inputs
        """
        # Ensure text is a string
        if "text" in inputs and not isinstance(inputs["text"], str):
            inputs["text"] = str(inputs["text"])
        
        # Ensure count is a number
        if "count" in inputs:
            try:
                inputs["count"] = int(inputs["count"])
            except (ValueError, TypeError):
                inputs["count"] = 1
        
        return inputs


# Example usage
if __name__ == "__main__":
    from backend.plugins.pdk.execution import PluginExecutor
    
    # Execute the plugin from the command line
    PluginExecutor.execute_plugin_from_cli(StandalonePluginExample)
