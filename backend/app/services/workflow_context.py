"""
Workflow Context

This module provides a context for workflow execution.
"""

from .variable_store import VariableStore
from .node_registry import NodeRegistry

class WorkflowContext:
    """
    Context for workflow execution.
    
    This class provides a context for executing workflows, including:
    - Variable storage
    - Node registry
    - Connection tracking
    - Node execution
    """
    
    def __init__(self, workflow_data=None):
        """
        Initialize a workflow context.
        
        Args:
            workflow_data (dict, optional): The workflow data to initialize with
        """
        self.variables = VariableStore()
        self.node_registry = NodeRegistry()
        self.nodes = {}
        self.connections = []
        
        if workflow_data:
            self.load_workflow(workflow_data)
    
    def load_workflow(self, workflow_data):
        """
        Load a workflow from data.
        
        Args:
            workflow_data (dict): The workflow data to load
            
        Returns:
            bool: True if the workflow was loaded successfully, False otherwise
        """
        try:
            # Load nodes
            for node_data in workflow_data.get("nodes", []):
                node_id = node_data.get("id")
                node_type = node_data.get("type")
                node_config = node_data.get("config", {})
                
                # Create the node instance
                node_class = self.node_registry.get_node(node_type)
                if node_class:
                    node_instance = node_class()
                    self.nodes[node_id] = {
                        "instance": node_instance,
                        "type": node_type,
                        "config": node_config
                    }
            
            # Load connections
            self.connections = workflow_data.get("connections", [])
            
            return True
        except Exception as e:
            print(f"Error loading workflow: {e}")
            return False
    
    def execute_workflow(self, start_node_id=None):
        """
        Execute the workflow.
        
        Args:
            start_node_id (str, optional): The ID of the node to start execution from
                                          If not provided, nodes with no input connections will be executed
            
        Returns:
            dict: The results of the workflow execution
        """
        results = {}
        
        # If no start node is provided, find nodes with no input connections
        if not start_node_id:
            start_nodes = self._find_start_nodes()
        else:
            start_nodes = [start_node_id]
        
        # Execute each start node
        for node_id in start_nodes:
            node_result = self.execute_node(node_id)
            if node_result:
                results[node_id] = node_result
        
        return results
    
    def execute_node(self, node_id):
        """
        Execute a node in the workflow.
        
        Args:
            node_id (str): The ID of the node to execute
            
        Returns:
            dict: The results of the node execution, or None if the node doesn't exist
        """
        node_data = self.nodes.get(node_id)
        if not node_data:
            return None
        
        node_instance = node_data.get("instance")
        node_config = node_data.get("config", {})
        
        # Get inputs from connected nodes
        inputs = self._get_node_inputs(node_id)
        
        # Execute the node
        try:
            return node_instance.execute(inputs, node_config, self)
        except Exception as e:
            print(f"Error executing node {node_id}: {e}")
            return {"error": str(e)}
    
    def _get_node_inputs(self, node_id):
        """
        Get inputs for a node from connected nodes.
        
        Args:
            node_id (str): The ID of the node to get inputs for
            
        Returns:
            dict: The inputs for the node
        """
        inputs = {}
        
        # Find all connections to this node
        for connection in self.connections:
            to_node = connection.get("to", {})
            if to_node.get("nodeId") == node_id:
                from_node = connection.get("from", {})
                from_node_id = from_node.get("nodeId")
                from_port = from_node.get("port")
                to_port = to_node.get("port")
                
                # Execute the input node
                from_node_result = self.execute_node(from_node_id)
                if from_node_result and from_port in from_node_result:
                    inputs[to_port] = from_node_result[from_port]
        
        return inputs
    
    def get_connected_nodes(self, node_id, output_port):
        """
        Get nodes connected to an output port of a node.
        
        Args:
            node_id (str): The ID of the node
            output_port (str): The output port to check
            
        Returns:
            list: A list of node IDs connected to the output port
        """
        connected_nodes = []
        
        for connection in self.connections:
            from_node = connection.get("from", {})
            if from_node.get("nodeId") == node_id and from_node.get("port") == output_port:
                to_node = connection.get("to", {})
                to_node_id = to_node.get("nodeId")
                if to_node_id in self.nodes:
                    connected_nodes.append(to_node_id)
        
        return connected_nodes
    
    def get_input_node(self, node_id, input_port):
        """
        Get the node connected to an input port of a node.
        
        Args:
            node_id (str): The ID of the node
            input_port (str): The input port to check
            
        Returns:
            str: The ID of the connected node, or None if no node is connected
        """
        for connection in self.connections:
            to_node = connection.get("to", {})
            if to_node.get("nodeId") == node_id and to_node.get("port") == input_port:
                from_node = connection.get("from", {})
                from_node_id = from_node.get("nodeId")
                if from_node_id in self.nodes:
                    return from_node_id
        
        return None
    
    def _find_start_nodes(self):
        """
        Find nodes with no input connections.
        
        Returns:
            list: A list of node IDs with no input connections
        """
        # Get all nodes that are targets of connections
        target_nodes = set()
        for connection in self.connections:
            to_node = connection.get("to", {})
            target_nodes.add(to_node.get("nodeId"))
        
        # Find nodes that are not targets of any connection
        start_nodes = []
        for node_id in self.nodes:
            if node_id not in target_nodes:
                start_nodes.append(node_id)
        
        return start_nodes
