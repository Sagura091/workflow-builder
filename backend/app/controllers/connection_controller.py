from typing import Dict, Any, List
from backend.app.services.connection_suggestion_service import ConnectionSuggestionService
from backend.app.services.plugin_manager import PluginManager
from backend.app.services.type_registry import TypeRegistry

class ConnectionController:
    def __init__(self, plugin_manager: PluginManager, type_registry: TypeRegistry):
        self.plugin_manager = plugin_manager
        self.type_registry = type_registry
        self.suggestion_service = ConnectionSuggestionService(plugin_manager, type_registry)
    
    def suggest_connections(self, workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest possible connections in a workflow.
        
        Args:
            workflow: The workflow data
            
        Returns:
            List of connection suggestions
        """
        return self.suggestion_service.suggest_connections(workflow)
    
    def check_connection_compatibility(self, source_type: str, target_type: str) -> Dict[str, Any]:
        """
        Check if two types are compatible for connection.
        
        Args:
            source_type: Source port type
            target_type: Target port type
            
        Returns:
            Compatibility information
        """
        is_compatible = self.type_registry.is_compatible(source_type, target_type)
        
        return {
            "compatible": is_compatible,
            "sourceType": source_type,
            "targetType": target_type,
            "message": f"Types are {'compatible' if is_compatible else 'not compatible'}"
        }
    
    def validate_connection(self, connection: Dict[str, Any], workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a connection in a workflow.
        
        Args:
            connection: The connection to validate
            workflow: The workflow data
            
        Returns:
            Validation results
        """
        source_id = connection.get("source")
        target_id = connection.get("target")
        source_port = connection.get("sourceHandle")
        target_port = connection.get("targetHandle")
        
        # Find source and target nodes
        nodes = workflow.get("nodes", [])
        source_node = next((n for n in nodes if n["id"] == source_id), None)
        target_node = next((n for n in nodes if n["id"] == target_id), None)
        
        if not source_node:
            return {
                "valid": False,
                "message": f"Source node '{source_id}' not found"
            }
        
        if not target_node:
            return {
                "valid": False,
                "message": f"Target node '{target_id}' not found"
            }
        
        # Get node metadata
        source_type = source_node.get("type")
        target_type = target_node.get("type")
        
        source_metadata = self.plugin_manager.get_plugin_metadata(source_type)
        target_metadata = self.plugin_manager.get_plugin_metadata(target_type)
        
        if not source_metadata:
            return {
                "valid": False,
                "message": f"Source node type '{source_type}' not found"
            }
        
        if not target_metadata:
            return {
                "valid": False,
                "message": f"Target node type '{target_type}' not found"
            }
        
        # Find port definitions
        source_port_def = next((p for p in source_metadata.outputs if p.id == source_port), None)
        target_port_def = next((p for p in target_metadata.inputs if p.id == target_port), None)
        
        if not source_port_def:
            return {
                "valid": False,
                "message": f"Source port '{source_port}' not found on node '{source_id}'"
            }
        
        if not target_port_def:
            return {
                "valid": False,
                "message": f"Target port '{target_port}' not found on node '{target_id}'"
            }
        
        # Check type compatibility
        source_type = source_port_def.type
        target_type = target_port_def.type
        
        is_compatible = self.type_registry.is_compatible(source_type, target_type)
        
        if not is_compatible:
            return {
                "valid": False,
                "message": f"Incompatible types: {source_type} → {target_type}",
                "details": {
                    "sourceType": source_type,
                    "targetType": target_type
                }
            }
        
        # Check if target port already has a connection
        existing_connections = workflow.get("connections", [])
        for conn in existing_connections:
            if conn.get("target") == target_id and conn.get("targetHandle") == target_port:
                # Skip if this is the same connection
                if conn.get("source") == source_id and conn.get("sourceHandle") == source_port:
                    continue
                
                # Check if the port accepts multiple connections
                if not target_port_def.accepts_multiple:
                    return {
                        "valid": False,
                        "message": f"Target port '{target_port}' already has a connection and does not accept multiple connections"
                    }
        
        return {
            "valid": True,
            "message": "Connection is valid"
        }
