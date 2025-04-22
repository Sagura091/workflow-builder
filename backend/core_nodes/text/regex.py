from typing import Dict, Any, List, Optional
import re
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class Regex(BaseNode):
    """
    A core node for applying regular expressions.
    
    This node allows users to perform regex operations on text.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.regex",
            name="Regex",
            version="1.0.0",
            description="Apply regular expressions",
            author="Workflow Builder",
            category=NodeCategory.TEXT,
            tags=["regex", "text", "pattern", "search", "replace", "core"],
            inputs=[
                PortDefinition(
                    id="text",
                    name="Text",
                    type="string",
                    description="The text to process",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="pattern",
                    name="Pattern",
                    type="string",
                    description="Regex pattern (overrides config)",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="replacement",
                    name="Replacement",
                    type="string",
                    description="Replacement text (for replace operation)",
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
                    description="The result of the regex operation",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="matches",
                    name="Matches",
                    type="array",
                    description="Array of matches",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="success",
                    name="Success",
                    type="boolean",
                    description="Whether the regex operation succeeded",
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
                    description="The regex operation to perform",
                    required=True,
                    default_value="match",
                    options=[
                        {"label": "Match", "value": "match"},
                        {"label": "Search", "value": "search"},
                        {"label": "Find All", "value": "findall"},
                        {"label": "Replace", "value": "replace"},
                        {"label": "Split", "value": "split"},
                        {"label": "Test", "value": "test"}
                    ]
                ),
                ConfigField(
                    id="pattern",
                    name="Pattern",
                    type="string",
                    description="The regex pattern",
                    required=True
                ),
                ConfigField(
                    id="replacement",
                    name="Replacement",
                    type="string",
                    description="Replacement text for replace operation",
                    required=False,
                    default_value=""
                ),
                ConfigField(
                    id="case_sensitive",
                    name="Case Sensitive",
                    type="boolean",
                    description="Whether the regex is case sensitive",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="multiline",
                    name="Multiline",
                    type="boolean",
                    description="Whether to enable multiline mode",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="global",
                    name="Global",
                    type="boolean",
                    description="Whether to replace all occurrences (for replace operation)",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="group",
                    name="Group",
                    type="number",
                    description="Capture group to return (0 for all)",
                    required=False,
                    default_value=0
                )
            ],
            ui_properties={
                "color": "#e67e22",
                "icon": "search",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the regex node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The result of the regex operation
        """
        # Get inputs
        text = inputs.get("text", "")
        input_pattern = inputs.get("pattern")
        input_replacement = inputs.get("replacement")
        
        # Get configuration
        operation = config.get("operation", "match")
        config_pattern = config.get("pattern", "")
        config_replacement = config.get("replacement", "")
        case_sensitive = config.get("case_sensitive", True)
        multiline = config.get("multiline", False)
        global_replace = config.get("global", True)
        group = int(config.get("group", 0))
        
        # Use input values if provided, otherwise use config
        pattern = input_pattern if input_pattern is not None else config_pattern
        replacement = input_replacement if input_replacement is not None else config_replacement
        
        # Convert text to string if it's not already
        if not isinstance(text, str):
            text = str(text)
        
        # Initialize outputs
        result = None
        matches = []
        success = False
        
        try:
            # Prepare regex flags
            flags = 0
            if not case_sensitive:
                flags |= re.IGNORECASE
            if multiline:
                flags |= re.MULTILINE
            
            # Compile regex
            regex = re.compile(pattern, flags)
            
            # Perform operation
            if operation == "match":
                # Match from start of string
                match = regex.match(text)
                if match:
                    success = True
                    if group > 0 and group <= len(match.groups()):
                        result = match.group(group)
                    else:
                        result = match.group(0)
                    
                    # Collect all groups
                    matches = list(match.groups())
                    matches.insert(0, match.group(0))  # Add full match at index 0
                else:
                    result = None
                    matches = []
            
            elif operation == "search":
                # Search anywhere in string
                match = regex.search(text)
                if match:
                    success = True
                    if group > 0 and group <= len(match.groups()):
                        result = match.group(group)
                    else:
                        result = match.group(0)
                    
                    # Collect all groups
                    matches = list(match.groups())
                    matches.insert(0, match.group(0))  # Add full match at index 0
                else:
                    result = None
                    matches = []
            
            elif operation == "findall":
                # Find all occurrences
                matches = regex.findall(text)
                success = True
                
                # Handle different return types from findall
                if matches:
                    if isinstance(matches[0], tuple):
                        # If groups are used, findall returns a list of tuples
                        if group > 0 and group <= len(matches[0]):
                            result = [match[group-1] for match in matches]
                        else:
                            result = matches
                    else:
                        # If no groups or only one group, findall returns a list of strings
                        result = matches
                else:
                    result = []
            
            elif operation == "replace":
                # Replace matches
                if global_replace:
                    result = regex.sub(replacement, text)
                else:
                    result = regex.sub(replacement, text, 1)
                
                # Find all matches for the matches output
                matches = regex.findall(text)
                success = True
            
            elif operation == "split":
                # Split text by pattern
                result = regex.split(text)
                matches = regex.findall(text)
                success = True
            
            elif operation == "test":
                # Test if pattern matches
                match = regex.search(text)
                result = bool(match)
                if match:
                    matches = list(match.groups())
                    matches.insert(0, match.group(0))  # Add full match at index 0
                success = True
            
            else:
                result = None
                matches = []
                success = False
        
        except Exception as e:
            result = str(e)
            matches = []
            success = False
        
        return {
            "result": result,
            "matches": matches,
            "success": success
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        operation = config.get("operation", "")
        if not operation:
            return "Operation is required"
        
        pattern = config.get("pattern", "")
        if not pattern:
            return "Pattern is required"
        
        # Validate regex pattern
        try:
            re.compile(pattern)
        except re.error as e:
            return f"Invalid regex pattern: {str(e)}"
        
        # Validate group
        try:
            group = int(config.get("group", 0))
            if group < 0:
                return "Group must be a non-negative integer"
        except ValueError:
            return "Group must be a number"
        
        return None
