from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class Trigger(BaseNode):
    """
    A core node for triggering workflow execution based on events.
    
    This node can trigger workflows based on various events like timers, webhooks, etc.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.trigger",
            name="Trigger",
            version="1.0.0",
            description="Execute a workflow based on events",
            author="Workflow Builder",
            category=NodeCategory.CONTROL_FLOW,
            tags=["trigger", "event", "schedule", "webhook", "control flow", "core"],
            inputs=[],  # No inputs as this is a trigger
            outputs=[
                PortDefinition(
                    id="trigger",
                    name="Trigger",
                    type="trigger",
                    description="Triggered when the event occurs",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="event_data",
                    name="Event Data",
                    type="object",
                    description="Data associated with the event",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="timestamp",
                    name="Timestamp",
                    type="number",
                    description="Timestamp when the event occurred",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="trigger_type",
                    name="Trigger Type",
                    type="select",
                    description="Type of trigger",
                    required=True,
                    default_value="manual",
                    options=[
                        {"label": "Manual", "value": "manual"},
                        {"label": "Schedule", "value": "schedule"},
                        {"label": "Webhook", "value": "webhook"},
                        {"label": "File Change", "value": "file_change"},
                        {"label": "Database Change", "value": "database_change"}
                    ]
                ),
                ConfigField(
                    id="schedule",
                    name="Schedule",
                    type="string",
                    description="Schedule in cron format (for schedule trigger)",
                    required=False
                ),
                ConfigField(
                    id="webhook_path",
                    name="Webhook Path",
                    type="string",
                    description="Path for the webhook (for webhook trigger)",
                    required=False
                ),
                ConfigField(
                    id="file_path",
                    name="File Path",
                    type="string",
                    description="Path to watch for changes (for file change trigger)",
                    required=False
                ),
                ConfigField(
                    id="database_query",
                    name="Database Query",
                    type="string",
                    description="Query to watch for changes (for database change trigger)",
                    required=False
                ),
                ConfigField(
                    id="description",
                    name="Description",
                    type="text",
                    description="Description of the trigger",
                    required=False
                )
            ],
            ui_properties={
                "color": "#e74c3c",
                "icon": "bolt",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the trigger node.
        
        Args:
            config: The node configuration
            inputs: The input values (empty for trigger node)
            
        Returns:
            The trigger outputs
        """
        import time
        
        # Get configuration
        trigger_type = config.get("trigger_type", "manual")
        
        # Get context
        context = inputs.get("__context__", {})
        event_data = context.get("event_data", {})
        
        # Get current timestamp
        timestamp = int(time.time() * 1000)  # milliseconds
        
        # For manual triggers, we just pass through the event data
        # Other trigger types would be handled by the workflow engine
        
        return {
            "trigger": True,
            "event_data": event_data,
            "timestamp": timestamp
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        trigger_type = config.get("trigger_type", "")
        
        if trigger_type == "schedule":
            schedule = config.get("schedule", "")
            if not schedule:
                return "Schedule is required for schedule trigger"
            
            # Basic cron format validation
            parts = schedule.split()
            if len(parts) != 5:
                return "Schedule must be in cron format (minute hour day month weekday)"
        
        elif trigger_type == "webhook":
            webhook_path = config.get("webhook_path", "")
            if not webhook_path:
                return "Webhook path is required for webhook trigger"
        
        elif trigger_type == "file_change":
            file_path = config.get("file_path", "")
            if not file_path:
                return "File path is required for file change trigger"
        
        elif trigger_type == "database_change":
            database_query = config.get("database_query", "")
            if not database_query:
                return "Database query is required for database change trigger"
        
        return None
