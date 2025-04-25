"""
Flow Control Node Information for v0.2.0

This module defines enhanced flow control nodes.
"""

from typing import Any, Dict, Callable

# Define the flow control nodes
NODE_INFO: Dict[str, Dict[str, Any]] = {
    # Nodes from v0.1.0
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
    },
    
    # New nodes in v0.2.0
    "flow.switch": {
        "name": "Switch",
        "introduced_in": "0.2.0",
        "category": "Flow Control",
        "description": "Branch execution based on a value",
        "inputs": {
            "flow": "flow",
            "value": "any"
        },
        "outputs": {
            "case1": "flow",
            "case2": "flow",
            "case3": "flow",
            "default": "flow"
        },
        "config_schema": {
            "cases": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "value": {
                            "type": "string"
                        },
                        "output": {
                            "type": "string",
                            "enum": ["case1", "case2", "case3"]
                        }
                    }
                }
            }
        }
    },
    "flow.for_each": {
        "name": "For Each",
        "introduced_in": "0.2.0",
        "category": "Flow Control",
        "description": "Execute a loop for each item in a collection",
        "inputs": {
            "flow": "flow",
            "items": "array"
        },
        "outputs": {
            "loop": "flow",
            "complete": "flow"
        },
        "config_schema": {}
    },
    "flow.while": {
        "name": "While",
        "introduced_in": "0.2.0",
        "category": "Flow Control",
        "description": "Execute a loop while a condition is true",
        "inputs": {
            "flow": "flow",
            "condition": "boolean"
        },
        "outputs": {
            "loop": "flow",
            "complete": "flow"
        },
        "config_schema": {}
    },
    "flow.delay": {
        "name": "Delay",
        "introduced_in": "0.2.0",
        "category": "Flow Control",
        "description": "Delay execution for a specified time",
        "inputs": {
            "flow": "flow",
            "duration": "number"
        },
        "outputs": {
            "flow": "flow"
        },
        "config_schema": {
            "unit": {
                "type": "string",
                "enum": ["milliseconds", "seconds", "minutes", "hours"],
                "default": "seconds"
            }
        }
    },
    "flow.parallel": {
        "name": "Parallel",
        "introduced_in": "0.2.0",
        "category": "Flow Control",
        "description": "Execute multiple branches in parallel",
        "inputs": {
            "flow": "flow"
        },
        "outputs": {
            "branch1": "flow",
            "branch2": "flow",
            "branch3": "flow",
            "branch4": "flow"
        },
        "config_schema": {}
    },
    "flow.join": {
        "name": "Join",
        "introduced_in": "0.2.0",
        "category": "Flow Control",
        "description": "Join multiple parallel branches",
        "inputs": {
            "branch1": "flow",
            "branch2": "flow",
            "branch3": "flow",
            "branch4": "flow"
        },
        "outputs": {
            "flow": "flow"
        },
        "config_schema": {
            "join_type": {
                "type": "string",
                "enum": ["all", "any", "first"],
                "default": "all"
            }
        }
    },
    "flow.try_catch": {
        "name": "Try Catch",
        "introduced_in": "0.2.0",
        "category": "Flow Control",
        "description": "Handle errors in a workflow",
        "inputs": {
            "flow": "flow"
        },
        "outputs": {
            "try": "flow",
            "catch": "flow",
            "finally": "flow"
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
    elif node_id == "flow.switch":
        def switch_impl(inputs, config):
            value = inputs.get("value")
            cases = config.get("cases", [])
            
            # Find matching case
            for case in cases:
                if case.get("value") == value:
                    output = case.get("output", "default")
                    return {output: None}
            
            # Default case
            return {"default": None}
        return switch_impl
    elif node_id == "flow.for_each":
        def for_each_impl(inputs, config):
            items = inputs.get("items", [])
            if not items:
                return {"complete": None}
            
            # In a real implementation, this would set up the loop
            return {"loop": None}
        return for_each_impl
    elif node_id == "flow.while":
        def while_impl(inputs, config):
            condition = inputs.get("condition", False)
            if condition:
                return {"loop": None}
            else:
                return {"complete": None}
        return while_impl
    elif node_id == "flow.delay":
        def delay_impl(inputs, config):
            # In a real implementation, this would actually delay
            return {"flow": None}
        return delay_impl
    elif node_id == "flow.parallel":
        def parallel_impl(inputs, config):
            # In a real implementation, this would set up parallel execution
            return {
                "branch1": None,
                "branch2": None,
                "branch3": None,
                "branch4": None
            }
        return parallel_impl
    elif node_id == "flow.join":
        def join_impl(inputs, config):
            # In a real implementation, this would wait for branches to complete
            return {"flow": None}
        return join_impl
    elif node_id == "flow.try_catch":
        def try_catch_impl(inputs, config):
            # In a real implementation, this would set up error handling
            return {"try": None}
        return try_catch_impl
    else:
        raise ValueError(f"Unknown node ID: {node_id}")
