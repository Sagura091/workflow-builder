from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class TextTemplate(BaseNode):
    """
    A core node for creating text from templates.
    
    This node allows users to create text using templates with variables.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.text_template",
            name="Text Template",
            version="1.0.0",
            description="Create text from templates",
            author="Workflow Builder",
            category=NodeCategory.TEXT,
            tags=["text", "template", "format", "core"],
            inputs=[
                PortDefinition(
                    id="variables",
                    name="Variables",
                    type="object",
                    description="Variables to use in the template",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="template",
                    name="Template",
                    type="string",
                    description="Template text (overrides config)",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="fallback",
                    name="Fallback",
                    type="string",
                    description="Fallback text if template fails",
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
                    description="The generated text",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="success",
                    name="Success",
                    type="boolean",
                    description="Whether the template was applied successfully",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if template failed",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="template",
                    name="Template",
                    type="text",
                    description="The template text with {variable} placeholders",
                    required=True,
                    default_value="Hello, {name}!"
                ),
                ConfigField(
                    id="template_engine",
                    name="Template Engine",
                    type="select",
                    description="The template engine to use",
                    required=False,
                    default_value="simple",
                    options=[
                        {"label": "Simple ({})", "value": "simple"},
                        {"label": "Format String", "value": "format"},
                        {"label": "Template String", "value": "template"}
                    ]
                ),
                ConfigField(
                    id="missing_var_behavior",
                    name="Missing Variable Behavior",
                    type="select",
                    description="What to do when a variable is missing",
                    required=False,
                    default_value="keep",
                    options=[
                        {"label": "Keep Placeholder", "value": "keep"},
                        {"label": "Replace with Empty", "value": "empty"},
                        {"label": "Replace with Default", "value": "default"},
                        {"label": "Fail", "value": "fail"}
                    ]
                ),
                ConfigField(
                    id="default_value",
                    name="Default Value",
                    type="string",
                    description="Default value for missing variables",
                    required=False,
                    default_value="[missing]"
                )
            ],
            ui_properties={
                "color": "#9b59b6",
                "icon": "file-alt",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the text template node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The generated text
        """
        import string
        
        # Get inputs
        variables = inputs.get("variables", {})
        input_template = inputs.get("template")
        fallback = inputs.get("fallback", "")
        
        # Get configuration
        config_template = config.get("template", "Hello, {name}!")
        template_engine = config.get("template_engine", "simple")
        missing_var_behavior = config.get("missing_var_behavior", "keep")
        default_value = config.get("default_value", "[missing]")
        
        # Use input template if provided, otherwise use config
        template_text = input_template if input_template is not None else config_template
        
        # Initialize outputs
        text = template_text
        success = True
        error = None
        
        try:
            # Convert variables to strings
            str_variables = {}
            for key, value in variables.items():
                str_variables[key] = str(value) if value is not None else ""
            
            # Apply template based on engine
            if template_engine == "simple":
                # Simple template replacement
                text = template_text
                for key, value in str_variables.items():
                    placeholder = "{" + key + "}"
                    if placeholder in text:
                        text = text.replace(placeholder, value)
                    elif missing_var_behavior == "fail":
                        raise ValueError(f"Missing variable: {key}")
            
            elif template_engine == "format":
                # Python string format
                try:
                    text = template_text.format(**str_variables)
                except KeyError as e:
                    if missing_var_behavior == "fail":
                        raise
                    elif missing_var_behavior == "empty":
                        # Create a dict with empty strings for missing keys
                        format_vars = {key: "" for key in e.args}
                        format_vars.update(str_variables)
                        text = template_text.format(**format_vars)
                    elif missing_var_behavior == "default":
                        # Create a dict with default value for missing keys
                        format_vars = {key: default_value for key in e.args}
                        format_vars.update(str_variables)
                        text = template_text.format(**format_vars)
                    else:  # keep
                        # We can't easily keep the placeholders with format strings
                        # So we'll fall back to simple replacement
                        text = template_text
                        for key, value in str_variables.items():
                            placeholder = "{" + key + "}"
                            text = text.replace(placeholder, value)
            
            elif template_engine == "template":
                # Python string.Template
                template = string.Template(template_text)
                
                if missing_var_behavior == "fail":
                    text = template.substitute(str_variables)
                elif missing_var_behavior == "empty":
                    # Create a safe_substitute with empty strings for missing keys
                    text = template.safe_substitute(str_variables)
                    # Replace any remaining $var or ${var} with empty string
                    import re
                    text = re.sub(r'\$\w+|\$\{\w+\}', '', text)
                elif missing_var_behavior == "default":
                    # Create a safe_substitute with default value for missing keys
                    text = template.safe_substitute(str_variables)
                    # Replace any remaining $var or ${var} with default value
                    import re
                    text = re.sub(r'\$\w+|\$\{\w+\}', default_value, text)
                else:  # keep
                    text = template.safe_substitute(str_variables)
            
            else:
                error = f"Unknown template engine: {template_engine}"
                success = False
                text = fallback if fallback else template_text
        
        except Exception as e:
            error = str(e)
            success = False
            text = fallback if fallback else template_text
        
        return {
            "text": text,
            "success": success,
            "error": error
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        template = config.get("template", "")
        if not template:
            return "Template is required"
        
        template_engine = config.get("template_engine", "")
        if template_engine not in ["simple", "format", "template"]:
            return "Invalid template engine"
        
        missing_var_behavior = config.get("missing_var_behavior", "")
        if missing_var_behavior not in ["keep", "empty", "default", "fail"]:
            return "Invalid missing variable behavior"
        
        return None
