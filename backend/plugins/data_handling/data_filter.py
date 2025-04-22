from typing import Dict, Any, List
import re
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class DataFilter:
    """
    A plugin for filtering data based on conditions.
    
    This plugin can filter arrays of objects based on field values.
    """
    
    def __init__(self):
        self.__plugin_meta__ = PluginMetadata(
            id="data_filter",
            name="Data Filter",
            version="1.0.0",
            description="Filter data based on conditions",
            author="Workflow Builder",
            category=NodeCategory.PROCESSING,
            tags=["data", "filter", "processing"],
            inputs=[
                PortDefinition(
                    id="data",
                    name="Data",
                    type="array",
                    description="The data to filter (array of objects)",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="filtered_data",
                    name="Filtered Data",
                    type="array",
                    description="Data that passed the filter",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="excluded_data",
                    name="Excluded Data",
                    type="array",
                    description="Data that did not pass the filter",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="count",
                    name="Count",
                    type="number",
                    description="Number of items that passed the filter",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="field",
                    name="Field",
                    type="string",
                    description="The field to filter on",
                    required=True
                ),
                ConfigField(
                    id="operator",
                    name="Operator",
                    type="select",
                    description="The comparison operator",
                    required=True,
                    default_value="eq",
                    options=[
                        {"label": "Equals", "value": "eq"},
                        {"label": "Not Equals", "value": "neq"},
                        {"label": "Greater Than", "value": "gt"},
                        {"label": "Less Than", "value": "lt"},
                        {"label": "Greater Than or Equal", "value": "gte"},
                        {"label": "Less Than or Equal", "value": "lte"},
                        {"label": "Contains", "value": "contains"},
                        {"label": "Starts With", "value": "startswith"},
                        {"label": "Ends With", "value": "endswith"},
                        {"label": "Matches Regex", "value": "regex"},
                        {"label": "Is Empty", "value": "empty"},
                        {"label": "Is Not Empty", "value": "not_empty"}
                    ]
                ),
                ConfigField(
                    id="value",
                    name="Value",
                    type="string",
                    description="The value to compare against",
                    required=False
                ),
                ConfigField(
                    id="case_sensitive",
                    name="Case Sensitive",
                    type="boolean",
                    description="Whether string comparisons are case sensitive",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="invert",
                    name="Invert Filter",
                    type="boolean",
                    description="Invert the filter result",
                    required=False,
                    default_value=False
                )
            ],
            ui_properties={
                "color": "#9b59b6",
                "icon": "filter",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the data filtering operation.
        
        Args:
            config: The plugin configuration
            inputs: The input values
            
        Returns:
            The filtered data and statistics
        """
        # Get input data
        data = inputs.get("data", [])
        
        if not isinstance(data, list):
            return {
                "filtered_data": [],
                "excluded_data": [],
                "count": 0
            }
        
        # Get configuration
        field = config.get("field", "")
        operator = config.get("operator", "eq")
        value = config.get("value", "")
        case_sensitive = config.get("case_sensitive", False)
        invert = config.get("invert", False)
        
        # Filter data
        filtered_data = []
        excluded_data = []
        
        for item in data:
            # Skip non-dict items
            if not isinstance(item, dict):
                excluded_data.append(item)
                continue
            
            # Get field value
            field_value = item.get(field)
            
            # Apply filter based on operator
            passes_filter = self._apply_filter(field_value, operator, value, case_sensitive)
            
            # Invert result if needed
            if invert:
                passes_filter = not passes_filter
            
            # Add to appropriate list
            if passes_filter:
                filtered_data.append(item)
            else:
                excluded_data.append(item)
        
        return {
            "filtered_data": filtered_data,
            "excluded_data": excluded_data,
            "count": len(filtered_data)
        }
    
    def _apply_filter(self, field_value: Any, operator: str, value: Any, case_sensitive: bool) -> bool:
        """Apply a filter operation."""
        # Handle None values
        if field_value is None:
            if operator == "empty":
                return True
            elif operator == "not_empty":
                return False
            elif operator == "eq":
                return value is None or value == "null" or value == ""
            elif operator == "neq":
                return value is not None and value != "null" and value != ""
            else:
                return False
        
        # Handle empty/not_empty operators
        if operator == "empty":
            if isinstance(field_value, str):
                return field_value.strip() == ""
            elif isinstance(field_value, (list, dict)):
                return len(field_value) == 0
            else:
                return False
        
        elif operator == "not_empty":
            if isinstance(field_value, str):
                return field_value.strip() != ""
            elif isinstance(field_value, (list, dict)):
                return len(field_value) > 0
            else:
                return True
        
        # Convert value to appropriate type
        if isinstance(field_value, (int, float)) and not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (ValueError, TypeError):
                pass
        
        # String operations
        if isinstance(field_value, str) and isinstance(value, str):
            if not case_sensitive:
                field_value = field_value.lower()
                value = value.lower()
            
            if operator == "eq":
                return field_value == value
            elif operator == "neq":
                return field_value != value
            elif operator == "contains":
                return value in field_value
            elif operator == "startswith":
                return field_value.startswith(value)
            elif operator == "endswith":
                return field_value.endswith(value)
            elif operator == "regex":
                try:
                    pattern = re.compile(value, 0 if case_sensitive else re.IGNORECASE)
                    return bool(pattern.search(field_value))
                except re.error:
                    return False
        
        # Numeric operations
        if isinstance(field_value, (int, float)) and isinstance(value, (int, float)):
            if operator == "eq":
                return field_value == value
            elif operator == "neq":
                return field_value != value
            elif operator == "gt":
                return field_value > value
            elif operator == "lt":
                return field_value < value
            elif operator == "gte":
                return field_value >= value
            elif operator == "lte":
                return field_value <= value
        
        # Boolean operations
        if isinstance(field_value, bool):
            bool_value = value
            if isinstance(value, str):
                bool_value = value.lower() in ["true", "yes", "1", "y"]
            
            if operator == "eq":
                return field_value == bool_value
            elif operator == "neq":
                return field_value != bool_value
        
        # Default comparison
        if operator == "eq":
            return field_value == value
        elif operator == "neq":
            return field_value != value
        
        return False
