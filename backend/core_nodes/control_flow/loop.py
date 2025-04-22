from typing import Dict, Any, List, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class Loop(BaseNode):
    """
    A core node for iterating over data.
    
    This node can iterate over arrays and execute for each item.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.loop",
            name="Loop",
            version="1.0.0",
            description="Iterate over items in an array",
            author="Workflow Builder",
            category=NodeCategory.CONTROL_FLOW,
            tags=["loop", "iterate", "control flow", "array", "core"],
            inputs=[
                PortDefinition(
                    id="items",
                    name="Items",
                    type="array",
                    description="The array to iterate over",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="reset",
                    name="Reset",
                    type="boolean",
                    description="Reset the loop to start from the beginning",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="current_item",
                    name="Current Item",
                    type="any",
                    description="The current item in the iteration",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="index",
                    name="Index",
                    type="number",
                    description="The current index in the iteration",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="is_first",
                    name="Is First",
                    type="boolean",
                    description="Whether this is the first iteration",
                    ui_properties={
                        "position": "right-center-bottom"
                    }
                ),
                PortDefinition(
                    id="is_last",
                    name="Is Last",
                    type="boolean",
                    description="Whether this is the last iteration",
                    ui_properties={
                        "position": "right-bottom"
                    }
                ),
                PortDefinition(
                    id="completed",
                    name="Completed",
                    type="boolean",
                    description="Whether the loop has completed all iterations",
                    ui_properties={
                        "position": "right-bottom-extra"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="start_index",
                    name="Start Index",
                    type="number",
                    description="The index to start iterating from",
                    required=False,
                    default_value=0
                ),
                ConfigField(
                    id="max_iterations",
                    name="Max Iterations",
                    type="number",
                    description="Maximum number of iterations (0 for no limit)",
                    required=False,
                    default_value=0
                ),
                ConfigField(
                    id="step",
                    name="Step",
                    type="number",
                    description="Step size for iteration",
                    required=False,
                    default_value=1
                ),
                ConfigField(
                    id="auto_reset",
                    name="Auto Reset",
                    type="boolean",
                    description="Automatically reset the loop when it completes",
                    required=False,
                    default_value=True
                )
            ],
            ui_properties={
                "color": "#3498db",
                "icon": "sync",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the loop iteration.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The current iteration data
        """
        # Get input items
        items = inputs.get("items", [])
        reset = inputs.get("reset", False)
        
        if not isinstance(items, list):
            # Try to convert to list if possible
            try:
                items = list(items)
            except:
                items = [items]
        
        # Get configuration
        start_index = max(0, int(config.get("start_index", 0)))
        max_iterations = int(config.get("max_iterations", 0))
        step = max(1, int(config.get("step", 1)))
        auto_reset = config.get("auto_reset", True)
        
        # Get current iteration from context or start new
        context = inputs.get("__context__", {})
        
        # Reset if requested or if auto_reset is enabled and the loop has completed
        if reset or (auto_reset and context.get("completed", False)):
            current_index = start_index
        else:
            current_index = context.get("current_index", start_index)
        
        # Check if we've reached the end
        if current_index >= len(items) or (max_iterations > 0 and current_index >= start_index + max_iterations * step):
            # Loop has completed
            return {
                "current_item": None,
                "index": -1,
                "is_first": False,
                "is_last": True,
                "completed": True,
                "__context__": {"current_index": start_index, "completed": True}
            }
        
        # Get current item
        current_item = items[current_index]
        
        # Check if this is the first or last iteration
        is_first = current_index == start_index
        next_index = current_index + step
        is_last = next_index >= len(items) or (max_iterations > 0 and next_index >= start_index + max_iterations * step)
        
        # Update context for next iteration
        return {
            "current_item": current_item,
            "index": current_index,
            "is_first": is_first,
            "is_last": is_last,
            "completed": False,
            "__context__": {"current_index": next_index, "completed": is_last}
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        try:
            start_index = int(config.get("start_index", 0))
            if start_index < 0:
                return "Start index must be a non-negative integer"
            
            step = int(config.get("step", 1))
            if step <= 0:
                return "Step must be a positive integer"
            
            max_iterations = int(config.get("max_iterations", 0))
            if max_iterations < 0:
                return "Max iterations must be a non-negative integer"
            
            return None
        except ValueError:
            return "Invalid numeric value in configuration"
