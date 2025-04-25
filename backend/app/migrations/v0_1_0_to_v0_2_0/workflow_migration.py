"""
Workflow Migration from v0.1.0 to v0.2.0

This module provides migration steps for upgrading workflows from v0.1.0 to v0.2.0.
"""

from typing import Any, Dict, List

from backend.app.versioning.migration import WorkflowMigrationStep

class UpdateWorkflowMetadataMigration(WorkflowMigrationStep):
    """Migration step to update workflow metadata."""

    def __init__(self):
        super().__init__(
            source_version="0.1.0",
            target_version="0.2.0",
            description="Update workflow metadata structure",
            breaking=False
        )

    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the migration step."""
        result = data.copy()

        # Add new metadata fields if they don't exist
        if "metadata" not in result:
            result["metadata"] = {}

        metadata = result["metadata"]

        # Add created_at if it doesn't exist
        if "created_at" not in metadata:
            import datetime
            metadata["created_at"] = datetime.datetime.now().isoformat()

        # Add updated_at
        import datetime
        metadata["updated_at"] = datetime.datetime.now().isoformat()

        # Add version
        metadata["version"] = self.target_version

        # Add description if it doesn't exist
        if "description" not in metadata:
            metadata["description"] = f"Workflow migrated from v{self.source_version} to v{self.target_version}"

        return result


class UpdateNodeTypesMigration(WorkflowMigrationStep):
    """Migration step to update node types."""

    def __init__(self):
        super().__init__(
            source_version="0.1.0",
            target_version="0.2.0",
            description="Update node types to use enhanced type system",
            breaking=False
        )

    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the migration step."""
        result = data.copy()

        # Update node types
        if "nodes" in result:
            for node in result["nodes"]:
                # Update node type if needed
                self._update_node_type(node)

        return result

    def _update_node_type(self, node: Dict[str, Any]):
        """Update a node's type information."""
        # Get the node type
        node_type = node.get("type")

        # Update specific node types
        if node_type == "flow.branch":
            # Update inputs to use enhanced types
            if "inputs" in node:
                inputs = node["inputs"]
                if "condition" in inputs and inputs["condition"].get("type") == "boolean":
                    # No change needed, boolean type is the same in v0.2.0
                    pass

        # Add version information to the node
        node["version"] = self.target_version


class UpdateConnectionsMigration(WorkflowMigrationStep):
    """Migration step to update connections."""

    def __init__(self):
        super().__init__(
            source_version="0.1.0",
            target_version="0.2.0",
            description="Update connections to use enhanced type system",
            breaking=False
        )

    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the migration step."""
        result = data.copy()

        # Update connections
        if "connections" in result:
            for connection in result["connections"]:
                # Update connection type if needed
                self._update_connection_type(connection)

        return result

    def _update_connection_type(self, connection: Dict[str, Any]):
        """Update a connection's type information."""
        # Get the connection type
        connection_type = connection.get("type")

        # Update specific connection types
        if connection_type == "data":
            # Add version information to the connection
            connection["version"] = self.target_version


# List of migration steps
MIGRATION_STEPS = [
    UpdateWorkflowMetadataMigration(),
    UpdateNodeTypesMigration(),
    UpdateConnectionsMigration()
]
