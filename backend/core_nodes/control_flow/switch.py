from typing import Dict, Any, List, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class Switch(BaseNode):
    """
    A core node for multi-way branching.
    
    This node routes data based on a value matching different cases.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.switch",
            name="Switch",
            version="1.0.0",
            description="Route data based on matching cases",
            author="Workflow Builder",
            category=NodeCategory.CONTROL_FLOW,
            tags=["switch", "case", "branch", "control flow", "core"],
            inputs=[
                PortDefinition(
                    id="value",
                    name="Value",
                    type="any",
                    description="The value to match against cases",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="case1",
                    name="Case 1",
                    type="any",
                    description="Output when value matches Case 1",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="case2",
                    name="Case 2",
                    type="any",
                    description="Output when value matches Case 2",
                    ui_properties={
                        "position": "right-center-top"
                    }
                ),
                PortDefinition(
                    id="case3",
                    name="Case 3",
                    type="any",
                    description="Output when value matches Case 3",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="default",
                    name="Default",
                    type="any",
                    description="Output when value doesn't match any case",
                    ui_properties={
                        "position": "right-bottom"
                    }
                ),
                PortDefinition(
                    id="matched_case",
                    name="Matched Case",
                    type="string",
                    description="The name of the case that matched",
                    ui_properties={
                        "position": "right-center-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="case1_value",
                    name="Case 1 Value",
                    type="string",
                    description="Value to match for Case 1",
                    required=True
                ),
                ConfigField(
                    id="case2_value",
                    name="Case 2 Value",
                    type="string",
                    description="Value to match for Case 2",
                    required=False
                ),
                ConfigField(
                    id="case3_value",
                    name="Case 3 Value",
                    type="string",
                    description="Value to match for Case 3",
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
                    id="pass_through",
                    name="Pass Through Value",
                    type="select",
                    description="Which value to pass through the outputs",
                    required=False,
                    default_value="value",
                    options=[
                        {"label": "Input Value", "value": "value"},
                        {"label": "Case Value", "value": "case_value"},
                        {"label": "Custom Value", "value": "custom"}
                    ]
                ),
                ConfigField(
                    id="custom_value",
                    name="Custom Value",
                    type="string",
                    description="Custom value to pass through (when Pass Through Value is 'custom')",
                    required=False
                )
            ],
            ui_properties={
                "color": "#9b59b6",
                "icon": "random",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the switch branching.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The branched outputs
        """
        # Get input value
        value = inputs.get("value")
        if value is None:
            value = ""
        
        # Convert to string for comparison
        if not isinstance(value, str):
            value = str(value)
        
        # Get configuration
        case1_value = config.get("case1_value", "")
        case2_value = config.get("case2_value", "")
        case3_value = config.get("case3_value", "")
        case_sensitive = config.get("case_sensitive", False)
        pass_through = config.get("pass_through", "value")
        custom_value = config.get("custom_value", "")
        
        # Prepare for case-insensitive comparison if needed
        compare_value = value
        if not case_sensitive:
            compare_value = value.lower()
            case1_value = case1_value.lower() if isinstance(case1_value, str) else case1_value
            case2_value = case2_value.lower() if isinstance(case2_value, str) else case2_value
            case3_value = case3_value.lower() if isinstance(case3_value, str) else case3_value
        
        # Determine which value to pass through
        if pass_through == "value":
            pass_value = inputs.get("value")
        elif pass_through == "case_value":
            # Will be set based on matched case
            pass_value = None
        else:  # custom
            pass_value = custom_value
        
        # Initialize outputs
        outputs = {
            "case1": None,
            "case2": None,
            "case3": None,
            "default": None,
            "matched_case": "none"
        }
        
        # Match cases
        if compare_value == case1_value:
            if pass_through == "case_value":
                pass_value = case1_value
            outputs["case1"] = pass_value
            outputs["matched_case"] = "case1"
        elif case2_value and compare_value == case2_value:
            if pass_through == "case_value":
                pass_value = case2_value
            outputs["case2"] = pass_value
            outputs["matched_case"] = "case2"
        elif case3_value and compare_value == case3_value:
            if pass_through == "case_value":
                pass_value = case3_value
            outputs["case3"] = pass_value
            outputs["matched_case"] = "case3"
        else:
            outputs["default"] = pass_value
            outputs["matched_case"] = "default"
        
        return outputs
