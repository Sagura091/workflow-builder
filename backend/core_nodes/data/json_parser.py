from typing import Dict, Any, Optional
import json
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class JsonParser(BaseNode):
    """
    A core node for parsing and generating JSON.
    
    This node can convert between JSON strings and JavaScript objects.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.json_parser",
            name="JSON Parser",
            version="1.0.0",
            description="Convert between JSON and objects",
            author="Workflow Builder",
            category=NodeCategory.DATA,
            tags=["json", "parse", "stringify", "data", "core"],
            inputs=[
                PortDefinition(
                    id="input",
                    name="Input",
                    type="any",
                    description="The input to parse or stringify",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="output",
                    name="Output",
                    type="any",
                    description="The parsed object or JSON string",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if parsing failed",
                    ui_properties={
                        "position": "right-bottom"
                    }
                ),
                PortDefinition(
                    id="is_valid",
                    name="Is Valid",
                    type="boolean",
                    description="Whether the input is valid for the operation",
                    ui_properties={
                        "position": "right-center"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="operation",
                    name="Operation",
                    type="select",
                    description="The operation to perform",
                    required=True,
                    default_value="parse",
                    options=[
                        {"label": "Parse (JSON to Object)", "value": "parse"},
                        {"label": "Stringify (Object to JSON)", "value": "stringify"},
                        {"label": "Validate", "value": "validate"}
                    ]
                ),
                ConfigField(
                    id="pretty_print",
                    name="Pretty Print",
                    type="boolean",
                    description="Whether to format the JSON with indentation",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="indent",
                    name="Indent",
                    type="number",
                    description="Number of spaces for indentation",
                    required=False,
                    default_value=2
                ),
                ConfigField(
                    id="schema",
                    name="JSON Schema",
                    type="code",
                    description="JSON Schema for validation (optional)",
                    required=False
                )
            ],
            ui_properties={
                "color": "#f39c12",
                "icon": "code",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the JSON parser node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The parsed or stringified output
        """
        # Get inputs
        input_value = inputs.get("input")
        
        # Get configuration
        operation = config.get("operation", "parse")
        pretty_print = config.get("pretty_print", True)
        indent = int(config.get("indent", 2)) if pretty_print else None
        schema_str = config.get("schema", "")
        
        # Initialize outputs
        output = None
        error = None
        is_valid = False
        
        try:
            if operation == "parse":
                # Parse JSON string to object
                if isinstance(input_value, str):
                    output = json.loads(input_value)
                    is_valid = True
                else:
                    error = "Input must be a string for parse operation"
            
            elif operation == "stringify":
                # Convert object to JSON string
                output = json.dumps(input_value, indent=indent, ensure_ascii=False)
                is_valid = True
            
            elif operation == "validate":
                # Validate JSON against schema
                try:
                    import jsonschema
                    
                    # Parse schema if provided
                    if schema_str:
                        schema = json.loads(schema_str)
                    else:
                        # If no schema provided, just validate that it's valid JSON
                        if isinstance(input_value, str):
                            json.loads(input_value)
                            is_valid = True
                            output = True
                        else:
                            # Try to serialize to JSON
                            json.dumps(input_value)
                            is_valid = True
                            output = True
                        return {"output": output, "error": error, "is_valid": is_valid}
                    
                    # Convert input to object if it's a string
                    if isinstance(input_value, str):
                        input_obj = json.loads(input_value)
                    else:
                        input_obj = input_value
                    
                    # Validate against schema
                    jsonschema.validate(instance=input_obj, schema=schema)
                    is_valid = True
                    output = True
                
                except ImportError:
                    error = "jsonschema module not available for validation"
                except json.JSONDecodeError as e:
                    error = f"Invalid JSON: {str(e)}"
                except jsonschema.exceptions.ValidationError as e:
                    error = f"Validation error: {str(e)}"
                    output = False
            
            else:
                error = f"Unknown operation: {operation}"
        
        except json.JSONDecodeError as e:
            error = f"Invalid JSON: {str(e)}"
        except Exception as e:
            error = str(e)
        
        return {
            "output": output,
            "error": error,
            "is_valid": is_valid
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        operation = config.get("operation", "")
        if not operation:
            return "Operation is required"
        
        # Validate indent
        try:
            indent = int(config.get("indent", 2))
            if indent < 0:
                return "Indent must be a non-negative integer"
        except ValueError:
            return "Indent must be a number"
        
        # Validate schema if provided
        schema_str = config.get("schema", "")
        if schema_str and operation == "validate":
            try:
                json.loads(schema_str)
            except json.JSONDecodeError as e:
                return f"Invalid JSON Schema: {str(e)}"
        
        return None
