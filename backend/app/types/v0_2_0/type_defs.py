"""
Type Definitions for v0.2.0

This module defines the enhanced types for the type system.
"""

from typing import Any, Dict, List, Optional, Union, Callable

# Define the enhanced types
TYPE_DEFS: Dict[str, Dict[str, Any]] = {
    # Base types from v0.1.0
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
    },
    
    # New types in v0.2.0
    "integer": {
        "name": "Integer",
        "introduced_in": "0.2.0",
        "base_type": "number",
        "validators": [],
        "converters": {}
    },
    "float": {
        "name": "Float",
        "introduced_in": "0.2.0",
        "base_type": "number",
        "validators": [],
        "converters": {}
    },
    "date": {
        "name": "Date",
        "introduced_in": "0.2.0",
        "validators": [],
        "converters": {}
    },
    "time": {
        "name": "Time",
        "introduced_in": "0.2.0",
        "validators": [],
        "converters": {}
    },
    "datetime": {
        "name": "DateTime",
        "introduced_in": "0.2.0",
        "validators": [],
        "converters": {}
    },
    "email": {
        "name": "Email",
        "introduced_in": "0.2.0",
        "base_type": "string",
        "validators": [],
        "converters": {}
    },
    "url": {
        "name": "URL",
        "introduced_in": "0.2.0",
        "base_type": "string",
        "validators": [],
        "converters": {}
    },
    "file": {
        "name": "File",
        "introduced_in": "0.2.0",
        "validators": [],
        "converters": {}
    },
    "image": {
        "name": "Image",
        "introduced_in": "0.2.0",
        "base_type": "file",
        "validators": [],
        "converters": {}
    },
    "audio": {
        "name": "Audio",
        "introduced_in": "0.2.0",
        "base_type": "file",
        "validators": [],
        "converters": {}
    },
    "video": {
        "name": "Video",
        "introduced_in": "0.2.0",
        "base_type": "file",
        "validators": [],
        "converters": {}
    },
    "color": {
        "name": "Color",
        "introduced_in": "0.2.0",
        "validators": [],
        "converters": {}
    },
    "regex": {
        "name": "RegEx",
        "introduced_in": "0.2.0",
        "base_type": "string",
        "validators": [],
        "converters": {}
    },
    "json": {
        "name": "JSON",
        "introduced_in": "0.2.0",
        "validators": [],
        "converters": {}
    },
    "xml": {
        "name": "XML",
        "introduced_in": "0.2.0",
        "base_type": "string",
        "validators": [],
        "converters": {}
    },
    "html": {
        "name": "HTML",
        "introduced_in": "0.2.0",
        "base_type": "string",
        "validators": [],
        "converters": {}
    },
    "markdown": {
        "name": "Markdown",
        "introduced_in": "0.2.0",
        "base_type": "string",
        "validators": [],
        "converters": {}
    },
    "css": {
        "name": "CSS",
        "introduced_in": "0.2.0",
        "base_type": "string",
        "validators": [],
        "converters": {}
    },
    "javascript": {
        "name": "JavaScript",
        "introduced_in": "0.2.0",
        "base_type": "string",
        "validators": [],
        "converters": {}
    },
    "python": {
        "name": "Python",
        "introduced_in": "0.2.0",
        "base_type": "string",
        "validators": [],
        "converters": {}
    }
}
