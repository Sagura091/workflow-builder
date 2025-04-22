#!/usr/bin/env python
"""
Script to test node execution to ensure that nodes can be properly executed.
This script will:
1. Load a test workflow
2. Execute the workflow
3. Report the results
"""

import os
import json
import sys
import importlib.util
from typing import Dict, List, Any, Optional

# Define the root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the directories
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
CORE_NODES_DIR = os.path.join(ROOT_DIR, "core_nodes")
PLUGINS_DIR = os.path.join(ROOT_DIR, "plugins")

# Define the test workflow
TEST_WORKFLOW = {
    "id": "test_workflow",
    "name": "Test Workflow",
    "nodes": [
        {
            "id": "node1",
            "type": "core.begin",
            "x": 100,
            "y": 100,
            "config": {}
        },
        {
            "id": "node2",
            "type": "core.text_input",
            "x": 300,
            "y": 100,
            "config": {
                "text": "Hello, world!"
            }
        },
        {
            "id": "node3",
            "type": "core.text_output",
            "x": 500,
            "y": 100,
            "config": {}
        }
    ],
    "connections": [
        {
            "id": "conn1",
            "from": {
                "nodeId": "node1",
                "port": "trigger"
            },
            "to": {
                "nodeId": "node2",
                "port": "trigger"
            }
        },
        {
            "id": "conn2",
            "from": {
                "nodeId": "node2",
                "port": "text"
            },
            "to": {
                "nodeId": "node3",
                "port": "text"
            }
        }
    ]
}

def load_node(node_type: str) -> Optional[Any]:
    """Load a node by type."""
    # Parse the node type
    parts = node_type.split(".")
    
    if len(parts) < 2:
        print(f"Invalid node type: {node_type}")
        return None
    
    if parts[0] == "core":
        # Load a core node
        node_name = parts[1]
        
        # Find the node in the core_nodes directory
        for root, dirs, files in os.walk(CORE_NODES_DIR):
            for file in files:
                if file == f"{node_name}.py":
                    # Load the module
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(node_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find the node class
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and attr_name.lower() == node_name.lower():
                            return attr()
        
        print(f"Core node not found: {node_type}")
        return None
    else:
        # Load a plugin
        category = parts[0]
        plugin_name = parts[1]
        
        # Find the plugin in the plugins directory
        plugin_path = os.path.join(PLUGINS_DIR, category, f"{plugin_name}.py")
        
        if os.path.exists(plugin_path):
            # Load the module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and attr_name.lower() == plugin_name.lower():
                    return attr()
        
        print(f"Plugin not found: {node_type}")
        return None

def execute_workflow(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a workflow."""
    # Load all nodes
    nodes = {}
    for node_data in workflow["nodes"]:
        node_id = node_data["id"]
        node_type = node_data["type"]
        
        node = load_node(node_type)
        if node:
            nodes[node_id] = {
                "instance": node,
                "data": node_data,
                "inputs": {},
                "outputs": {}
            }
    
    # Set up connections
    for connection in workflow["connections"]:
        from_node_id = connection["from"]["nodeId"]
        from_port = connection["from"]["port"]
        to_node_id = connection["to"]["nodeId"]
        to_port = connection["to"]["port"]
        
        if from_node_id in nodes and to_node_id in nodes:
            # Store the connection for later use
            if "connections" not in nodes[to_node_id]:
                nodes[to_node_id]["connections"] = []
            
            nodes[to_node_id]["connections"].append({
                "from_node_id": from_node_id,
                "from_port": from_port,
                "to_port": to_port
            })
    
    # Execute the workflow
    results = {}
    
    # Start with the begin node
    for node_id, node_data in nodes.items():
        if node_data["data"]["type"] == "core.begin":
            # Execute the begin node
            try:
                node_data["outputs"] = node_data["instance"].execute({}, node_data["data"]["config"])
                results[node_id] = node_data["outputs"]
            except Exception as e:
                print(f"Error executing node {node_id}: {e}")
                results[node_id] = {"error": str(e)}
    
    # Execute the rest of the nodes in topological order
    # This is a simplified approach and doesn't handle cycles
    executed = set()
    while len(executed) < len(nodes):
        for node_id, node_data in nodes.items():
            if node_id in executed:
                continue
            
            # Check if all input nodes have been executed
            can_execute = True
            if "connections" in node_data:
                for connection in node_data["connections"]:
                    if connection["from_node_id"] not in executed:
                        can_execute = False
                        break
            
            if can_execute:
                # Prepare inputs
                inputs = {}
                if "connections" in node_data:
                    for connection in node_data["connections"]:
                        from_node_id = connection["from_node_id"]
                        from_port = connection["from_port"]
                        to_port = connection["to_port"]
                        
                        if from_port in nodes[from_node_id]["outputs"]:
                            inputs[to_port] = nodes[from_node_id]["outputs"][from_port]
                
                # Execute the node
                try:
                    node_data["inputs"] = inputs
                    node_data["outputs"] = node_data["instance"].execute(inputs, node_data["data"]["config"])
                    results[node_id] = node_data["outputs"]
                except Exception as e:
                    print(f"Error executing node {node_id}: {e}")
                    results[node_id] = {"error": str(e)}
                
                executed.add(node_id)
    
    return results

def main():
    """Main function."""
    print("Testing node execution...")
    
    # Execute the test workflow
    try:
        results = execute_workflow(TEST_WORKFLOW)
        
        print("\nWorkflow execution results:")
        for node_id, outputs in results.items():
            print(f"Node {node_id}:")
            for port, value in outputs.items():
                print(f"  - {port}: {value}")
    except Exception as e:
        print(f"Error executing workflow: {e}")
    
    print("\nNode execution testing complete!")

if __name__ == "__main__":
    main()
