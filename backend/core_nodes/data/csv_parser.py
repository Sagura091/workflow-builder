from typing import Dict, Any, List, Optional
import csv
import io
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class CsvParser(BaseNode):
    """
    A core node for parsing and generating CSV.
    
    This node can convert between CSV strings and arrays of objects.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.csv_parser",
            name="CSV Parser",
            version="1.0.0",
            description="Convert between CSV and data objects",
            author="Workflow Builder",
            category=NodeCategory.DATA,
            tags=["csv", "parse", "data", "core"],
            inputs=[
                PortDefinition(
                    id="input",
                    name="Input",
                    type="any",
                    description="The input to parse or generate",
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
                    description="The parsed data or CSV string",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="headers",
                    name="Headers",
                    type="array",
                    description="The CSV headers",
                    ui_properties={
                        "position": "right-center"
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
                        {"label": "Parse (CSV to Objects)", "value": "parse"},
                        {"label": "Generate (Objects to CSV)", "value": "generate"}
                    ]
                ),
                ConfigField(
                    id="delimiter",
                    name="Delimiter",
                    type="string",
                    description="The delimiter character",
                    required=False,
                    default_value=","
                ),
                ConfigField(
                    id="has_header",
                    name="Has Header",
                    type="boolean",
                    description="Whether the CSV has a header row",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="quote_char",
                    name="Quote Character",
                    type="string",
                    description="The character used for quoting",
                    required=False,
                    default_value="\""
                ),
                ConfigField(
                    id="skip_initial_space",
                    name="Skip Initial Space",
                    type="boolean",
                    description="Whether to skip initial whitespace in fields",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="custom_headers",
                    name="Custom Headers",
                    type="string",
                    description="Comma-separated list of custom headers (for generate operation)",
                    required=False
                )
            ],
            ui_properties={
                "color": "#27ae60",
                "icon": "table",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the CSV parser node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The parsed or generated output
        """
        # Get inputs
        input_value = inputs.get("input")
        
        # Get configuration
        operation = config.get("operation", "parse")
        delimiter = config.get("delimiter", ",")
        has_header = config.get("has_header", True)
        quote_char = config.get("quote_char", "\"")
        skip_initial_space = config.get("skip_initial_space", True)
        custom_headers_str = config.get("custom_headers", "")
        
        # Parse custom headers if provided
        custom_headers = None
        if custom_headers_str:
            custom_headers = [h.strip() for h in custom_headers_str.split(",")]
        
        # Initialize outputs
        output = None
        headers = []
        error = None
        
        try:
            if operation == "parse":
                # Parse CSV string to objects
                if not isinstance(input_value, str):
                    error = "Input must be a string for parse operation"
                    return {"output": None, "headers": [], "error": error}
                
                # Parse CSV
                csv_data = []
                csv_reader = csv.reader(
                    io.StringIO(input_value),
                    delimiter=delimiter,
                    quotechar=quote_char,
                    skipinitialspace=skip_initial_space
                )
                
                # Read rows
                rows = list(csv_reader)
                if not rows:
                    return {"output": [], "headers": [], "error": None}
                
                # Get headers
                if has_header:
                    headers = rows[0]
                    data_rows = rows[1:]
                else:
                    # Use custom headers or generate column names
                    if custom_headers:
                        headers = custom_headers
                    else:
                        # Generate column names (Column1, Column2, etc.)
                        headers = [f"Column{i+1}" for i in range(len(rows[0]))]
                    data_rows = rows
                
                # Convert to objects if has headers
                if has_header or custom_headers:
                    for row in data_rows:
                        # Create object with header keys
                        row_obj = {}
                        for i, value in enumerate(row):
                            if i < len(headers):
                                row_obj[headers[i]] = value
                        csv_data.append(row_obj)
                else:
                    # Just return arrays
                    csv_data = data_rows
                
                output = csv_data
            
            elif operation == "generate":
                # Convert objects to CSV string
                if not isinstance(input_value, list):
                    error = "Input must be an array for generate operation"
                    return {"output": None, "headers": [], "error": error}
                
                # Determine headers
                if custom_headers:
                    headers = custom_headers
                elif input_value and isinstance(input_value[0], dict):
                    # Get headers from first object
                    headers = list(input_value[0].keys())
                else:
                    headers = []
                
                # Create CSV
                output_buffer = io.StringIO()
                csv_writer = csv.writer(
                    output_buffer,
                    delimiter=delimiter,
                    quotechar=quote_char,
                    quoting=csv.QUOTE_MINIMAL
                )
                
                # Write header if needed
                if has_header and headers:
                    csv_writer.writerow(headers)
                
                # Write data rows
                for item in input_value:
                    if isinstance(item, dict):
                        # Extract values in header order
                        row = [item.get(header, "") for header in headers]
                        csv_writer.writerow(row)
                    elif isinstance(item, list):
                        # Write list directly
                        csv_writer.writerow(item)
                    else:
                        # Write single value
                        csv_writer.writerow([item])
                
                output = output_buffer.getvalue()
                output_buffer.close()
            
            else:
                error = f"Unknown operation: {operation}"
        
        except Exception as e:
            error = str(e)
        
        return {
            "output": output,
            "headers": headers,
            "error": error
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        operation = config.get("operation", "")
        if not operation:
            return "Operation is required"
        
        delimiter = config.get("delimiter", ",")
        if not delimiter:
            return "Delimiter cannot be empty"
        
        quote_char = config.get("quote_char", "\"")
        if not quote_char:
            return "Quote character cannot be empty"
        
        return None
