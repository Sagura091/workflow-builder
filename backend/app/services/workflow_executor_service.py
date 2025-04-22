"""
Workflow Executor Service

This module provides functionality to execute workflows by building a DAG from nodes and edges.
"""

import networkx as nx
from typing import Dict, List, Any

from backend.app.services.plugin_loader_service import load_plugin
from backend.app.services.rules_engine_service import validate_connection

class WorkflowExecutorService:
    """Service for executing workflows."""
    
    def topological_sort(self, nodes: List[Any], edges: List[Any]) -> List[str]:
        """
        Perform a topological sort on the workflow graph.
        
        Args:
            nodes: List of nodes in the workflow
            edges: List of edges in the workflow
            
        Returns:
            List of node IDs in topological order
        """
        G = nx.DiGraph()
        for node in nodes:
            G.add_node(node.id, type=node.type, config=node.config)
        for edge in edges:
            G.add_edge(edge.source, edge.target)
        return list(nx.topological_sort(G))
    
    def validate_graph(self, nodes: List[Any], edges: List[Any]) -> None:
        """
        Validate the workflow graph by checking that all connections are valid.
        
        Args:
            nodes: List of nodes in the workflow
            edges: List of edges in the workflow
            
        Raises:
            ValueError: If any connection is invalid
        """
        node_map = {node.id: node for node in nodes}
        for edge in edges:
            source = node_map[edge.source]
            target = node_map[edge.target]
            source_plugin = load_plugin(source.type)
            target_plugin = load_plugin(target.type)
            
            source_outputs = source_plugin.__plugin_meta__.get("outputs", {})
            target_inputs = target_plugin.__plugin_meta__.get("inputs", {})
            
            for out_key, out_type in source_outputs.items():
                for in_key, in_type in target_inputs.items():
                    if not validate_connection(out_type, in_type):
                        raise ValueError(f"Invalid connection from {source.id}.{out_key} to {target.id}.{in_key}")
    
    def execute_workflow(self, nodes: List[Any], edges: List[Any]) -> Dict[str, Any]:
        """
        Execute a workflow by running each node in topological order.
        
        Args:
            nodes: List of nodes in the workflow
            edges: List of edges in the workflow
            
        Returns:
            Dictionary containing the results of the workflow execution
        """
        self.validate_graph(nodes, edges)
        node_map = {node.id: node for node in nodes}
        sorted_ids = self.topological_sort(nodes, edges)
        results = {}
        logs = []
        
        for node_id in sorted_ids:
            node = node_map[node_id]
            plugin = load_plugin(node.type)
            
            # Gather inputs from upstream node outputs
            inputs = {}
            for edge in edges:
                if edge.target == node_id:
                    inputs.update(results.get(edge.source, {}))
            
            # Execute plugin
            result = plugin.run(inputs, node.config)
            results[node_id] = result
            
            # If it's a terminal node (outputs == {})
            if plugin.__plugin_meta__.get("outputs") == {}:
                logs.append({"node": node_id, "value": result.get("logged") or result.get("display")})
        
        return {"node_outputs": results, "log": logs}

# For backwards compatibility
def topological_sort(nodes: List[Any], edges: List[Any]) -> List[str]:
    """
    Perform a topological sort on the workflow graph.
    
    Args:
        nodes: List of nodes in the workflow
        edges: List of edges in the workflow
        
    Returns:
        List of node IDs in topological order
    """
    executor = WorkflowExecutorService()
    return executor.topological_sort(nodes, edges)

def validate_graph(nodes: List[Any], edges: List[Any]) -> None:
    """
    Validate the workflow graph by checking that all connections are valid.
    
    Args:
        nodes: List of nodes in the workflow
        edges: List of edges in the workflow
        
    Raises:
        ValueError: If any connection is invalid
    """
    executor = WorkflowExecutorService()
    executor.validate_graph(nodes, edges)

def execute_workflow(nodes: List[Any], edges: List[Any]) -> Dict[str, Any]:
    """
    Execute a workflow by running each node in topological order.
    
    Args:
        nodes: List of nodes in the workflow
        edges: List of edges in the workflow
        
    Returns:
        Dictionary containing the results of the workflow execution
    """
    executor = WorkflowExecutorService()
    return executor.execute_workflow(nodes, edges)
