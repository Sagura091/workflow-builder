from typing import Dict, Any, List
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class DataSorter:
    """
    A plugin for sorting data by specified fields.
    
    This plugin can sort arrays of objects by one or more fields.
    """
    
    def __init__(self):
        self.__plugin_meta__ = PluginMetadata(
            id="data_sorter",
            name="Data Sorter",
            version="1.0.0",
            description="Sort data by specified fields",
            author="Workflow Builder",
            category=NodeCategory.PROCESSING,
            tags=["data", "sort", "processing", "array"],
            inputs=[
                PortDefinition(
                    id="data",
                    name="Data",
                    type="array",
                    description="The data to sort (array of objects)",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="sorted_data",
                    name="Sorted Data",
                    type="array",
                    description="The sorted data",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if sorting failed",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="sort_by",
                    name="Sort By",
                    type="string",
                    description="Field to sort by",
                    required=True
                ),
                ConfigField(
                    id="direction",
                    name="Direction",
                    type="select",
                    description="Sort direction",
                    required=True,
                    default_value="asc",
                    options=[
                        {"label": "Ascending", "value": "asc"},
                        {"label": "Descending", "value": "desc"}
                    ]
                ),
                ConfigField(
                    id="secondary_sort",
                    name="Secondary Sort",
                    type="string",
                    description="Secondary field to sort by (optional)",
                    required=False
                ),
                ConfigField(
                    id="secondary_direction",
                    name="Secondary Direction",
                    type="select",
                    description="Secondary sort direction",
                    required=False,
                    default_value="asc",
                    options=[
                        {"label": "Ascending", "value": "asc"},
                        {"label": "Descending", "value": "desc"}
                    ]
                ),
                ConfigField(
                    id="case_sensitive",
                    name="Case Sensitive",
                    type="boolean",
                    description="Whether string comparisons are case sensitive",
                    required=False,
                    default_value=False
                )
            ],
            ui_properties={
                "color": "#2ecc71",
                "icon": "sort",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the data sorting operation.
        
        Args:
            config: The plugin configuration
            inputs: The input values
            
        Returns:
            The sorted data
        """
        # Get input data
        data = inputs.get("data", [])
        
        if not isinstance(data, list):
            return {
                "sorted_data": [],
                "error": "Input data must be an array"
            }
        
        # Get configuration
        sort_by = config.get("sort_by", "")
        direction = config.get("direction", "asc")
        secondary_sort = config.get("secondary_sort", "")
        secondary_direction = config.get("secondary_direction", "asc")
        case_sensitive = config.get("case_sensitive", False)
        
        if not sort_by:
            return {
                "sorted_data": data,
                "error": "No sort field specified"
            }
        
        # Check if data is sortable
        if not all(isinstance(item, dict) for item in data):
            return {
                "sorted_data": data,
                "error": "Data must be an array of objects"
            }
        
        # Sort data
        try:
            # Create a key function for sorting
            def get_sort_key(item):
                # Get primary sort value
                primary_value = item.get(sort_by)
                
                # Handle string case sensitivity
                if isinstance(primary_value, str) and not case_sensitive:
                    primary_value = primary_value.lower()
                
                # Get secondary sort value if specified
                if secondary_sort:
                    secondary_value = item.get(secondary_sort)
                    
                    # Handle string case sensitivity
                    if isinstance(secondary_value, str) and not case_sensitive:
                        secondary_value = secondary_value.lower()
                    
                    return (primary_value, secondary_value)
                
                return primary_value
            
            # Sort the data
            sorted_data = sorted(data, key=get_sort_key)
            
            # Reverse if descending order
            if direction == "desc":
                sorted_data = list(reversed(sorted_data))
            
            return {
                "sorted_data": sorted_data,
                "error": None
            }
        
        except Exception as e:
            return {
                "sorted_data": data,
                "error": str(e)
            }
