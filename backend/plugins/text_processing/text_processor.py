from typing import Dict, Any
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class TextProcessor:
    """
    A plugin for processing text data.
    
    This plugin can perform various text operations like uppercase, lowercase,
    and counting characters.
    """
    
    def __init__(self):
        self.__plugin_meta__ = PluginMetadata(
            id="text_processor",
            name="Text Processor",
            version="1.0.0",
            description="Process text with various operations",
            author="Workflow Builder",
            category=NodeCategory.PROCESSING,
            tags=["text", "string", "processing"],
            inputs=[
                PortDefinition(
                    id="text",
                    name="Text",
                    type="string",
                    description="The text to process",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="result",
                    name="Result",
                    type="string",
                    description="The processed text",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="character_count",
                    name="Character Count",
                    type="number",
                    description="The number of characters in the text",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="operation",
                    name="Operation",
                    type="select",
                    description="The operation to perform on the text",
                    required=True,
                    default_value="uppercase",
                    options=[
                        {"label": "Uppercase", "value": "uppercase"},
                        {"label": "Lowercase", "value": "lowercase"},
                        {"label": "Capitalize", "value": "capitalize"},
                        {"label": "Reverse", "value": "reverse"},
                        {"label": "Trim", "value": "trim"}
                    ]
                ),
                ConfigField(
                    id="prefix",
                    name="Prefix",
                    type="text",
                    description="Text to add before the result",
                    required=False,
                    default_value=""
                ),
                ConfigField(
                    id="suffix",
                    name="Suffix",
                    type="text",
                    description="Text to add after the result",
                    required=False,
                    default_value=""
                )
            ],
            ui_properties={
                "color": "#3498db",
                "icon": "font",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the text processing operation.
        
        Args:
            config: The plugin configuration
            inputs: The input values
            
        Returns:
            The processed text and character count
        """
        # Get input text
        text = inputs.get("text", "")
        if not isinstance(text, str):
            text = str(text)
        
        # Get configuration
        operation = config.get("operation", "uppercase")
        prefix = config.get("prefix", "")
        suffix = config.get("suffix", "")
        
        # Process text
        if operation == "uppercase":
            result = text.upper()
        elif operation == "lowercase":
            result = text.lower()
        elif operation == "capitalize":
            result = text.capitalize()
        elif operation == "reverse":
            result = text[::-1]
        elif operation == "trim":
            result = text.strip()
        else:
            result = text
        
        # Add prefix and suffix
        result = f"{prefix}{result}{suffix}"
        
        # Return result
        return {
            "result": result,
            "character_count": len(result)
        }
