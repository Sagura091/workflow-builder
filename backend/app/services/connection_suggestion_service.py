from typing import Dict, Any, List, Optional
from backend.app.services.plugin_manager import PluginManager
from backend.app.services.type_registry import TypeRegistry

class ConnectionSuggestionService:
    def __init__(self, plugin_manager: PluginManager, type_registry: TypeRegistry):
        self.plugin_manager = plugin_manager
        self.type_registry = type_registry
    
    def suggest_connections(self, workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest possible connections in a workflow.
        
        Args:
            workflow: The workflow data
            
        Returns:
            List of connection suggestions
        """
        suggestions = []
        
        # Get all nodes
        nodes = workflow.get("nodes", [])
        nodes_by_id = {node["id"]: node for node in nodes}
        
        # Get existing connections
        existing_connections = set()
        for conn in workflow.get("connections", []):
            source_id = conn.get("source")
            target_id = conn.get("target")
            source_port = conn.get("sourceHandle")
            target_port = conn.get("targetHandle")
            existing_connections.add((source_id, source_port, target_id, target_port))
        
        # For each node output, find compatible inputs
        for source_node in nodes:
            source_id = source_node["id"]
            source_type = source_node.get("type")
            
            # Get source plugin metadata
            source_metadata = self.plugin_manager.get_plugin_metadata(source_type)
            if not source_metadata:
                continue
            
            # Check each output port
            for output_port in source_metadata.outputs:
                output_type = output_port.type
                
                # Find compatible input ports on other nodes
                for target_node in nodes:
                    target_id = target_node["id"]
                    
                    # Skip self-connections
                    if target_id == source_id:
                        continue
                    
                    target_type = target_node.get("type")
                    
                    # Get target plugin metadata
                    target_metadata = self.plugin_manager.get_plugin_metadata(target_type)
                    if not target_metadata:
                        continue
                    
                    # Check each input port
                    for input_port in target_metadata.inputs:
                        input_type = input_port.type
                        
                        # Skip if connection already exists
                        if (source_id, output_port.id, target_id, input_port.id) in existing_connections:
                            continue
                        
                        # Check type compatibility
                        if self.type_registry.is_compatible(output_type, input_type):
                            # Calculate relevance score
                            relevance = self._calculate_relevance(
                                source_type, output_port.id, 
                                target_type, input_port.id
                            )
                            
                            suggestions.append({
                                "source": {
                                    "nodeId": source_id,
                                    "port": output_port.id
                                },
                                "target": {
                                    "nodeId": target_id,
                                    "port": input_port.id
                                },
                                "relevance": relevance,
                                "description": f"Connect {source_metadata.name}'s {output_port.name} to {target_metadata.name}'s {input_port.name}",
                                "types": {
                                    "sourceType": output_type,
                                    "targetType": input_type
                                }
                            })
        
        # Sort by relevance
        suggestions.sort(key=lambda x: x["relevance"], reverse=True)
        
        return suggestions
    
    def _calculate_relevance(self, source_type: str, source_port: str, 
                            target_type: str, target_port: str) -> float:
        """
        Calculate relevance score for a connection.
        
        Args:
            source_type: Source node type
            source_port: Source port ID
            target_type: Target node type
            target_port: Target port ID
            
        Returns:
            Relevance score (0-1)
        """
        # Base relevance
        relevance = 0.5
        
        # Exact type match is more relevant
        source_metadata = self.plugin_manager.get_plugin_metadata(source_type)
        target_metadata = self.plugin_manager.get_plugin_metadata(target_type)
        
        if source_metadata and target_metadata:
            source_port_def = next((p for p in source_metadata.outputs if p.id == source_port), None)
            target_port_def = next((p for p in target_metadata.inputs if p.id == target_port), None)
            
            if source_port_def and target_port_def:
                # Exact type match
                if source_port_def.type == target_port_def.type:
                    relevance += 0.3
                
                # Name similarity
                if source_port_def.name.lower() in target_port_def.name.lower() or \
                   target_port_def.name.lower() in source_port_def.name.lower():
                    relevance += 0.1
                
                # Required inputs are more relevant
                if target_port_def.required:
                    relevance += 0.1
        
        # Common patterns (could be expanded based on usage analytics)
        common_patterns = [
            # Data flow patterns
            ("data_loader", "data_processor"),
            ("data_processor", "data_visualizer"),
            ("data_loader", "model_trainer"),
            ("model_trainer", "model_evaluator"),
            
            # Text processing patterns
            ("text_processor", "text_analyzer"),
            ("text_processor", "text_visualizer"),
            
            # Image processing patterns
            ("image_loader", "image_processor"),
            ("image_processor", "image_visualizer")
        ]
        
        if any(source_type.startswith(s) and target_type.startswith(t) for s, t in common_patterns):
            relevance += 0.1
        
        # Ensure relevance is between 0 and 1
        return min(max(relevance, 0), 1)
