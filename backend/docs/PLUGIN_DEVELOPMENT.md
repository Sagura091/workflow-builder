# Plugin Development Guide

This guide explains how to create plugins for the workflow builder.

## Table of Contents

- [Overview](#overview)
- [Plugin Types](#plugin-types)
- [Creating a Plugin](#creating-a-plugin)
- [Plugin Metadata](#plugin-metadata)
- [Using Core Nodes in Plugins](#using-core-nodes-in-plugins)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

Plugins are Python classes that extend the `BasePlugin` class and implement the `run` method. They can range from simple utilities to complex systems. Plugins allow you to extend the functionality of the workflow builder without modifying the core code.

## Plugin Types

You can create two types of plugins:

1. **Simple Plugins**: Single-purpose nodes that do one thing well
2. **Complex System Plugins**: Nodes that encapsulate entire systems

### Simple Plugins

Simple plugins are focused on a specific task, such as:
- Text transformation
- Mathematical operations
- Data filtering
- File operations

### Complex System Plugins

Complex system plugins combine multiple operations into a single node, such as:
- RAG (Retrieval-Augmented Generation) systems
- Image processing pipelines
- Data ETL (Extract, Transform, Load) processes
- Machine learning workflows

## Creating a Plugin

### Step 1: Create a new Python file in the plugins directory

```python
# my_plugin.py
from backend.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    __plugin_meta__ = {
        "name": "My Plugin",
        "category": "CUSTOM",
        "description": "Description of my plugin",
        "inputs": {
            "input1": {"type": "string", "description": "Input description"}
        },
        "outputs": {
            "output1": {"type": "string", "description": "Output description"}
        },
        "configFields": [
            {"name": "field1", "type": "text", "label": "Field 1", "default": ""}
        ]
    }

    @classmethod
    def run(cls, inputs, config):
        # Plugin implementation
        input1 = inputs.get("input1", "")
        field1 = config.get("field1", "")
        
        # Process inputs
        result = input1 + " " + field1
        
        return {"output1": result}
```

### Step 2: Register your plugin

Plugins are automatically discovered when placed in the plugins directory.

## Plugin Metadata

The `__plugin_meta__` dictionary defines the plugin's metadata:

- `name`: Display name of the plugin
- `category`: Category for organizing plugins
- `description`: Description of what the plugin does
- `inputs`: Input ports for the plugin
  - Each input has a type, description, and optional required flag
- `outputs`: Output ports for the plugin
  - Each output has a type and description
- `configFields`: Configuration fields for the plugin
  - Each field has a name, type, label, and default value

### Input and Output Types

The following types are supported:
- `string`: Text values
- `number`: Numeric values
- `boolean`: True/false values
- `object`: Key-value pairs
- `array`: Lists of values
- `file`: File references
- `image`: Image data
- `any`: Any type of data

### Config Field Types

The following field types are supported:
- `text`: Single-line text input
- `textarea`: Multi-line text input
- `number`: Numeric input
- `boolean`: Checkbox
- `select`: Dropdown selection
- `multiselect`: Multiple selection
- `color`: Color picker
- `file`: File upload

## Using Core Nodes in Plugins

The workflow builder allows plugins to use core nodes, enabling you to:

1. Reuse existing functionality
2. Chain together multiple operations
3. Create higher-level abstractions

### Getting a Core Node

```python
node = cls.get_core_node("core.node_id")
```

This returns an instance of the core node, or `None` if the node is not found.

### Executing a Core Node

```python
result = cls.execute_core_node("core.node_id", inputs, config)
```

This executes the core node with the given inputs and configuration, and returns the result.

### Example: Text Processor Chain

Here's an example of a plugin that uses multiple core nodes:

```python
from backend.plugins.base_plugin import BasePlugin

class TextProcessorChain(BasePlugin):
    __plugin_meta__ = {
        "name": "Text Processor Chain",
        "category": "TEXT_PROCESSING",
        "description": "Process text through multiple transformations",
        "inputs": {
            "text": {"type": "string", "description": "Text to process"}
        },
        "outputs": {
            "processed_text": {"type": "string", "description": "Processed text"},
            "word_count": {"type": "number", "description": "Word count"}
        },
        "configFields": [
            {"name": "uppercase", "type": "boolean", "label": "Convert to Uppercase", "default": False},
            {"name": "trim_whitespace", "type": "boolean", "label": "Trim Whitespace", "default": True},
            {"name": "count_words", "type": "boolean", "label": "Count Words", "default": True}
        ]
    }
    
    @classmethod
    def run(cls, inputs, config):
        text = inputs.get("text", "")
        results = {"processed_text": text, "word_count": 0}
        
        # Use string operations core node if available
        if config.get("uppercase", False):
            string_ops_result = cls.execute_core_node(
                "core.string_operations",
                {"text": text},
                {"operation": "uppercase"}
            )
            if string_ops_result and "result" in string_ops_result:
                text = string_ops_result["result"]
        
        # Use text analyzer core node if available and configured
        if config.get("count_words", True):
            text_analyzer_result = cls.execute_core_node(
                "core.text_analyzer",
                {"text": text},
                {"analyze": "word_count"}
            )
            if text_analyzer_result and "word_count" in text_analyzer_result:
                results["word_count"] = text_analyzer_result["word_count"]
        
        results["processed_text"] = text
        return results
```

## Examples

### Simple Calculator Plugin

```python
from backend.plugins.base_plugin import BasePlugin

class SimpleCalculator(BasePlugin):
    __plugin_meta__ = {
        "name": "Simple Calculator",
        "category": "MATH",
        "description": "Performs basic math operations",
        "inputs": {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"}
        },
        "outputs": {
            "result": {"type": "number", "description": "Calculation result"}
        },
        "configFields": [
            {"name": "operation", "type": "select", "label": "Operation", 
             "options": [
                 {"label": "Add", "value": "add"},
                 {"label": "Subtract", "value": "subtract"},
                 {"label": "Multiply", "value": "multiply"},
                 {"label": "Divide", "value": "divide"}
             ],
             "default": "add"}
        ]
    }

    @classmethod
    def run(cls, inputs, config):
        a = inputs.get("a", 0)
        b = inputs.get("b", 0)
        operation = config.get("operation", "add")
        
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            result = a / b if b != 0 else "Error: Division by zero"
        
        return {"result": result}
```

### Complex RAG System Plugin

See the `examples/rag_system.py` file for a complete example of a complex RAG system plugin.

## Best Practices

1. **Keep It Simple**: Start with the simplest implementation that works
2. **Follow the Template**: Use the provided templates as a starting point
3. **Document Everything**: Clearly document inputs, outputs, and configuration
4. **Use Python Power**: Leverage the full Python ecosystem when needed
5. **Test Thoroughly**: Test your plugin with different inputs and configurations
6. **Handle Errors**: Provide meaningful error messages and fallbacks
7. **Check for Null**: Always check if inputs and core nodes exist before using them
8. **Provide Defaults**: Always provide default values for inputs and configuration

## Troubleshooting

### Plugin Not Found

If your plugin is not being discovered:
- Make sure it's in the correct directory
- Make sure the class name matches the file name
- Make sure the class extends BasePlugin
- Check for syntax errors in your plugin code

### Plugin Not Working

If your plugin is not working as expected:
- Check the logs for error messages
- Make sure all required inputs are provided
- Make sure the configuration is correct
- Test with simple inputs first
- Add debug print statements to your plugin code

### Core Node Not Found

If a core node is not found:
- Make sure the node ID is correct
- Make sure the core node is registered
- Check if the core node is available in the current environment
- Provide a fallback implementation
