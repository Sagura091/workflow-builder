from typing import Dict, Any, Optional
import os
import json
import csv
import io
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class FileReader(BaseNode):
    """
    A core node for reading data from files.
    
    This node can read data from various file formats.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.file_reader",
            name="File Reader",
            version="1.0.0",
            description="Read data from files",
            author="Workflow Builder",
            category=NodeCategory.FILE_STORAGE,
            tags=["file", "read", "input", "storage", "core"],
            inputs=[
                PortDefinition(
                    id="file_path",
                    name="File Path",
                    type="string",
                    description="Path to the file to read",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="encoding",
                    name="Encoding",
                    type="string",
                    description="File encoding (overrides config)",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="trigger",
                    name="Trigger",
                    type="trigger",
                    description="Trigger to read the file",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="data",
                    name="Data",
                    type="any",
                    description="The data read from the file",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="file_info",
                    name="File Info",
                    type="object",
                    description="Information about the file",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if reading failed",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="file_type",
                    name="File Type",
                    type="select",
                    description="The type of file to read",
                    required=True,
                    default_value="auto",
                    options=[
                        {"label": "Auto-detect", "value": "auto"},
                        {"label": "Text", "value": "text"},
                        {"label": "JSON", "value": "json"},
                        {"label": "CSV", "value": "csv"},
                        {"label": "Binary", "value": "binary"}
                    ]
                ),
                ConfigField(
                    id="encoding",
                    name="Encoding",
                    type="string",
                    description="File encoding",
                    required=False,
                    default_value="utf-8"
                ),
                ConfigField(
                    id="csv_delimiter",
                    name="CSV Delimiter",
                    type="string",
                    description="Delimiter for CSV files",
                    required=False,
                    default_value=","
                ),
                ConfigField(
                    id="csv_has_header",
                    name="CSV Has Header",
                    type="boolean",
                    description="Whether CSV files have a header row",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="max_size",
                    name="Max Size (KB)",
                    type="number",
                    description="Maximum file size to read in KB (0 for no limit)",
                    required=False,
                    default_value=1024
                ),
                ConfigField(
                    id="base_path",
                    name="Base Path",
                    type="string",
                    description="Base path for relative file paths",
                    required=False,
                    default_value=""
                )
            ],
            ui_properties={
                "color": "#3498db",
                "icon": "file-import",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the file reader node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The data read from the file
        """
        # Get inputs
        file_path = inputs.get("file_path", "")
        input_encoding = inputs.get("encoding")
        trigger = inputs.get("trigger", False)
        
        # Get configuration
        file_type = config.get("file_type", "auto")
        config_encoding = config.get("encoding", "utf-8")
        csv_delimiter = config.get("csv_delimiter", ",")
        csv_has_header = config.get("csv_has_header", True)
        max_size = int(config.get("max_size", 1024)) * 1024  # Convert to bytes
        base_path = config.get("base_path", "")
        
        # Use input encoding if provided, otherwise use config
        encoding = input_encoding if input_encoding is not None else config_encoding
        
        # Initialize outputs
        data = None
        file_info = {}
        error = None
        
        # Check if file path is provided
        if not file_path:
            error = "No file path provided"
            return {"data": None, "file_info": {}, "error": error}
        
        # Resolve file path
        if base_path and not os.path.isabs(file_path):
            full_path = os.path.join(base_path, file_path)
        else:
            full_path = file_path
        
        try:
            # Check if file exists
            if not os.path.exists(full_path):
                error = f"File not found: {full_path}"
                return {"data": None, "file_info": {}, "error": error}
            
            # Get file info
            file_size = os.path.getsize(full_path)
            file_info = {
                "path": full_path,
                "size": file_size,
                "size_kb": round(file_size / 1024, 2),
                "modified": os.path.getmtime(full_path),
                "extension": os.path.splitext(full_path)[1].lower()
            }
            
            # Check file size
            if max_size > 0 and file_size > max_size:
                error = f"File too large: {file_size} bytes (max {max_size} bytes)"
                return {"data": None, "file_info": file_info, "error": error}
            
            # Auto-detect file type if needed
            if file_type == "auto":
                extension = file_info["extension"]
                if extension == ".json":
                    file_type = "json"
                elif extension == ".csv":
                    file_type = "csv"
                elif extension in [".txt", ".md", ".py", ".js", ".html", ".css"]:
                    file_type = "text"
                else:
                    file_type = "binary"
            
            # Read file based on type
            if file_type == "text":
                with open(full_path, "r", encoding=encoding) as f:
                    data = f.read()
            
            elif file_type == "json":
                with open(full_path, "r", encoding=encoding) as f:
                    data = json.load(f)
            
            elif file_type == "csv":
                with open(full_path, "r", encoding=encoding, newline="") as f:
                    if csv_has_header:
                        reader = csv.DictReader(f, delimiter=csv_delimiter)
                        data = list(reader)
                    else:
                        reader = csv.reader(f, delimiter=csv_delimiter)
                        data = list(reader)
            
            elif file_type == "binary":
                with open(full_path, "rb") as f:
                    binary_data = f.read()
                    # Convert to base64 for safe handling
                    import base64
                    data = base64.b64encode(binary_data).decode("ascii")
            
            # Update file info
            file_info["type"] = file_type
            file_info["encoding"] = encoding
        
        except Exception as e:
            error = str(e)
            data = None
        
        return {
            "data": data,
            "file_info": file_info,
            "error": error
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        file_type = config.get("file_type", "")
        if not file_type:
            return "File type is required"
        
        # Validate max size
        try:
            max_size = int(config.get("max_size", 1024))
            if max_size < 0:
                return "Max size must be a non-negative integer"
        except (ValueError, TypeError):
            return "Max size must be a number"
        
        # Validate CSV delimiter
        csv_delimiter = config.get("csv_delimiter", ",")
        if file_type == "csv" and not csv_delimiter:
            return "CSV delimiter cannot be empty"
        
        return None
