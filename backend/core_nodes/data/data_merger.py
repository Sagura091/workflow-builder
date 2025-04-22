from typing import Dict, Any, List, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class DataMerger(BaseNode):
    """
    A core node for merging multiple data sources.
    
    This node can combine data from different sources in various ways.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.data_merger",
            name="Data Merger",
            version="1.0.0",
            description="Combine multiple data sources",
            author="Workflow Builder",
            category=NodeCategory.DATA,
            tags=["data", "merge", "combine", "join", "core"],
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
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="input3",
                    name="Input 3",
                    type="any",
                    description="Third data input",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="output",
                    name="Output",
                    type="any",
                    description="The merged data",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="count",
                    name="Count",
                    type="number",
                    description="The number of items in the output",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if merging failed",
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
                        {"label": "Concatenate Arrays", "value": "concat"},
                        {"label": "Merge Objects", "value": "merge_objects"},
                        {"label": "Join Arrays", "value": "join"},
                        {"label": "Zip Arrays", "value": "zip"},
                        {"label": "Union", "value": "union"},
                        {"label": "Intersection", "value": "intersection"},
                        {"label": "Difference", "value": "difference"}
                    ]
                ),
                ConfigField(
                    id="join_key",
                    name="Join Key",
                    type="string",
                    description="Key to use for joining arrays of objects",
                    required=False
                ),
                ConfigField(
                    id="flatten",
                    name="Flatten Arrays",
                    type="boolean",
                    description="Whether to flatten nested arrays",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="unique",
                    name="Remove Duplicates",
                    type="boolean",
                    description="Whether to remove duplicate items",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="overwrite",
                    name="Overwrite Existing",
                    type="boolean",
                    description="Whether to overwrite existing properties when merging objects",
                    required=False,
                    default_value=True
                )
            ],
            ui_properties={
                "color": "#3498db",
                "icon": "object-group",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the data merger node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The merged data
        """
        import copy
        
        # Get inputs
        input1 = inputs.get("input1")
        input2 = inputs.get("input2")
        input3 = inputs.get("input3")
        
        # Get configuration
        merge_mode = config.get("merge_mode", "concat")
        join_key = config.get("join_key", "")
        flatten = config.get("flatten", False)
        unique = config.get("unique", False)
        overwrite = config.get("overwrite", True)
        
        # Collect all inputs
        all_inputs = [input1, input2, input3]
        valid_inputs = [inp for inp in all_inputs if inp is not None]
        
        # Initialize outputs
        output = None
        count = 0
        error = None
        
        try:
            if merge_mode == "concat":
                # Concatenate arrays
                result = []
                
                for inp in valid_inputs:
                    if isinstance(inp, list):
                        result.extend(inp)
                    else:
                        result.append(inp)
                
                # Flatten nested arrays if requested
                if flatten:
                    flat_result = []
                    for item in result:
                        if isinstance(item, list):
                            flat_result.extend(item)
                        else:
                            flat_result.append(item)
                    result = flat_result
                
                # Remove duplicates if requested
                if unique:
                    try:
                        # Try to use set for efficiency
                        result = list(set(result))
                    except:
                        # If items aren't hashable, do it manually
                        unique_items = []
                        for item in result:
                            if item not in unique_items:
                                unique_items.append(item)
                        result = unique_items
                
                output = result
                count = len(result)
            
            elif merge_mode == "merge_objects":
                # Merge objects
                result = {}
                
                for inp in valid_inputs:
                    if isinstance(inp, dict):
                        if overwrite:
                            # Simple update
                            result.update(inp)
                        else:
                            # Only add keys that don't exist
                            for key, value in inp.items():
                                if key not in result:
                                    result[key] = value
                
                output = result
                count = len(result)
            
            elif merge_mode == "join":
                # Join arrays of objects based on key
                if not join_key:
                    error = "Join key is required for join mode"
                    return {"output": None, "count": 0, "error": error}
                
                # Ensure all inputs are arrays
                arrays = []
                for inp in valid_inputs:
                    if isinstance(inp, list):
                        arrays.append(inp)
                    else:
                        arrays.append([inp] if inp is not None else [])
                
                if len(arrays) < 2:
                    output = arrays[0] if arrays else []
                    count = len(output)
                    return {"output": output, "count": count, "error": None}
                
                # Perform join
                result = []
                
                # Build lookup tables for each array after the first
                lookups = []
                for arr in arrays[1:]:
                    lookup = {}
                    for item in arr:
                        if isinstance(item, dict) and join_key in item:
                            key_value = item[join_key]
                            lookup[key_value] = item
                    lookups.append(lookup)
                
                # Join with first array
                for item in arrays[0]:
                    if isinstance(item, dict) and join_key in item:
                        key_value = item[join_key]
                        joined_item = copy.deepcopy(item)
                        
                        # Look for matching items in other arrays
                        for lookup in lookups:
                            if key_value in lookup:
                                matching_item = lookup[key_value]
                                # Merge with joined item
                                for k, v in matching_item.items():
                                    if k != join_key or overwrite:
                                        joined_item[k] = v
                        
                        result.append(joined_item)
                
                output = result
                count = len(result)
            
            elif merge_mode == "zip":
                # Zip arrays (combine corresponding elements)
                # Ensure all inputs are arrays
                arrays = []
                for inp in valid_inputs:
                    if isinstance(inp, list):
                        arrays.append(inp)
                    else:
                        arrays.append([inp] if inp is not None else [])
                
                # Zip the arrays
                result = list(zip(*arrays))
                
                # Convert tuples to lists
                result = [list(item) for item in result]
                
                output = result
                count = len(result)
            
            elif merge_mode == "union":
                # Union of sets (unique items from all inputs)
                result = set()
                
                for inp in valid_inputs:
                    if isinstance(inp, list):
                        try:
                            result.update(inp)
                        except:
                            # If items aren't hashable, do it manually
                            for item in inp:
                                result.add(item)
                    else:
                        result.add(inp)
                
                output = list(result)
                count = len(output)
            
            elif merge_mode == "intersection":
                # Intersection of sets (items common to all inputs)
                if not valid_inputs:
                    output = []
                    count = 0
                    return {"output": output, "count": count, "error": None}
                
                # Convert first input to set
                if isinstance(valid_inputs[0], list):
                    result = set(valid_inputs[0])
                else:
                    result = {valid_inputs[0]}
                
                # Intersect with other inputs
                for inp in valid_inputs[1:]:
                    if isinstance(inp, list):
                        result.intersection_update(inp)
                    else:
                        result.intersection_update({inp})
                
                output = list(result)
                count = len(output)
            
            elif merge_mode == "difference":
                # Difference of sets (items in first input but not in others)
                if not valid_inputs:
                    output = []
                    count = 0
                    return {"output": output, "count": count, "error": None}
                
                # Convert first input to set
                if isinstance(valid_inputs[0], list):
                    result = set(valid_inputs[0])
                else:
                    result = {valid_inputs[0]}
                
                # Subtract other inputs
                for inp in valid_inputs[1:]:
                    if isinstance(inp, list):
                        result.difference_update(inp)
                    else:
                        result.difference_update({inp})
                
                output = list(result)
                count = len(output)
            
            else:
                error = f"Unknown merge mode: {merge_mode}"
        
        except Exception as e:
            error = str(e)
            output = None
            count = 0
        
        return {
            "output": output,
            "count": count,
            "error": error
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        merge_mode = config.get("merge_mode", "")
        if not merge_mode:
            return "Merge mode is required"
        
        if merge_mode == "join" and not config.get("join_key", ""):
            return "Join key is required for join mode"
        
        return None
