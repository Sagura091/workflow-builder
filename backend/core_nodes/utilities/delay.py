from typing import Dict, Any, Optional
import time
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class Delay(BaseNode):
    """
    A core node for adding delays in workflow execution.
    
    This node pauses the execution for a specified amount of time.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.delay",
            name="Delay",
            version="1.0.0",
            description="Pause execution for a specified time",
            author="Workflow Builder",
            category=NodeCategory.CONTROL_FLOW,
            tags=["delay", "pause", "wait", "timeout", "control flow", "core"],
            inputs=[
                PortDefinition(
                    id="trigger",
                    name="Trigger",
                    type="trigger",
                    description="Trigger to start the delay",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="duration",
                    name="Duration",
                    type="number",
                    description="Duration of the delay in seconds (overrides config)",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="pass_through",
                    name="Pass Through",
                    type="any",
                    description="Data to pass through the delay",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="trigger",
                    name="Trigger",
                    type="trigger",
                    description="Triggered after the delay",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="pass_through",
                    name="Pass Through",
                    type="any",
                    description="Data passed through the delay",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="duration",
                    name="Actual Duration",
                    type="number",
                    description="Actual duration of the delay in seconds",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="duration",
                    name="Duration",
                    type="number",
                    description="Duration of the delay in seconds",
                    required=True,
                    default_value=1.0
                ),
                ConfigField(
                    id="unit",
                    name="Time Unit",
                    type="select",
                    description="Unit of time for the duration",
                    required=False,
                    default_value="seconds",
                    options=[
                        {"label": "Seconds", "value": "seconds"},
                        {"label": "Milliseconds", "value": "milliseconds"},
                        {"label": "Minutes", "value": "minutes"}
                    ]
                ),
                ConfigField(
                    id="skip_in_test",
                    name="Skip in Test Mode",
                    type="boolean",
                    description="Whether to skip the delay in test mode",
                    required=False,
                    default_value=True
                )
            ],
            ui_properties={
                "color": "#3498db",
                "icon": "clock",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the delay node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The outputs after the delay
        """
        # Get inputs
        trigger = inputs.get("trigger", False)
        input_duration = inputs.get("duration")
        pass_through = inputs.get("pass_through")
        
        # Get configuration
        config_duration = config.get("duration", 1.0)
        unit = config.get("unit", "seconds")
        skip_in_test = config.get("skip_in_test", True)
        
        # Use input duration if provided, otherwise use config
        duration = input_duration if input_duration is not None else config_duration
        
        # Convert duration to seconds based on unit
        if unit == "milliseconds":
            duration_seconds = duration / 1000.0
        elif unit == "minutes":
            duration_seconds = duration * 60.0
        else:  # seconds
            duration_seconds = duration
        
        # Get context
        context = inputs.get("__context__", {})
        test_mode = context.get("test_mode", False)
        
        # Skip delay in test mode if configured
        if test_mode and skip_in_test:
            actual_duration = 0
        else:
            # Perform the delay
            start_time = time.time()
            time.sleep(duration_seconds)
            actual_duration = time.time() - start_time
        
        return {
            "trigger": trigger,
            "pass_through": pass_through,
            "duration": actual_duration
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        try:
            duration = float(config.get("duration", 1.0))
            if duration < 0:
                return "Duration must be a non-negative number"
        except ValueError:
            return "Duration must be a number"
        
        return None
