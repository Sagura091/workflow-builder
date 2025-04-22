from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class NumberFormatter(BaseNode):
    """
    A core node for formatting numbers for display.
    
    This node allows users to format numbers in various ways.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.number_formatter",
            name="Number Formatter",
            version="1.0.0",
            description="Format numbers for display",
            author="Workflow Builder",
            category=NodeCategory.MATH,
            tags=["number", "format", "display", "core"],
            inputs=[
                PortDefinition(
                    id="number",
                    name="Number",
                    type="number",
                    description="The number to format",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="locale",
                    name="Locale",
                    type="string",
                    description="Locale for formatting (overrides config)",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="prefix",
                    name="Prefix",
                    type="string",
                    description="Text to add before the number",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="formatted",
                    name="Formatted",
                    type="string",
                    description="The formatted number",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="number",
                    name="Number",
                    type="number",
                    description="The original number (pass-through)",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="error",
                    name="Error",
                    type="string",
                    description="Error message if formatting failed",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="format_type",
                    name="Format Type",
                    type="select",
                    description="Type of number formatting",
                    required=True,
                    default_value="decimal",
                    options=[
                        {"label": "Decimal", "value": "decimal"},
                        {"label": "Currency", "value": "currency"},
                        {"label": "Percent", "value": "percent"},
                        {"label": "Scientific", "value": "scientific"},
                        {"label": "Compact", "value": "compact"},
                        {"label": "Custom", "value": "custom"}
                    ]
                ),
                ConfigField(
                    id="decimal_places",
                    name="Decimal Places",
                    type="number",
                    description="Number of decimal places",
                    required=False,
                    default_value=2
                ),
                ConfigField(
                    id="use_grouping",
                    name="Use Grouping",
                    type="boolean",
                    description="Whether to use thousand separators",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="currency",
                    name="Currency",
                    type="string",
                    description="Currency code (for currency format)",
                    required=False,
                    default_value="USD"
                ),
                ConfigField(
                    id="locale",
                    name="Locale",
                    type="string",
                    description="Locale for formatting",
                    required=False,
                    default_value="en-US"
                ),
                ConfigField(
                    id="custom_format",
                    name="Custom Format",
                    type="string",
                    description="Custom format string",
                    required=False,
                    default_value="0,0.00"
                ),
                ConfigField(
                    id="suffix",
                    name="Suffix",
                    type="string",
                    description="Text to add after the number",
                    required=False,
                    default_value=""
                )
            ],
            ui_properties={
                "color": "#3498db",
                "icon": "percentage",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the number formatter node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The formatted number
        """
        # Get inputs
        number = inputs.get("number")
        input_locale = inputs.get("locale")
        prefix = inputs.get("prefix", "")
        
        # Get configuration
        format_type = config.get("format_type", "decimal")
        decimal_places = int(config.get("decimal_places", 2))
        use_grouping = config.get("use_grouping", True)
        currency = config.get("currency", "USD")
        config_locale = config.get("locale", "en-US")
        custom_format = config.get("custom_format", "0,0.00")
        suffix = config.get("suffix", "")
        
        # Use input locale if provided, otherwise use config
        locale = input_locale if input_locale is not None else config_locale
        
        # Initialize outputs
        formatted = ""
        error = None
        
        try:
            # Convert to number if it's not already
            if number is None:
                number = 0
            else:
                try:
                    number = float(number)
                except (ValueError, TypeError):
                    error = "Input is not a valid number"
                    return {"formatted": str(number), "number": number, "error": error}
            
            # Format based on type
            if format_type == "decimal":
                try:
                    import locale as locale_module
                    locale_module.setlocale(locale_module.LC_ALL, locale)
                    if use_grouping:
                        formatted = locale_module.format_string(f"%.{decimal_places}f", number, grouping=True)
                    else:
                        formatted = locale_module.format_string(f"%.{decimal_places}f", number, grouping=False)
                except:
                    # Fallback if locale is not available
                    if use_grouping:
                        formatted = f"{number:,.{decimal_places}f}"
                    else:
                        formatted = f"{number:.{decimal_places}f}"
            
            elif format_type == "currency":
                try:
                    import locale as locale_module
                    locale_module.setlocale(locale_module.LC_ALL, locale)
                    formatted = locale_module.currency(number, symbol=True, grouping=use_grouping)
                except:
                    # Fallback if locale is not available
                    if use_grouping:
                        formatted = f"{currency} {number:,.{decimal_places}f}"
                    else:
                        formatted = f"{currency} {number:.{decimal_places}f}"
            
            elif format_type == "percent":
                try:
                    import locale as locale_module
                    locale_module.setlocale(locale_module.LC_ALL, locale)
                    # Convert to percentage
                    percent_value = number * 100
                    if use_grouping:
                        formatted = locale_module.format_string(f"%.{decimal_places}f%%", percent_value, grouping=True)
                    else:
                        formatted = locale_module.format_string(f"%.{decimal_places}f%%", percent_value, grouping=False)
                except:
                    # Fallback if locale is not available
                    if use_grouping:
                        formatted = f"{number*100:,.{decimal_places}f}%"
                    else:
                        formatted = f"{number*100:.{decimal_places}f}%"
            
            elif format_type == "scientific":
                formatted = f"{number:.{decimal_places}e}"
            
            elif format_type == "compact":
                # Simple compact format
                if abs(number) >= 1_000_000_000:
                    formatted = f"{number/1_000_000_000:.{decimal_places}f}B"
                elif abs(number) >= 1_000_000:
                    formatted = f"{number/1_000_000:.{decimal_places}f}M"
                elif abs(number) >= 1_000:
                    formatted = f"{number/1_000:.{decimal_places}f}K"
                else:
                    formatted = f"{number:.{decimal_places}f}"
            
            elif format_type == "custom":
                try:
                    # Try to use numeral.js style formatting
                    parts = custom_format.split(".")
                    
                    # Handle integer part
                    int_part = int(abs(number))
                    int_str = str(int_part)
                    
                    if "," in parts[0]:
                        # Add thousand separators
                        int_str = ""
                        orig = str(int_part)
                        for i, digit in enumerate(reversed(orig)):
                            if i > 0 and i % 3 == 0:
                                int_str = "," + int_str
                            int_str = digit + int_str
                    
                    # Handle decimal part
                    if len(parts) > 1:
                        decimal_format = parts[1]
                        decimal_places = len(decimal_format)
                        decimal_str = f"{abs(number) % 1:.{decimal_places}f}"[2:]  # Remove "0."
                    else:
                        decimal_str = ""
                    
                    # Combine parts
                    if decimal_str:
                        formatted = f"{int_str}.{decimal_str}"
                    else:
                        formatted = int_str
                    
                    # Add sign
                    if number < 0:
                        formatted = "-" + formatted
                except:
                    # Fallback to simple formatting
                    formatted = f"{number:.{decimal_places}f}"
            
            else:
                formatted = str(number)
            
            # Add prefix and suffix
            formatted = f"{prefix}{formatted}{suffix}"
        
        except Exception as e:
            error = str(e)
            formatted = str(number)
        
        return {
            "formatted": formatted,
            "number": number,
            "error": error
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        format_type = config.get("format_type", "")
        if not format_type:
            return "Format type is required"
        
        try:
            decimal_places = int(config.get("decimal_places", 2))
            if decimal_places < 0:
                return "Decimal places must be a non-negative integer"
        except (ValueError, TypeError):
            return "Decimal places must be a number"
        
        return None
