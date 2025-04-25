"""
Type Definitions for v0.1.0

This module defines the base types for the type system.
"""

from typing import Any, Dict, List, Optional, Union, Callable

# Define the base types
TYPE_DEFS: Dict[str, Dict[str, Any]] = {
    "string": {
        "name": "String",
        "introduced_in": "0.1.0",
        "validators": [],
        "converters": {}
    },
    "number": {
        "name": "Number",
        "introduced_in": "0.1.0",
        "validators": [],
        "converters": {}
    },
    "boolean": {
        "name": "Boolean",
        "introduced_in": "0.1.0",
        "validators": [],
        "converters": {}
    },
    "array": {
        "name": "Array",
        "introduced_in": "0.1.0",
        "validators": [],
        "converters": {}
    },
    "object": {
        "name": "Object",
        "introduced_in": "0.1.0",
        "validators": [],
        "converters": {}
    },
    "any": {
        "name": "Any",
        "introduced_in": "0.1.0",
        "validators": [],
        "converters": {}
    }
}
