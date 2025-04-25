"""
Flow Control Node Information for v0.1.0

This module defines the flow control nodes for the initial version.
"""

from typing import Any, Dict, Callable

# Define the flow control nodes
NODE_INFO: Dict[str, Dict[str, Any]] = {
    "flow.begin": {
        "name": "Begin",
        "introduced_in": "0.1.0",
        "category": "Flow Control",
        "description": "Starting point for workflow execution",
        "inputs": {},
        "outputs": {
            "flow": "flow"
        },
        "config_schema": {}
    },
    "flow.end": {
        "name": "End",
        "introduced_in": "0.1.0",
        "category": "Flow Control",
        "description": "Ending point for workflow execution",
        "inputs": {
            "flow": "flow"
        },
        "outputs": {},
        "config_schema": {}
    },
    "flow.branch": {
        "name": "Branch",
        "introduced_in": "0.1.0",
        "category": "Flow Control",
        "description": "Branch execution based on a condition",
        "inputs": {
            "flow": "flow",
            "condition": "boolean"
        },
        "outputs": {
            "true": "flow",
            "false": "flow"
        },
        "config_schema": {}
    }
}

def get_implementation(node_id: str) -> Callable:
    """
    Get the implementation function for a node.
    
    Args:
        node_id: The ID of the node
        
    Returns:
        The implementation function
    """
    if node_id == "flow.begin":
        return lambda inputs, config: {"flow": None}
    elif node_id == "flow.end":
        return lambda inputs, config: {}
    elif node_id == "flow.branch":
        def branch_impl(inputs, config):
            condition = inputs.get("condition", False)
            if condition:
                return {"true": None}
            else:
                return {"false": None}
        return branch_impl
    else:
        raise ValueError(f"Unknown node ID: {node_id}")
