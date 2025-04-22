from typing import Dict, Any, List, Optional
import random
import string
import uuid
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class RandomGenerator(BaseNode):
    """
    A core node for generating random values.
    
    This node can generate various types of random data.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.random_generator",
            name="Random Generator",
            version="1.0.0",
            description="Generate random values",
            author="Workflow Builder",
            category=NodeCategory.MATH,
            tags=["random", "generator", "math", "core"],
            inputs=[
                PortDefinition(
                    id="seed",
                    name="Seed",
                    type="number",
                    description="Seed for the random generator",
                    required=False,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="min",
                    name="Min",
                    type="number",
                    description="Minimum value (for number generation)",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="max",
                    name="Max",
                    type="number",
                    description="Maximum value (for number generation)",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="value",
                    name="Value",
                    type="any",
                    description="The generated random value",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="values",
                    name="Values",
                    type="array",
                    description="Multiple random values (for array generation)",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="seed",
                    name="Used Seed",
                    type="number",
                    description="The seed that was used",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="type",
                    name="Type",
                    type="select",
                    description="Type of random value to generate",
                    required=True,
                    default_value="number",
                    options=[
                        {"label": "Number", "value": "number"},
                        {"label": "Integer", "value": "integer"},
                        {"label": "Boolean", "value": "boolean"},
                        {"label": "String", "value": "string"},
                        {"label": "UUID", "value": "uuid"},
                        {"label": "Array", "value": "array"},
                        {"label": "Color", "value": "color"},
                        {"label": "Date", "value": "date"},
                        {"label": "Item from List", "value": "item"}
                    ]
                ),
                ConfigField(
                    id="min",
                    name="Min",
                    type="number",
                    description="Minimum value (for number/integer generation)",
                    required=False,
                    default_value=0
                ),
                ConfigField(
                    id="max",
                    name="Max",
                    type="number",
                    description="Maximum value (for number/integer generation)",
                    required=False,
                    default_value=100
                ),
                ConfigField(
                    id="length",
                    name="Length",
                    type="number",
                    description="Length of string or size of array",
                    required=False,
                    default_value=10
                ),
                ConfigField(
                    id="characters",
                    name="Characters",
                    type="string",
                    description="Characters to use for string generation",
                    required=False,
                    default_value="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                ),
                ConfigField(
                    id="items",
                    name="Items",
                    type="string",
                    description="Comma-separated list of items to choose from",
                    required=False,
                    default_value="item1,item2,item3"
                ),
                ConfigField(
                    id="date_min",
                    name="Min Date",
                    type="string",
                    description="Minimum date (YYYY-MM-DD)",
                    required=False,
                    default_value="2000-01-01"
                ),
                ConfigField(
                    id="date_max",
                    name="Max Date",
                    type="string",
                    description="Maximum date (YYYY-MM-DD)",
                    required=False,
                    default_value="2030-12-31"
                ),
                ConfigField(
                    id="use_seed",
                    name="Use Seed",
                    type="boolean",
                    description="Whether to use a seed for reproducible randomness",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="seed",
                    name="Seed",
                    type="number",
                    description="Seed for the random generator",
                    required=False,
                    default_value=42
                )
            ],
            ui_properties={
                "color": "#9b59b6",
                "icon": "dice",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the random generator node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The generated random value(s)
        """
        import datetime
        
        # Get inputs
        input_seed = inputs.get("seed")
        input_min = inputs.get("min")
        input_max = inputs.get("max")
        
        # Get configuration
        value_type = config.get("type", "number")
        config_min = config.get("min", 0)
        config_max = config.get("max", 100)
        length = int(config.get("length", 10))
        characters = config.get("characters", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        items_str = config.get("items", "item1,item2,item3")
        date_min_str = config.get("date_min", "2000-01-01")
        date_max_str = config.get("date_max", "2030-12-31")
        use_seed = config.get("use_seed", False)
        config_seed = config.get("seed", 42)
        
        # Use input values if provided, otherwise use config
        min_value = input_min if input_min is not None else config_min
        max_value = input_max if input_max is not None else config_max
        seed = input_seed if input_seed is not None else config_seed
        
        # Initialize random generator
        if use_seed:
            random.seed(seed)
        
        # Generate random value based on type
        value = None
        values = []
        
        if value_type == "number":
            value = random.uniform(float(min_value), float(max_value))
        
        elif value_type == "integer":
            value = random.randint(int(min_value), int(max_value))
        
        elif value_type == "boolean":
            value = random.choice([True, False])
        
        elif value_type == "string":
            if not characters:
                characters = string.ascii_letters + string.digits
            value = ''.join(random.choice(characters) for _ in range(length))
        
        elif value_type == "uuid":
            value = str(uuid.uuid4())
        
        elif value_type == "array":
            # Generate an array of random integers
            values = [random.randint(int(min_value), int(max_value)) for _ in range(length)]
            value = values[0] if values else None
        
        elif value_type == "color":
            # Generate a random hex color
            value = f"#{random.randint(0, 0xFFFFFF):06x}"
        
        elif value_type == "date":
            # Parse date strings
            try:
                date_min = datetime.datetime.strptime(date_min_str, "%Y-%m-%d").date()
                date_max = datetime.datetime.strptime(date_max_str, "%Y-%m-%d").date()
                
                # Calculate days between
                days_between = (date_max - date_min).days
                if days_between < 0:
                    # Swap if min is after max
                    date_min, date_max = date_max, date_min
                    days_between = abs(days_between)
                
                # Generate random date
                random_days = random.randint(0, days_between)
                random_date = date_min + datetime.timedelta(days=random_days)
                value = random_date.isoformat()
            except:
                # Fallback to current date
                value = datetime.date.today().isoformat()
        
        elif value_type == "item":
            # Split items string and choose one
            items = [item.strip() for item in items_str.split(",")]
            if items:
                value = random.choice(items)
            else:
                value = None
        
        else:
            value = None
        
        # If values is empty but we have a value, create a single-item array
        if not values and value is not None:
            values = [value]
        
        return {
            "value": value,
            "values": values,
            "seed": seed if use_seed else None
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        value_type = config.get("type", "")
        if not value_type:
            return "Type is required"
        
        if value_type in ["number", "integer"]:
            try:
                min_value = float(config.get("min", 0))
                max_value = float(config.get("max", 100))
                if min_value > max_value:
                    return "Min cannot be greater than max"
            except (ValueError, TypeError):
                return "Min and max must be numbers"
        
        if value_type in ["string", "array"]:
            try:
                length = int(config.get("length", 10))
                if length < 0:
                    return "Length must be a non-negative integer"
            except (ValueError, TypeError):
                return "Length must be a number"
        
        if value_type == "date":
            date_min = config.get("date_min", "")
            date_max = config.get("date_max", "")
            try:
                datetime.datetime.strptime(date_min, "%Y-%m-%d")
                datetime.datetime.strptime(date_max, "%Y-%m-%d")
            except ValueError:
                return "Dates must be in YYYY-MM-DD format"
        
        if value_type == "item" and not config.get("items", ""):
            return "Items list cannot be empty"
        
        return None
