"""
Enhanced Loop Node

This module provides an enhanced loop node for iterating over collections
or repeating operations a specified number of times.
"""

from typing import Dict, Any, Optional, ClassVar, List, Union

from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.enhanced_base_node import EnhancedBaseNode


class EnhancedLoop(EnhancedBaseNode):
    """
    Enhanced loop node for iterating over collections or repeating operations.
    
    This node supports different loop types: count, collection, and condition.
    """
    
    # Class variables
    __node_id__: ClassVar[str] = "core.loop"
    __node_version__: ClassVar[str] = "1.0.0"
    __node_category__: ClassVar[str] = NodeCategory.CONTROL_FLOW
    __node_description__: ClassVar[str] = "Iterate over collections or repeat operations"
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id=self.__node_id__,
            name="Loop",
            version=self.__node_version__,
            description=self.__node_description__,
            author="Workflow Builder",
            category=self.__node_category__,
            tags=["loop", "iteration", "repeat", "for", "while", "control flow", "core"],
            inputs=[
                PortDefinition(
                    id="collection",
                    name="Collection",
                    type="any",
                    description="The collection to iterate over (array, object, string)",
                    required=False,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="condition",
                    name="Condition",
                    type="boolean",
                    description="The condition for a while loop",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="reset",
                    name="Reset",
                    type="trigger",
                    description="Reset the loop to its initial state",
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
                    id="current_key",
                    name="Current Key",
                    type="any",
                    description="The current key or index in the iteration",
                    ui_properties={
                        "position": "right-center-top"
                    }
                ),
                PortDefinition(
                    id="index",
                    name="Index",
                    type="number",
                    description="The current iteration index (0-based)",
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
                    type="trigger",
                    description="Triggered when all iterations are complete",
                    ui_properties={
                        "position": "bottom-center"
                    }
                ),
                PortDefinition(
                    id="result",
                    name="Result",
                    type="array",
                    description="The collected results from all iterations",
                    ui_properties={
                        "position": "bottom-right"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="loop_type",
                    name="Loop Type",
                    type="select",
                    description="The type of loop to perform",
                    required=True,
                    default_value="collection",
                    options=[
                        {"label": "Collection (For Each)", "value": "collection"},
                        {"label": "Count (For)", "value": "count"},
                        {"label": "Condition (While)", "value": "condition"}
                    ]
                ),
                ConfigField(
                    id="count",
                    name="Count",
                    type="number",
                    description="The number of iterations for a count loop",
                    required=False,
                    default_value=10
                ),
                ConfigField(
                    id="start_index",
                    name="Start Index",
                    type="number",
                    description="The starting index for a count loop",
                    required=False,
                    default_value=0
                ),
                ConfigField(
                    id="step",
                    name="Step",
                    type="number",
                    description="The step size for a count loop",
                    required=False,
                    default_value=1
                ),
                ConfigField(
                    id="max_iterations",
                    name="Max Iterations",
                    type="number",
                    description="Maximum number of iterations for condition loops",
                    required=False,
                    default_value=1000
                ),
                ConfigField(
                    id="collect_results",
                    name="Collect Results",
                    type="boolean",
                    description="Whether to collect results from each iteration",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="break_on_error",
                    name="Break on Error",
                    type="boolean",
                    description="Whether to break the loop on error",
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
    
    def initialize(self) -> bool:
        """Initialize the node."""
        super().initialize()
        self._reset_state()
        return True
    
    def _reset_state(self) -> None:
        """Reset the internal state of the loop."""
        self._current_index = 0
        self._current_key = None
        self._current_item = None
        self._is_first = True
        self._is_last = False
        self._completed = False
        self._results = []
        self._iteration_count = 0
        self._collection = None
        self._keys = []
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the loop node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The loop outputs
        """
        # Check for reset trigger
        if inputs.get("reset", False):
            self._reset_state()
            return {
                "current_item": None,
                "current_key": None,
                "index": 0,
                "is_first": True,
                "is_last": False,
                "completed": False,
                "result": []
            }
        
        # Get configuration
        loop_type = config.get("loop_type", "collection")
        count = int(config.get("count", 10))
        start_index = int(config.get("start_index", 0))
        step = int(config.get("step", 1))
        max_iterations = int(config.get("max_iterations", 1000))
        collect_results = config.get("collect_results", True)
        
        # Initialize if this is the first execution or collection has changed
        if self._is_first or self._collection != inputs.get("collection"):
            self._reset_state()
            self._collection = inputs.get("collection")
            
            # Set up the loop based on type
            if loop_type == "collection":
                self._setup_collection_loop(self._collection)
            elif loop_type == "count":
                self._setup_count_loop(start_index, count, step)
            # For condition loops, we'll check the condition on each iteration
        
        # Check if we should continue the loop
        should_continue = False
        
        if loop_type == "collection":
            should_continue = self._current_index < len(self._keys)
        elif loop_type == "count":
            should_continue = self._current_index < len(self._keys)
        elif loop_type == "condition":
            condition = inputs.get("condition", False)
            should_continue = condition and self._iteration_count < max_iterations
        
        # If we should continue, get the current item
        if should_continue:
            self._iteration_count += 1
            
            if loop_type in ["collection", "count"]:
                self._current_key = self._keys[self._current_index]
                
                if loop_type == "collection" and isinstance(self._collection, (dict, list, tuple, str)):
                    if isinstance(self._collection, dict):
                        self._current_item = self._collection.get(self._current_key)
                    else:
                        self._current_item = self._collection[self._current_key]
                else:
                    self._current_item = self._current_key
            else:  # condition loop
                self._current_key = self._iteration_count
                self._current_item = inputs.get("collection")
            
            # Check if this is the last iteration
            if loop_type in ["collection", "count"]:
                self._is_last = self._current_index == len(self._keys) - 1
            else:  # condition loop
                # We can't know if it's the last iteration for a condition loop
                self._is_last = False
            
            # Collect result if configured
            if collect_results and "result" in inputs:
                self._results.append(inputs["result"])
            
            # Prepare for next iteration
            self._current_index += 1
            self._is_first = False
            
            return {
                "current_item": self._current_item,
                "current_key": self._current_key,
                "index": self._current_index - 1,  # 0-based index
                "is_first": self._is_first and self._current_index == 1,
                "is_last": self._is_last,
                "completed": False,
                "result": self._results
            }
        else:
            # Loop is completed
            self._completed = True
            
            return {
                "current_item": None,
                "current_key": None,
                "index": self._current_index,
                "is_first": False,
                "is_last": False,
                "completed": True,
                "result": self._results
            }
    
    def _setup_collection_loop(self, collection: Any) -> None:
        """
        Set up a collection loop.
        
        Args:
            collection: The collection to iterate over
        """
        if isinstance(collection, dict):
            self._keys = list(collection.keys())
        elif isinstance(collection, (list, tuple, str)):
            self._keys = list(range(len(collection)))
        else:
            # If not a collection, treat as a single item
            self._keys = [0]
            self._collection = [collection]
    
    def _setup_count_loop(self, start: int, count: int, step: int) -> None:
        """
        Set up a count loop.
        
        Args:
            start: The starting index
            count: The number of iterations
            step: The step size
        """
        end = start + (count * step)
        self._keys = list(range(start, end, step))
        self._collection = self._keys
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the node configuration.
        
        Args:
            config: The node configuration
            
        Returns:
            The validated and normalized configuration
            
        Raises:
            ValueError: If the configuration is invalid
        """
        # Validate loop_type
        loop_type = config.get("loop_type", "collection")
        if loop_type not in ["collection", "count", "condition"]:
            raise ValueError(f"Invalid loop type: {loop_type}")
        
        # Validate numeric values
        for key, default in [
            ("count", 10),
            ("start_index", 0),
            ("step", 1),
            ("max_iterations", 1000)
        ]:
            if key in config:
                try:
                    config[key] = int(config[key])
                    if key == "step" and config[key] == 0:
                        raise ValueError("Step cannot be zero")
                    if key in ["count", "max_iterations"] and config[key] < 0:
                        raise ValueError(f"{key} cannot be negative")
                except (ValueError, TypeError):
                    config[key] = default
        
        return config
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the node inputs.
        
        Args:
            inputs: The input values
            
        Returns:
            The validated and normalized inputs
            
        Raises:
            ValueError: If the inputs are invalid
        """
        # Ensure reset is a boolean
        if "reset" in inputs and not isinstance(inputs["reset"], bool):
            inputs["reset"] = bool(inputs["reset"])
        
        # Ensure condition is a boolean
        if "condition" in inputs and not isinstance(inputs["condition"], bool):
            inputs["condition"] = bool(inputs["condition"])
        
        return inputs
