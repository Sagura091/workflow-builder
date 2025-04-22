import json
from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class Begin(BaseNode):
    """
    A core node that serves as the starting point of a workflow.

    This node provides initial values and triggers the workflow execution.
    """

    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.begin",
            name="Begin",
            version="1.0.0",
            description="Starting point of the workflow",
            author="Workflow Builder",
            category=NodeCategory.CONTROL_FLOW,
            tags=["begin", "start", "entry point", "control flow", "core"],
            inputs=[],  # No inputs as this is the starting point
            outputs=[
                PortDefinition(
                    id="trigger",
                    name="Trigger",
                    type="trigger",
                    description="Triggers the workflow execution",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="workflow_id",
                    name="Workflow ID",
                    type="string",
                    description="The ID of the current workflow",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="timestamp",
                    name="Timestamp",
                    type="number",
                    description="The timestamp when the workflow started",
                    ui_properties={
                        "position": "right-bottom"
                    }
                ),
                PortDefinition(
                    id="initial_data",
                    name="Initial Data",
                    type="any",
                    description="Initial data for the workflow",
                    ui_properties={
                        "position": "right-bottom-extra"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="workflow_name",
                    name="Workflow Name",
                    type="string",
                    description="Name of the workflow",
                    required=False,
                    default_value="My Workflow"
                ),
                ConfigField(
                    id="initial_data",
                    name="Initial Data",
                    type="code",
                    description="Initial data for the workflow (JSON format)",
                    required=False,
                    default_value="{}"
                ),
                ConfigField(
                    id="description",
                    name="Description",
                    type="text",
                    description="Description of the workflow",
                    required=False
                ),
                ConfigField(
                    id="auto_start",
                    name="Auto Start",
                    type="boolean",
                    description="Whether to automatically start the workflow",
                    required=False,
                    default_value=True
                )
            ],
            ui_properties={
                "color": "#2ecc71",
                "icon": "play",
                "width": 240
            }
        )

    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the begin node.

        Args:
            config: The node configuration
            inputs: The input values (empty for begin node)

        Returns:
            The initial outputs for the workflow
        """
        import time
        import json
        import uuid

        # Get configuration
        workflow_name = config.get("workflow_name", "My Workflow")
        initial_data_str = config.get("initial_data", "{}")

        # Parse initial data
        try:
            initial_data = json.loads(initial_data_str)
        except json.JSONDecodeError:
            initial_data = {}

        # Get workflow context
        context = inputs.get("__context__", {})
        workflow_id = context.get("workflow_id", str(uuid.uuid4()))

        # Get current timestamp
        timestamp = int(time.time() * 1000)  # milliseconds

        return {
            "trigger": True,
            "workflow_id": workflow_id,
            "timestamp": timestamp,
            "initial_data": initial_data,
            "__context__": {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "start_time": timestamp
            }
        }

    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        initial_data_str = config.get("initial_data", "{}")

        # Validate initial data JSON
        try:
            json.loads(initial_data_str)
        except json.JSONDecodeError as e:
            return f"Invalid JSON in Initial Data: {str(e)}"

        return None
