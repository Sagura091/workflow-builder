from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class TextOutput(BaseNode):
    """
    A core node for displaying text output.
    
    This node allows users to display text results in the workflow.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.text_output",
            name="Text Output",
            version="1.0.0",
            description="Display text results",
            author="Workflow Builder",
            category=NodeCategory.TEXT,
            tags=["text", "output", "display", "core"],
            inputs=[
                PortDefinition(
                    id="text",
                    name="Text",
                    type="string",
                    description="The text to display",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="label",
                    name="Label",
                    type="string",
                    description="Label for the text (overrides config)",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="trigger",
                    name="Trigger",
                    type="trigger",
                    description="Trigger to update the display",
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
                    description="The displayed text (pass-through)",
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
                    id="display_id",
                    name="Display ID",
                    type="string",
                    description="Unique ID for this display",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="label",
                    name="Label",
                    type="string",
                    description="Label for the text",
                    required=False,
                    default_value="Output"
                ),
                ConfigField(
                    id="format",
                    name="Format",
                    type="select",
                    description="Format for displaying the text",
                    required=False,
                    default_value="plain",
                    options=[
                        {"label": "Plain Text", "value": "plain"},
                        {"label": "Markdown", "value": "markdown"},
                        {"label": "HTML", "value": "html"},
                        {"label": "JSON", "value": "json"},
                        {"label": "Code", "value": "code"}
                    ]
                ),
                ConfigField(
                    id="max_length",
                    name="Max Length",
                    type="number",
                    description="Maximum length to display (0 for no limit)",
                    required=False,
                    default_value=0
                ),
                ConfigField(
                    id="truncate_indicator",
                    name="Truncate Indicator",
                    type="string",
                    description="Text to show when truncated",
                    required=False,
                    default_value="..."
                ),
                ConfigField(
                    id="code_language",
                    name="Code Language",
                    type="string",
                    description="Language for code highlighting",
                    required=False,
                    default_value="javascript"
                )
            ],
            ui_properties={
                "color": "#e74c3c",
                "icon": "comment",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the text output node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The text output
        """
        import uuid
        import json
        
        # Get inputs
        text = inputs.get("text", "")
        input_label = inputs.get("label")
        trigger = inputs.get("trigger", False)
        
        # Get configuration
        config_label = config.get("label", "Output")
        format_type = config.get("format", "plain")
        max_length = int(config.get("max_length", 0))
        truncate_indicator = config.get("truncate_indicator", "...")
        code_language = config.get("code_language", "javascript")
        
        # Use input label if provided, otherwise use config
        label = input_label if input_label is not None else config_label
        
        # Convert text to string if it's not already
        if not isinstance(text, str):
            if format_type == "json" and (isinstance(text, dict) or isinstance(text, list)):
                # Format as JSON
                try:
                    text = json.dumps(text, indent=2)
                except:
                    text = str(text)
            else:
                text = str(text)
        
        # Truncate if needed
        original_length = len(text)
        if max_length > 0 and original_length > max_length:
            text = text[:max_length] + truncate_indicator
        
        # Generate a unique ID for this display
        display_id = str(uuid.uuid4())
        
        # In a real implementation, this would send the text to the UI
        # For now, we just print it
        print(f"[{label}] ({format_type}):")
        print(text)
        
        return {
            "text": text,
            "length": original_length,
            "display_id": display_id
        }
