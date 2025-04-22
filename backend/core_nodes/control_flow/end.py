from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class End(BaseNode):
    """
    A core node that serves as the ending point of a workflow.
    
    This node collects final results and signals the completion of the workflow.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.end",
            name="End",
            version="1.0.0",
            description="Ending point of the workflow",
            author="Workflow Builder",
            category=NodeCategory.CONTROL_FLOW,
            tags=["end", "finish", "exit point", "control flow", "core"],
            inputs=[
                PortDefinition(
                    id="trigger",
                    name="Trigger",
                    type="trigger",
                    description="Triggers the workflow completion",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="result",
                    name="Result",
                    type="any",
                    description="The final result of the workflow",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="status",
                    name="Status",
                    type="string",
                    description="The status of the workflow completion",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="workflow_id",
                    name="Workflow ID",
                    type="string",
                    description="The ID of the completed workflow",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="execution_time",
                    name="Execution Time",
                    type="number",
                    description="The total execution time in milliseconds",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="final_result",
                    name="Final Result",
                    type="any",
                    description="The final result of the workflow",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="success_message",
                    name="Success Message",
                    type="string",
                    description="Message to display on successful completion",
                    required=False,
                    default_value="Workflow completed successfully"
                ),
                ConfigField(
                    id="error_message",
                    name="Error Message",
                    type="string",
                    description="Message to display on error",
                    required=False,
                    default_value="Workflow completed with errors"
                ),
                ConfigField(
                    id="log_result",
                    name="Log Result",
                    type="boolean",
                    description="Whether to log the final result",
                    required=False,
                    default_value=True
                )
            ],
            ui_properties={
                "color": "#e74c3c",
                "icon": "stop",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the end node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The final outputs for the workflow
        """
        import time
        
        # Get inputs
        trigger = inputs.get("trigger", False)
        result = inputs.get("result")
        status = inputs.get("status", "success")
        
        # Get configuration
        success_message = config.get("success_message", "Workflow completed successfully")
        error_message = config.get("error_message", "Workflow completed with errors")
        log_result = config.get("log_result", True)
        
        # Get workflow context
        context = inputs.get("__context__", {})
        workflow_id = context.get("workflow_id", "unknown")
        start_time = context.get("start_time", 0)
        
        # Calculate execution time
        current_time = int(time.time() * 1000)  # milliseconds
        execution_time = current_time - start_time if start_time > 0 else 0
        
        # Determine final message
        final_message = success_message if status == "success" else error_message
        
        # Log result if configured
        if log_result:
            print(f"Workflow {workflow_id} completed with status: {status}")
            print(f"Execution time: {execution_time} ms")
            print(f"Result: {result}")
        
        return {
            "workflow_id": workflow_id,
            "execution_time": execution_time,
            "final_result": {
                "result": result,
                "status": status,
                "message": final_message,
                "execution_time": execution_time
            }
        }
