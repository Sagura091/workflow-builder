"""
For Loop Node

This node iterates over a list of items and executes connected nodes for each item.
"""

from typing import Dict, Any, Optional
from backend.core_nodes.base_node import BaseNode
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class ForLoop(BaseNode):
    """
    Iterates over a list of items and executes connected nodes for each item.
    """

    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.for_loop",
            name="For Loop",
            version="1.0.0",
            description="Iterate over a list of items",
            author="Workflow Builder",
            category=NodeCategory.CONTROL_FLOW,
            tags=["loop", "iteration", "control flow", "core"],
            inputs=[
                PortDefinition(
                    id="items",
                    name="Items",
                    type="array",
                    description="Items to iterate over",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="trigger",
                    name="Trigger",
                    type="trigger",
                    description="Execution trigger",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="completed",
                    name="Completed",
                    type="trigger",
                    description="Triggered when loop completes",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="current_item",
                    name="Current Item",
                    type="any",
                    description="Current item in the iteration",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="index",
                    name="Index",
                    type="number",
                    description="Current iteration index",
                    ui_properties={
                        "position": "right-bottom"
                    }
                ),
                PortDefinition(
                    id="results",
                    name="Results",
                    type="array",
                    description="Collected results from all iterations",
                    ui_properties={
                        "position": "right-bottom-extra"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="item_variable",
                    name="Item Variable Name",
                    type="string",
                    description="Name of the variable to store the current item",
                    required=False,
                    default_value="item"
                ),
                ConfigField(
                    id="index_variable",
                    name="Index Variable Name",
                    type="string",
                    description="Name of the variable to store the current index",
                    required=False,
                    default_value="index"
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
                    id="result_variable",
                    name="Result Variable Name",
                    type="string",
                    description="Name of the variable to store the loop results",
                    required=False,
                    default_value="loop_results"
                )
            ],
            ui_properties={
                "color": "#e74c3c",
                "icon": "sync",
                "width": 240
            }
        )

    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node.

        Args:
            config: The node configuration
            inputs: The input values

        Returns:
            The output values
        """
        items = inputs.get("items", [])
        item_var_name = config.get("item_variable", "item")
        index_var_name = config.get("index_variable", "index")
        collect_results = config.get("collect_results", True)
        result_var_name = config.get("result_variable", "loop_results")

        # Get workflow context from inputs
        workflow_context = inputs.get("__context__")

        # Default return if no workflow context
        if not workflow_context:
            return {
                "completed": True,
                "current_item": None,
                "index": -1,
                "results": []
            }

        results = []

        # Get connected nodes (the loop body)
        body_node_ids = workflow_context.get_connected_nodes(self.id, "current_item")

        # Iterate over items
        for index, item in enumerate(items):
            # Set variables for this iteration
            workflow_context.variables.set(item_var_name, item)
            workflow_context.variables.set(index_var_name, index)

            # Execute body nodes
            iteration_results = []
            for node_id in body_node_ids:
                node_result = workflow_context.execute_node(node_id)
                if collect_results and node_result:
                    iteration_results.append(node_result)

            if collect_results:
                results.append(iteration_results)

        # Store results in a variable if configured
        if collect_results and result_var_name:
            workflow_context.variables.set(result_var_name, results)

        return {
            "completed": True,
            "current_item": None,  # Reset after loop completes
            "index": len(items),   # Final index after loop
            "results": results,
            "__context__": workflow_context  # Pass context to next node
        }
