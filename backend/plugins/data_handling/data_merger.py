from typing import Dict, Any, List
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class DataMerger:
    """
    A plugin for merging multiple data inputs.
    
    This plugin can combine data from multiple sources into a single output.
    """
    
    def __init__(self):
        self.__plugin_meta__ = PluginMetadata(
            id="data_merger",
            name="Data Merger",
            version="1.0.0",
            description="Merge data from multiple inputs",
            author="Workflow Builder",
            category=NodeCategory.DATA,
            tags=["data", "merge", "combine"],
            inputs=[
                PortDefinition(
                    id="input1",
                    name="Input 1",
                    type="any",
                    description="First data input",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="input2",
                    name="Input 2",
                    type="any",
                    description="Second data input",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="input3",
                    name="Input 3",
                    type="any",
                    description="Third data input (optional)",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="merged_data",
                    name="Merged Data",
                    type="array",
                    description="The combined data from all inputs",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="count",
                    name="Item Count",
                    type="number",
                    description="The number of items in the merged data",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="merge_mode",
                    name="Merge Mode",
                    type="select",
                    description="How to merge the data",
                    required=True,
                    default_value="concat",
                    options=[
                        {"label": "Concatenate", "value": "concat"},
                        {"label": "Merge Objects", "value": "merge_objects"},
                        {"label": "Zip", "value": "zip"}
                    ]
                ),
                ConfigField(
                    id="flatten",
                    name="Flatten Arrays",
                    type="boolean",
                    description="Flatten nested arrays",
                    required=False,
                    default_value=False
                )
            ],
            ui_properties={
                "color": "#e67e22",
                "icon": "object-group",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the data merging operation.
        
        Args:
            config: The plugin configuration
            inputs: The input values
            
        Returns:
            The merged data and item count
        """
        # Get inputs
        input1 = inputs.get("input1", [])
        input2 = inputs.get("input2", [])
        input3 = inputs.get("input3", [])
        
        # Get configuration
        merge_mode = config.get("merge_mode", "concat")
        flatten = config.get("flatten", False)
        
        # Ensure inputs are in the right format
        def ensure_list(value):
            if isinstance(value, list):
                return value
            elif isinstance(value, dict):
                return [value]
            else:
                return [value]
        
        # Process inputs based on merge mode
        if merge_mode == "concat":
            # Concatenate lists
            result = []
            for input_val in [input1, input2, input3]:
                if input_val is not None:
                    if isinstance(input_val, list):
                        result.extend(input_val)
                    else:
                        result.append(input_val)
        
        elif merge_mode == "merge_objects":
            # Merge dictionaries
            result = {}
            for input_val in [input1, input2, input3]:
                if isinstance(input_val, dict):
                    result.update(input_val)
                elif isinstance(input_val, list) and all(isinstance(item, dict) for item in input_val):
                    for item in input_val:
                        result.update(item)
            result = [result]  # Convert to list for consistent output
        
        elif merge_mode == "zip":
            # Zip lists together
            lists = []
            for input_val in [input1, input2, input3]:
                if input_val is not None:
                    lists.append(ensure_list(input_val))
            
            # Zip the lists
            result = list(zip(*lists))
        
        else:
            # Default to concatenation
            result = ensure_list(input1) + ensure_list(input2) + ensure_list(input3)
        
        # Flatten if requested
        if flatten:
            flat_result = []
            for item in result:
                if isinstance(item, list):
                    flat_result.extend(item)
                else:
                    flat_result.append(item)
            result = flat_result
        
        # Return result
        return {
            "merged_data": result,
            "count": len(result)
        }
