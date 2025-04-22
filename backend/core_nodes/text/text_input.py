from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class TextInput(BaseNode):
    """
    A core node for providing text input.
    
    This node allows users to enter text manually or use a template.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.text_input",
            name="Text Input",
            version="1.0.0",
            description="Enter text manually",
            author="Workflow Builder",
            category=NodeCategory.TEXT,
            tags=["text", "input", "string", "core"],
            inputs=[
                PortDefinition(
                    id="variables",
                    name="Variables",
                    type="object",
                    description="Variables to use in the template",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="override",
                    name="Override",
                    type="string",
                    description="Text to override the configured text",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="text",
                    name="Text",
                    type="string",
                    description="The output text",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="length",
                    name="Length",
                    type="number",
                    description="The length of the text",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="is_empty",
                    name="Is Empty",
                    type="boolean",
                    description="Whether the text is empty",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="text",
                    name="Text",
                    type="text",
                    description="The text to output",
                    required=False,
                    default_value=""
                ),
                ConfigField(
                    id="use_template",
                    name="Use Template",
                    type="boolean",
                    description="Whether to use template variables",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="trim",
                    name="Trim Whitespace",
                    type="boolean",
                    description="Whether to trim whitespace from the text",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="multiline",
                    name="Multiline",
                    type="boolean",
                    description="Whether the text can contain multiple lines",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="placeholder",
                    name="Placeholder",
                    type="string",
                    description="Placeholder text to show in the editor",
                    required=False,
                    default_value="Enter text here..."
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
        Execute the text input node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The text output
        """
        # Get inputs
        variables = inputs.get("variables", {})
        override = inputs.get("override")
        
        # Get configuration
        text = config.get("text", "")
        use_template = config.get("use_template", False)
        trim = config.get("trim", True)
        
        # Use override if provided
        if override is not None:
            text = str(override)
        
        # Apply template if enabled
        if use_template and variables:
            try:
                # Simple template replacement using format
                # Convert variables to strings
                str_variables = {}
                for key, value in variables.items():
                    str_variables[key] = str(value) if value is not None else ""
                
                # Replace {variable} placeholders
                for key, value in str_variables.items():
                    placeholder = "{" + key + "}"
                    text = text.replace(placeholder, value)
            except Exception:
                # If template fails, use original text
                pass
        
        # Trim whitespace if configured
        if trim:
            text = text.strip()
        
        # Calculate length and emptiness
        length = len(text)
        is_empty = length == 0
        
        return {
            "text": text,
            "length": length,
            "is_empty": is_empty
        }
