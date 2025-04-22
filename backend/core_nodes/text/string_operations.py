from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class StringOperations(BaseNode):
    """
    A core node for performing string operations.
    
    This node can manipulate and transform strings in various ways.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.string_operations",
            name="String Operations",
            version="1.0.0",
            description="Perform string operations and transformations",
            author="Workflow Builder",
            category=NodeCategory.TEXT,
            tags=["string", "text", "manipulation", "core"],
            inputs=[
                PortDefinition(
                    id="text",
                    name="Text",
                    type="string",
                    description="The input text",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="search",
                    name="Search",
                    type="string",
                    description="Text to search for (for some operations)",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="replace",
                    name="Replace",
                    type="string",
                    description="Text to replace with (for replace operation)",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="result",
                    name="Result",
                    type="string",
                    description="The result of the operation",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="length",
                    name="Length",
                    type="number",
                    description="The length of the result",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="success",
                    name="Success",
                    type="boolean",
                    description="Whether the operation was successful",
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
                    description="The string operation to perform",
                    required=True,
                    default_value="uppercase",
                    options=[
                        {"label": "Uppercase", "value": "uppercase"},
                        {"label": "Lowercase", "value": "lowercase"},
                        {"label": "Capitalize", "value": "capitalize"},
                        {"label": "Trim", "value": "trim"},
                        {"label": "Replace", "value": "replace"},
                        {"label": "Substring", "value": "substring"},
                        {"label": "Split", "value": "split"},
                        {"label": "Join", "value": "join"},
                        {"label": "Pad Start", "value": "pad_start"},
                        {"label": "Pad End", "value": "pad_end"},
                        {"label": "Count Occurrences", "value": "count"},
                        {"label": "Reverse", "value": "reverse"},
                        {"label": "Format", "value": "format"},
                        {"label": "Encode URL", "value": "url_encode"},
                        {"label": "Decode URL", "value": "url_decode"},
                        {"label": "Base64 Encode", "value": "base64_encode"},
                        {"label": "Base64 Decode", "value": "base64_decode"}
                    ]
                ),
                ConfigField(
                    id="start_index",
                    name="Start Index",
                    type="number",
                    description="Start index for substring operation",
                    required=False,
                    default_value=0
                ),
                ConfigField(
                    id="end_index",
                    name="End Index",
                    type="number",
                    description="End index for substring operation",
                    required=False,
                    default_value=-1
                ),
                ConfigField(
                    id="delimiter",
                    name="Delimiter",
                    type="string",
                    description="Delimiter for split/join operations",
                    required=False,
                    default_value=","
                ),
                ConfigField(
                    id="pad_character",
                    name="Pad Character",
                    type="string",
                    description="Character to use for padding",
                    required=False,
                    default_value=" "
                ),
                ConfigField(
                    id="pad_length",
                    name="Pad Length",
                    type="number",
                    description="Target length for padding",
                    required=False,
                    default_value=10
                ),
                ConfigField(
                    id="case_sensitive",
                    name="Case Sensitive",
                    type="boolean",
                    description="Whether operations are case sensitive",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="format_template",
                    name="Format Template",
                    type="string",
                    description="Template for format operation (use {0}, {1}, etc. for placeholders)",
                    required=False,
                    default_value="{0}"
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
        Execute the string operations node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The result of the operation
        """
        import re
        import base64
        import urllib.parse
        
        # Get inputs
        text = inputs.get("text", "")
        search = inputs.get("search", "")
        replace = inputs.get("replace", "")
        
        # Ensure text is a string
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        
        # Get configuration
        operation = config.get("operation", "uppercase")
        start_index = int(config.get("start_index", 0))
        end_index = int(config.get("end_index", -1))
        delimiter = config.get("delimiter", ",")
        pad_character = config.get("pad_character", " ")
        pad_length = int(config.get("pad_length", 10))
        case_sensitive = config.get("case_sensitive", True)
        format_template = config.get("format_template", "{0}")
        
        # Perform the operation
        result = text
        success = True
        
        try:
            if operation == "uppercase":
                result = text.upper()
            
            elif operation == "lowercase":
                result = text.lower()
            
            elif operation == "capitalize":
                result = text.capitalize()
            
            elif operation == "trim":
                result = text.strip()
            
            elif operation == "replace":
                if case_sensitive:
                    result = text.replace(search, replace)
                else:
                    result = re.sub(re.escape(search), replace, text, flags=re.IGNORECASE)
            
            elif operation == "substring":
                if end_index < 0:
                    end_index = len(text)
                result = text[start_index:end_index]
            
            elif operation == "split":
                result = text.split(delimiter)
                # Convert to string for output
                result = str(result)
            
            elif operation == "join":
                # Assume text is a representation of a list
                try:
                    # Try to parse as a list
                    if text.startswith("[") and text.endswith("]"):
                        import ast
                        items = ast.literal_eval(text)
                        result = delimiter.join(str(item) for item in items)
                    else:
                        # Treat as comma-separated values
                        items = text.split(",")
                        result = delimiter.join(items)
                except:
                    result = text
                    success = False
            
            elif operation == "pad_start":
                result = text.rjust(pad_length, pad_character[0] if pad_character else " ")
            
            elif operation == "pad_end":
                result = text.ljust(pad_length, pad_character[0] if pad_character else " ")
            
            elif operation == "count":
                if case_sensitive:
                    result = str(text.count(search))
                else:
                    result = str(len(re.findall(re.escape(search), text, re.IGNORECASE)))
            
            elif operation == "reverse":
                result = text[::-1]
            
            elif operation == "format":
                # Use search and replace as format arguments
                args = [text]
                if search:
                    args.append(search)
                if replace:
                    args.append(replace)
                
                try:
                    result = format_template.format(*args)
                except:
                    result = format_template
                    success = False
            
            elif operation == "url_encode":
                result = urllib.parse.quote(text)
            
            elif operation == "url_decode":
                result = urllib.parse.unquote(text)
            
            elif operation == "base64_encode":
                result = base64.b64encode(text.encode()).decode()
            
            elif operation == "base64_decode":
                result = base64.b64decode(text.encode()).decode()
            
            else:
                result = text
                success = False
        
        except Exception as e:
            result = str(e)
            success = False
        
        # Ensure result is a string
        if not isinstance(result, str):
            result = str(result)
        
        return {
            "result": result,
            "length": len(result),
            "success": success
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        operation = config.get("operation", "")
        if not operation:
            return "Operation is required"
        
        try:
            start_index = int(config.get("start_index", 0))
            end_index = int(config.get("end_index", -1))
            pad_length = int(config.get("pad_length", 10))
            
            if start_index < 0:
                return "Start index must be a non-negative integer"
            
            if pad_length < 0:
                return "Pad length must be a non-negative integer"
        except ValueError:
            return "Invalid numeric value in configuration"
        
        pad_character = config.get("pad_character", " ")
        if pad_character and len(pad_character) != 1 and operation in ["pad_start", "pad_end"]:
            return "Pad character must be a single character"
        
        return None
