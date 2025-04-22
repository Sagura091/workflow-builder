from typing import Dict, Any, List, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class ArrayOperations(BaseNode):
    """
    A core node for performing operations on arrays.
    
    This node can manipulate arrays in various ways.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.array_operations",
            name="Array Operations",
            version="1.0.0",
            description="Perform operations on arrays",
            author="Workflow Builder",
            category=NodeCategory.DATA,
            tags=["array", "list", "data", "core"],
            inputs=[
                PortDefinition(
                    id="array",
                    name="Array",
                    type="array",
                    description="The array to operate on",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="item",
                    name="Item",
                    type="any",
                    description="The item to add, remove, or find",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="index",
                    name="Index",
                    type="number",
                    description="The index for operations that require it",
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
                    type="any",
                    description="The result of the operation",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="modified_array",
                    name="Modified Array",
                    type="array",
                    description="The modified array",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="length",
                    name="Length",
                    type="number",
                    description="The length of the array",
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
                    default_value="get",
                    options=[
                        {"label": "Get Item", "value": "get"},
                        {"label": "Add Item", "value": "add"},
                        {"label": "Remove Item", "value": "remove"},
                        {"label": "Remove At Index", "value": "remove_at"},
                        {"label": "Insert At Index", "value": "insert_at"},
                        {"label": "Find Index", "value": "find_index"},
                        {"label": "Filter", "value": "filter"},
                        {"label": "Map", "value": "map"},
                        {"label": "Sort", "value": "sort"},
                        {"label": "Reverse", "value": "reverse"},
                        {"label": "Join", "value": "join"},
                        {"label": "Slice", "value": "slice"},
                        {"label": "Unique", "value": "unique"}
                    ]
                ),
                ConfigField(
                    id="default_index",
                    name="Default Index",
                    type="number",
                    description="Default index to use if not provided in input",
                    required=False,
                    default_value=0
                ),
                ConfigField(
                    id="filter_property",
                    name="Filter Property",
                    type="string",
                    description="Property to filter by (for filter operation)",
                    required=False
                ),
                ConfigField(
                    id="filter_value",
                    name="Filter Value",
                    type="string",
                    description="Value to filter by (for filter operation)",
                    required=False
                ),
                ConfigField(
                    id="sort_property",
                    name="Sort Property",
                    type="string",
                    description="Property to sort by (for sort operation)",
                    required=False
                ),
                ConfigField(
                    id="sort_direction",
                    name="Sort Direction",
                    type="select",
                    description="Direction to sort (for sort operation)",
                    required=False,
                    default_value="asc",
                    options=[
                        {"label": "Ascending", "value": "asc"},
                        {"label": "Descending", "value": "desc"}
                    ]
                ),
                ConfigField(
                    id="join_delimiter",
                    name="Join Delimiter",
                    type="string",
                    description="Delimiter to use when joining (for join operation)",
                    required=False,
                    default_value=","
                ),
                ConfigField(
                    id="slice_start",
                    name="Slice Start",
                    type="number",
                    description="Start index for slice operation",
                    required=False,
                    default_value=0
                ),
                ConfigField(
                    id="slice_end",
                    name="Slice End",
                    type="number",
                    description="End index for slice operation",
                    required=False,
                    default_value=-1
                )
            ],
            ui_properties={
                "color": "#2ecc71",
                "icon": "list",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the array operations node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The result of the operation
        """
        import copy
        
        # Get inputs
        array = inputs.get("array", [])
        item = inputs.get("item")
        index = inputs.get("index")
        
        # Ensure array is a list
        if not isinstance(array, list):
            try:
                array = list(array)
            except:
                array = [array] if array is not None else []
        
        # Make a copy to avoid modifying the original
        array_copy = copy.deepcopy(array)
        
        # Get configuration
        operation = config.get("operation", "get")
        default_index = int(config.get("default_index", 0))
        filter_property = config.get("filter_property", "")
        filter_value = config.get("filter_value", "")
        sort_property = config.get("sort_property", "")
        sort_direction = config.get("sort_direction", "asc")
        join_delimiter = config.get("join_delimiter", ",")
        slice_start = int(config.get("slice_start", 0))
        slice_end = int(config.get("slice_end", -1))
        
        # Use input index or default
        idx = index if index is not None else default_index
        
        # Perform the operation
        result = None
        
        if operation == "get":
            # Get item at index
            if 0 <= idx < len(array_copy):
                result = array_copy[idx]
        
        elif operation == "add":
            # Add item to end of array
            if item is not None:
                array_copy.append(item)
                result = len(array_copy) - 1  # Return index of added item
        
        elif operation == "remove":
            # Remove item from array
            if item in array_copy:
                array_copy.remove(item)
                result = True
            else:
                result = False
        
        elif operation == "remove_at":
            # Remove item at index
            if 0 <= idx < len(array_copy):
                result = array_copy.pop(idx)
        
        elif operation == "insert_at":
            # Insert item at index
            if item is not None:
                idx = max(0, min(idx, len(array_copy)))
                array_copy.insert(idx, item)
                result = idx
        
        elif operation == "find_index":
            # Find index of item
            try:
                result = array_copy.index(item)
            except ValueError:
                result = -1
        
        elif operation == "filter":
            # Filter array by property value
            if filter_property:
                array_copy = [
                    item for item in array_copy
                    if isinstance(item, dict) and item.get(filter_property) == filter_value
                ]
            result = len(array_copy)
        
        elif operation == "map":
            # Map array by extracting property
            if filter_property:
                array_copy = [
                    item.get(filter_property) if isinstance(item, dict) else item
                    for item in array_copy
                ]
            result = len(array_copy)
        
        elif operation == "sort":
            # Sort array
            if sort_property:
                # Sort by property
                array_copy.sort(
                    key=lambda x: x.get(sort_property) if isinstance(x, dict) else x,
                    reverse=(sort_direction == "desc")
                )
            else:
                # Simple sort
                try:
                    array_copy.sort(reverse=(sort_direction == "desc"))
                except:
                    # If sorting fails, leave array unchanged
                    pass
            result = True
        
        elif operation == "reverse":
            # Reverse array
            array_copy.reverse()
            result = True
        
        elif operation == "join":
            # Join array into string
            try:
                result = join_delimiter.join(str(x) for x in array_copy)
                array_copy = array  # Keep original array
            except:
                result = ""
        
        elif operation == "slice":
            # Slice array
            if slice_end < 0:
                slice_end = len(array_copy)
            array_copy = array_copy[slice_start:slice_end]
            result = len(array_copy)
        
        elif operation == "unique":
            # Get unique items
            try:
                # Try to use set for efficiency
                array_copy = list(set(array_copy))
            except:
                # If items aren't hashable, do it manually
                unique_items = []
                for item in array_copy:
                    if item not in unique_items:
                        unique_items.append(item)
                array_copy = unique_items
            result = len(array_copy)
        
        return {
            "result": result,
            "modified_array": array_copy,
            "length": len(array_copy)
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        operation = config.get("operation", "")
        if not operation:
            return "Operation is required"
        
        try:
            default_index = int(config.get("default_index", 0))
            slice_start = int(config.get("slice_start", 0))
            slice_end = int(config.get("slice_end", -1))
        except ValueError:
            return "Invalid numeric value in configuration"
        
        return None
