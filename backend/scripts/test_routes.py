"""
Test Routes

This script tests the consolidated routes to ensure they are working properly.
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8001/api"

def test_core_nodes():
    """Test core node routes."""
    print("\n=== Testing Core Node Routes ===")
    
    # Get all core nodes
    response = requests.get(f"{BASE_URL}/core-nodes")
    print(f"GET /core-nodes: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['data'])} core nodes")
    
    # Get core nodes by directory
    response = requests.get(f"{BASE_URL}/core-nodes/directories")
    print(f"GET /core-nodes/directories: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['data'])} directories")
        for directory, nodes in data['data'].items():
            print(f"  - {directory}: {len(nodes)} nodes")
    
    # Get a specific core node
    response = requests.get(f"{BASE_URL}/core-nodes/core.begin")
    print(f"GET /core-nodes/core.begin: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found core node: {data['data']['id']}")

def test_plugins():
    """Test plugin routes."""
    print("\n=== Testing Plugin Routes ===")
    
    # Get all plugins
    response = requests.get(f"{BASE_URL}/plugins")
    print(f"GET /plugins: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['data'])} plugins")

def test_type_system():
    """Test type system routes."""
    print("\n=== Testing Type System Routes ===")
    
    # Get type system
    response = requests.get(f"{BASE_URL}/type-system")
    print(f"GET /type-system: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['data']['types'])} types and {len(data['data']['rules'])} rules")
    
    # Check type compatibility
    response = requests.get(f"{BASE_URL}/type-system/compatibility?source=string&target=any")
    print(f"GET /type-system/compatibility?source=string&target=any: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Compatibility result: {data['data']}")

def test_node_types():
    """Test node types routes."""
    print("\n=== Testing Node Types Routes ===")
    
    # Get all node types
    response = requests.get(f"{BASE_URL}/node-types")
    print(f"GET /node-types: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found node types")
    
    # Get core nodes
    response = requests.get(f"{BASE_URL}/node-types/core-nodes")
    print(f"GET /node-types/core-nodes: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['data'])} core nodes")
    
    # Get plugins
    response = requests.get(f"{BASE_URL}/node-types/plugins")
    print(f"GET /node-types/plugins: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['data'])} plugins")

def main():
    """Run all tests."""
    print("Testing consolidated routes...")
    
    try:
        test_core_nodes()
        test_plugins()
        test_type_system()
        test_node_types()
        
        print("\nAll tests completed!")
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server. Make sure the server is running.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
