"""
Data Handling Node Information for v0.2.0

This module defines data handling nodes.
"""

from typing import Any, Dict, Callable

# Define the data handling nodes
NODE_INFO: Dict[str, Dict[str, Any]] = {
    "data.variable": {
        "name": "Variable",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Store and retrieve a variable",
        "inputs": {
            "flow": "flow",
            "value": "any"
        },
        "outputs": {
            "flow": "flow",
            "value": "any"
        },
        "config_schema": {
            "name": {
                "type": "string",
                "default": "variable"
            },
            "scope": {
                "type": "string",
                "enum": ["local", "global"],
                "default": "local"
            }
        }
    },
    "data.get_property": {
        "name": "Get Property",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Get a property from an object",
        "inputs": {
            "flow": "flow",
            "object": "object"
        },
        "outputs": {
            "flow": "flow",
            "value": "any"
        },
        "config_schema": {
            "property": {
                "type": "string",
                "default": ""
            }
        }
    },
    "data.set_property": {
        "name": "Set Property",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Set a property on an object",
        "inputs": {
            "flow": "flow",
            "object": "object",
            "value": "any"
        },
        "outputs": {
            "flow": "flow",
            "object": "object"
        },
        "config_schema": {
            "property": {
                "type": "string",
                "default": ""
            }
        }
    },
    "data.array_item": {
        "name": "Array Item",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Get an item from an array",
        "inputs": {
            "flow": "flow",
            "array": "array",
            "index": "number"
        },
        "outputs": {
            "flow": "flow",
            "item": "any"
        },
        "config_schema": {}
    },
    "data.array_length": {
        "name": "Array Length",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Get the length of an array",
        "inputs": {
            "flow": "flow",
            "array": "array"
        },
        "outputs": {
            "flow": "flow",
            "length": "number"
        },
        "config_schema": {}
    },
    "data.array_push": {
        "name": "Array Push",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Add an item to the end of an array",
        "inputs": {
            "flow": "flow",
            "array": "array",
            "item": "any"
        },
        "outputs": {
            "flow": "flow",
            "array": "array"
        },
        "config_schema": {}
    },
    "data.array_pop": {
        "name": "Array Pop",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Remove and return the last item from an array",
        "inputs": {
            "flow": "flow",
            "array": "array"
        },
        "outputs": {
            "flow": "flow",
            "array": "array",
            "item": "any"
        },
        "config_schema": {}
    },
    "data.array_filter": {
        "name": "Array Filter",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Filter an array based on a condition",
        "inputs": {
            "flow": "flow",
            "array": "array",
            "condition": "boolean"
        },
        "outputs": {
            "flow": "flow",
            "filtered": "array"
        },
        "config_schema": {}
    },
    "data.array_map": {
        "name": "Array Map",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Transform each item in an array",
        "inputs": {
            "flow": "flow",
            "array": "array",
            "transform": "any"
        },
        "outputs": {
            "flow": "flow",
            "mapped": "array"
        },
        "config_schema": {}
    },
    "data.object_keys": {
        "name": "Object Keys",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Get the keys of an object",
        "inputs": {
            "flow": "flow",
            "object": "object"
        },
        "outputs": {
            "flow": "flow",
            "keys": "array"
        },
        "config_schema": {}
    },
    "data.object_values": {
        "name": "Object Values",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Get the values of an object",
        "inputs": {
            "flow": "flow",
            "object": "object"
        },
        "outputs": {
            "flow": "flow",
            "values": "array"
        },
        "config_schema": {}
    },
    "data.object_entries": {
        "name": "Object Entries",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Get the entries of an object as key-value pairs",
        "inputs": {
            "flow": "flow",
            "object": "object"
        },
        "outputs": {
            "flow": "flow",
            "entries": "array"
        },
        "config_schema": {}
    },
    "data.json_parse": {
        "name": "JSON Parse",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Parse a JSON string into an object",
        "inputs": {
            "flow": "flow",
            "json": "string"
        },
        "outputs": {
            "flow": "flow",
            "object": "object"
        },
        "config_schema": {}
    },
    "data.json_stringify": {
        "name": "JSON Stringify",
        "introduced_in": "0.2.0",
        "category": "Data Handling",
        "description": "Convert an object to a JSON string",
        "inputs": {
            "flow": "flow",
            "object": "object"
        },
        "outputs": {
            "flow": "flow",
            "json": "string"
        },
        "config_schema": {
            "pretty": {
                "type": "boolean",
                "default": false
            }
        }
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
    if node_id == "data.variable":
        def variable_impl(inputs, config):
            value = inputs.get("value")
            return {"flow": None, "value": value}
        return variable_impl
    elif node_id == "data.get_property":
        def get_property_impl(inputs, config):
            obj = inputs.get("object", {})
            prop = config.get("property", "")
            value = obj.get(prop) if isinstance(obj, dict) else None
            return {"flow": None, "value": value}
        return get_property_impl
    elif node_id == "data.set_property":
        def set_property_impl(inputs, config):
            obj = inputs.get("object", {})
            if not isinstance(obj, dict):
                obj = {}
            prop = config.get("property", "")
            value = inputs.get("value")
            obj[prop] = value
            return {"flow": None, "object": obj}
        return set_property_impl
    elif node_id == "data.array_item":
        def array_item_impl(inputs, config):
            array = inputs.get("array", [])
            index = inputs.get("index", 0)
            if not isinstance(array, list):
                array = []
            if not isinstance(index, (int, float)):
                index = 0
            index = int(index)
            item = array[index] if 0 <= index < len(array) else None
            return {"flow": None, "item": item}
        return array_item_impl
    elif node_id == "data.array_length":
        def array_length_impl(inputs, config):
            array = inputs.get("array", [])
            if not isinstance(array, list):
                array = []
            return {"flow": None, "length": len(array)}
        return array_length_impl
    elif node_id == "data.array_push":
        def array_push_impl(inputs, config):
            array = inputs.get("array", [])
            item = inputs.get("item")
            if not isinstance(array, list):
                array = []
            array.append(item)
            return {"flow": None, "array": array}
        return array_push_impl
    elif node_id == "data.array_pop":
        def array_pop_impl(inputs, config):
            array = inputs.get("array", [])
            if not isinstance(array, list):
                array = []
            item = array.pop() if array else None
            return {"flow": None, "array": array, "item": item}
        return array_pop_impl
    elif node_id == "data.array_filter":
        def array_filter_impl(inputs, config):
            array = inputs.get("array", [])
            condition = inputs.get("condition", False)
            if not isinstance(array, list):
                array = []
            # In a real implementation, this would apply the condition to each item
            filtered = array if condition else []
            return {"flow": None, "filtered": filtered}
        return array_filter_impl
    elif node_id == "data.array_map":
        def array_map_impl(inputs, config):
            array = inputs.get("array", [])
            transform = inputs.get("transform")
            if not isinstance(array, list):
                array = []
            # In a real implementation, this would apply the transform to each item
            mapped = array
            return {"flow": None, "mapped": mapped}
        return array_map_impl
    elif node_id == "data.object_keys":
        def object_keys_impl(inputs, config):
            obj = inputs.get("object", {})
            if not isinstance(obj, dict):
                obj = {}
            keys = list(obj.keys())
            return {"flow": None, "keys": keys}
        return object_keys_impl
    elif node_id == "data.object_values":
        def object_values_impl(inputs, config):
            obj = inputs.get("object", {})
            if not isinstance(obj, dict):
                obj = {}
            values = list(obj.values())
            return {"flow": None, "values": values}
        return object_values_impl
    elif node_id == "data.object_entries":
        def object_entries_impl(inputs, config):
            obj = inputs.get("object", {})
            if not isinstance(obj, dict):
                obj = {}
            entries = [{"key": k, "value": v} for k, v in obj.items()]
            return {"flow": None, "entries": entries}
        return object_entries_impl
    elif node_id == "data.json_parse":
        def json_parse_impl(inputs, config):
            json_str = inputs.get("json", "{}")
            if not isinstance(json_str, str):
                json_str = "{}"
            try:
                import json
                obj = json.loads(json_str)
            except Exception:
                obj = {}
            return {"flow": None, "object": obj}
        return json_parse_impl
    elif node_id == "data.json_stringify":
        def json_stringify_impl(inputs, config):
            obj = inputs.get("object", {})
            pretty = config.get("pretty", False)
            try:
                import json
                indent = 2 if pretty else None
                json_str = json.dumps(obj, indent=indent)
            except Exception:
                json_str = "{}"
            return {"flow": None, "json": json_str}
        return json_stringify_impl
    else:
        raise ValueError(f"Unknown node ID: {node_id}")
