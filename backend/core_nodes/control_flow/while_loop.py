"""
While Loop Node

This node executes connected nodes while a condition is true.
"""

from typing import Dict, Any, Optional
from backend.core_nodes.base_node import BaseNode
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class WhileLoop(BaseNode):
    """
    Executes connected nodes while a condition is true.
    """

    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.while_loop",
            name="While Loop",
            version="1.0.0",
            description="Execute nodes while a condition is true",
            author="Workflow Builder",
            category=NodeCategory.CONTROL_FLOW,
            tags=["loop", "iteration", "control flow", "core"],
            inputs=[
                PortDefinition(
                    id="condition",
                    name="Condition",
                    type="boolean",
                    description="Loop condition",
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
                    id="iteration",
                    name="Iteration",
                    type="trigger",
                    description="Triggered for each iteration",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="iteration_count",
                    name="Iteration Count",
                    type="number",
                    description="Number of iterations completed",
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
                    id="max_iterations",
                    name="Maximum Iterations",
                    type="number",
                    description="Maximum number of iterations to prevent infinite loops",
                    required=False,
                    default_value=100
                ),
                ConfigField(
                    id="iteration_variable",
                    name="Iteration Variable Name",
                    type="string",
                    description="Name of the variable to store the current iteration",
                    required=False,
                    default_value="iteration"
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
                "color": "#9b59b6",
                "icon": "sync-alt",
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
        condition = inputs.get("condition", False)
        max_iterations = config.get("max_iterations", 100)
        iteration_var_name = config.get("iteration_variable", "iteration")
        collect_results = config.get("collect_results", True)
        result_var_name = config.get("result_variable", "loop_results")

        # Get workflow context from inputs
        workflow_context = inputs.get("__context__")

        # Default return if no workflow context
        if not workflow_context:
            return {
                "completed": True,
                "iteration_count": 0,
                "results": []
            }

        results = []
        iteration_count = 0

        # Get connected nodes (the loop body)
        body_node_ids = workflow_context.get_connected_nodes(self.id, "iteration")

        # Get the condition node
        condition_node_id = workflow_context.get_input_node(self.id, "condition")

        # Execute the loop
        while condition and iteration_count < max_iterations:
            # Set variables for this iteration
            workflow_context.variables.set(iteration_var_name, iteration_count)

            # Execute body nodes
            iteration_results = []
            for node_id in body_node_ids:
                node_result = workflow_context.execute_node(node_id)
                if collect_results and node_result:
                    iteration_results.append(node_result)

            if collect_results:
                results.append(iteration_results)

            # Update condition
            if condition_node_id:
                condition_result = workflow_context.execute_node(condition_node_id)
                if condition_result:
                    condition = condition_result.get("value", False)
            else:
                condition = False

            iteration_count += 1

        # Store results in a variable if configured
        if collect_results and result_var_name:
            workflow_context.variables.set(result_var_name, results)

        return {
            "completed": True,
            "iteration_count": iteration_count,
            "results": results,
            "__context__": workflow_context  # Pass context to next node
        }
