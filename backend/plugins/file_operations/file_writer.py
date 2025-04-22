from typing import Dict, Any
import os
import json
import csv
import pandas as pd
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class FileWriter:
    """
    A plugin for writing data to various file formats.
    
    This plugin can write data to CSV, JSON, Excel, and text files.
    """
    
    def __init__(self):
        self.__plugin_meta__ = PluginMetadata(
            id="file_writer",
            name="File Writer",
            version="1.0.0",
            description="Write data to various file formats",
            author="Workflow Builder",
            category=NodeCategory.DATA,
            tags=["file", "data", "output", "csv", "json", "excel", "text"],
            inputs=[
                PortDefinition(
                    id="data",
                    name="Data",
                    type="any",
                    description="The data to write to the file",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="file_path",
                    name="File Path",
                    type="string",
                    description="Path where the file should be written",
                    required=True,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="success",
                    name="Success",
                    type="boolean",
                    description="Whether the operation was successful",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="file_path",
                    name="File Path",
                    type="string",
                    description="Path to the written file",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if the operation failed",
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
                    description="The type of file to write",
                    required=True,
                    default_value="csv",
                    options=[
                        {"label": "CSV", "value": "csv"},
                        {"label": "JSON", "value": "json"},
                        {"label": "Excel", "value": "excel"},
                        {"label": "Text", "value": "text"}
                    ]
                ),
                ConfigField(
                    id="encoding",
                    name="Encoding",
                    type="select",
                    description="The encoding of the file",
                    required=False,
                    default_value="utf-8",
                    options=[
                        {"label": "UTF-8", "value": "utf-8"},
                        {"label": "ASCII", "value": "ascii"},
                        {"label": "Latin-1", "value": "latin-1"}
                    ]
                ),
                ConfigField(
                    id="include_header",
                    name="Include Header",
                    type="boolean",
                    description="Whether to include a header row (for CSV and Excel)",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="overwrite",
                    name="Overwrite Existing",
                    type="boolean",
                    description="Whether to overwrite the file if it already exists",
                    required=False,
                    default_value=False
                )
            ],
            ui_properties={
                "color": "#2ecc71",
                "icon": "file-export",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the file writing operation.
        
        Args:
            config: The plugin configuration
            inputs: The input values
            
        Returns:
            The result of the operation
        """
        # Get inputs
        data = inputs.get("data")
        file_path = inputs.get("file_path", "")
        
        if not file_path:
            return {
                "success": False,
                "file_path": None,
                "error": "No file path provided"
            }
        
        if data is None:
            return {
                "success": False,
                "file_path": file_path,
                "error": "No data provided"
            }
        
        # Get configuration
        file_type = config.get("file_type", "csv")
        encoding = config.get("encoding", "utf-8")
        include_header = config.get("include_header", True)
        overwrite = config.get("overwrite", False)
        
        # Check if file exists and should not be overwritten
        if os.path.exists(file_path) and not overwrite:
            return {
                "success": False,
                "file_path": file_path,
                "error": f"File already exists: {file_path}"
            }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Write file based on type
        try:
            if file_type == "csv":
                # Write CSV file
                if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    # List of dictionaries
                    with open(file_path, "w", encoding=encoding, newline="") as f:
                        if data:
                            fieldnames = data[0].keys()
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            if include_header:
                                writer.writeheader()
                            writer.writerows(data)
                        else:
                            # Empty data
                            writer = csv.writer(f)
                            if include_header:
                                writer.writerow([])
                
                elif isinstance(data, list) and all(isinstance(item, list) for item in data):
                    # List of lists
                    with open(file_path, "w", encoding=encoding, newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(data)
                
                else:
                    # Convert to DataFrame and write
                    df = pd.DataFrame(data)
                    df.to_csv(file_path, index=False, header=include_header, encoding=encoding)
            
            elif file_type == "json":
                # Write JSON file
                with open(file_path, "w", encoding=encoding) as f:
                    json.dump(data, f, indent=2)
            
            elif file_type == "excel":
                # Write Excel file
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    df.to_excel(file_path, index=False, header=include_header)
                else:
                    # Convert to DataFrame and write
                    df = pd.DataFrame(data)
                    df.to_excel(file_path, index=False, header=include_header)
            
            else:
                # Write text file
                with open(file_path, "w", encoding=encoding) as f:
                    if isinstance(data, str):
                        f.write(data)
                    else:
                        f.write(str(data))
            
            return {
                "success": True,
                "file_path": file_path,
                "error": None
            }
        
        except Exception as e:
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e)
            }
