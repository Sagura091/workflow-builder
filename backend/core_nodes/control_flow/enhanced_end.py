"""
Enhanced End Node

This module provides an enhanced end node that serves as the ending point
of a workflow.
"""

import time
from typing import Dict, Any, Optional, ClassVar

from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.enhanced_base_node import EnhancedBaseNode


class EnhancedEnd(EnhancedBaseNode):
    """
    Enhanced end node that serves as the ending point of a workflow.
    
    This node collects final results and signals the completion of the workflow.
    """
    
    # Class variables
    __node_id__: ClassVar[str] = "core.end"
    __node_version__: ClassVar[str] = "1.0.0"
    __node_category__: ClassVar[str] = NodeCategory.CONTROL_FLOW
    __node_description__: ClassVar[str] = "Ending point of the workflow"
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id=self.__node_id__,
            name="End",
            version=self.__node_version__,
            description=self.__node_description__,
            author="Workflow Builder",
            category=self.__node_category__,
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
                    description="The status of the workflow (success, error, etc.)",
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
                    description="The total execution time of the workflow in milliseconds",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="result",
                    name="Result",
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
                    description="Message to display when the workflow completes successfully",
                    required=False,
                    default_value="Workflow completed successfully"
                ),
                ConfigField(
                    id="error_message",
                    name="Error Message",
                    type="string",
                    description="Message to display when the workflow completes with errors",
                    required=False,
                    default_value="Workflow completed with errors"
                ),
                ConfigField(
                    id="log_result",
                    name="Log Result",
                    type="boolean",
                    description="Whether to log the result of the workflow",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="notify_completion",
                    name="Notify Completion",
                    type="boolean",
                    description="Whether to send a notification when the workflow completes",
                    required=False,
                    default_value=False
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
        # Get inputs
        trigger = inputs.get("trigger", False)
        result = inputs.get("result")
        status = inputs.get("status", "success")
        
        # Get configuration
        success_message = config.get("success_message", "Workflow completed successfully")
        error_message = config.get("error_message", "Workflow completed with errors")
        log_result = config.get("log_result", True)
        notify_completion = config.get("notify_completion", False)
        
        # Get workflow context
        context = inputs.get("__context__", {})
        workflow_id = context.get("workflow_id", "unknown")
        start_time = context.get("start_time", 0)
        
        # Calculate execution time
        current_time = int(time.time() * 1000)  # milliseconds
        execution_time = current_time - start_time if start_time > 0 else 0
        
        # Determine message based on status
        message = success_message if status == "success" else error_message
        
        # Log result if configured
        if log_result:
            # In a real implementation, this would log to a database or file
            pass
        
        # Send notification if configured
        if notify_completion:
            # In a real implementation, this would send a notification
            pass
        
        return {
            "workflow_id": workflow_id,
            "execution_time": execution_time,
            "result": result,
            "status": status,
            "message": message,
            "__context__": {
                "workflow_id": workflow_id,
                "end_time": current_time,
                "execution_time": execution_time,
                "status": status
            }
        }
    
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
        # Ensure trigger is a boolean
        if "trigger" in inputs and not isinstance(inputs["trigger"], bool):
            inputs["trigger"] = bool(inputs["trigger"])
        
        # Ensure status is a string
        if "status" in inputs and not isinstance(inputs["status"], str):
            inputs["status"] = str(inputs["status"])
        
        # Validate status value
        if "status" in inputs and inputs["status"] not in ["success", "error", "warning", "info"]:
            inputs["status"] = "success"
        
        return inputs
