from typing import Dict, Any, List
import json
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class DataMapper:
    """
    A plugin for transforming data by mapping fields.
    
    This plugin can transform arrays of objects by mapping fields to new structures.
    """
    
    def __init__(self):
        self.__plugin_meta__ = PluginMetadata(
            id="data_mapper",
            name="Data Mapper",
            version="1.0.0",
            description="Transform data by mapping fields",
            author="Workflow Builder",
            category=NodeCategory.PROCESSING,
            tags=["data", "transform", "mapping", "processing"],
            inputs=[
                PortDefinition(
                    id="data",
                    name="Data",
                    type="array",
                    description="The data to transform (array of objects)",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="transformed_data",
                    name="Transformed Data",
                    type="array",
                    description="The transformed data",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if transformation failed",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="mapping",
                    name="Field Mapping",
                    type="object",
                    description="Mapping of source fields to target fields",
                    required=True,
                    default_value={}
                ),
                ConfigField(
                    id="keep_original",
                    name="Keep Original Fields",
                    type="boolean",
                    description="Whether to keep original fields not in the mapping",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="flatten_arrays",
                    name="Flatten Arrays",
                    type="boolean",
                    description="Whether to flatten nested arrays",
                    required=False,
                    default_value=False
                )
            ],
            ui_properties={
                "color": "#e67e22",
                "icon": "exchange-alt",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the data mapping operation.
        
        Args:
            config: The plugin configuration
            inputs: The input values
            
        Returns:
            The transformed data
        """
        # Get input data
        data = inputs.get("data", [])
        
        if not isinstance(data, list):
            return {
                "transformed_data": [],
                "error": "Input data must be an array"
            }
        
        # Get configuration
        mapping = config.get("mapping", {})
        keep_original = config.get("keep_original", False)
        flatten_arrays = config.get("flatten_arrays", False)
        
        # Validate mapping
        if not isinstance(mapping, dict):
            try:
                # Try to parse as JSON if it's a string
                if isinstance(mapping, str):
                    mapping = json.loads(mapping)
                else:
                    return {
                        "transformed_data": [],
                        "error": "Mapping must be an object"
                    }
            except json.JSONDecodeError:
                return {
                    "transformed_data": [],
                    "error": "Invalid mapping format"
                }
        
        # Transform data
        transformed_data = []
        
        try:
            for item in data:
                if not isinstance(item, dict):
                    # Skip non-dict items
                    continue
                
                # Create new item
                new_item = {}
                
                # Keep original fields if requested
                if keep_original:
                    new_item.update(item)
                
                # Apply mapping
                for target_field, source_field in mapping.items():
                    if isinstance(source_field, str):
                        # Simple field mapping
                        if source_field in item:
                            new_item[target_field] = item[source_field]
                    elif isinstance(source_field, list):
                        # Nested field access
                        value = item
                        for key in source_field:
                            if isinstance(value, dict) and key in value:
                                value = value[key]
                            else:
                                value = None
                                break
                        if value is not None:
                            new_item[target_field] = value
                    elif isinstance(source_field, dict) and "value" in source_field:
                        # Static value
                        new_item[target_field] = source_field["value"]
                    elif isinstance(source_field, dict) and "concat" in source_field:
                        # Concatenate fields
                        concat_fields = source_field["concat"]
                        if isinstance(concat_fields, list):
                            concat_values = []
                            for field in concat_fields:
                                if field in item:
                                    concat_values.append(str(item[field]))
                                else:
                                    concat_values.append("")
                            new_item[target_field] = "".join(concat_values)
                
                transformed_data.append(new_item)
            
            # Flatten arrays if requested
            if flatten_arrays and transformed_data:
                flattened_data = []
                for item in transformed_data:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if isinstance(value, list):
                                for val in value:
                                    new_item = item.copy()
                                    new_item[key] = val
                                    flattened_data.append(new_item)
                                break
                        else:
                            flattened_data.append(item)
                    else:
                        flattened_data.append(item)
                
                if flattened_data:
                    transformed_data = flattened_data
            
            return {
                "transformed_data": transformed_data,
                "error": None
            }
        
        except Exception as e:
            return {
                "transformed_data": [],
                "error": str(e)
            }
