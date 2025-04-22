# Plugins

This directory contains plugins for the workflow builder. Plugins extend the functionality of the workflow builder with specialized or advanced features.

## Categories

The plugins are organized into the following categories:

- **text_processing**: Plugins for advanced text processing (text analysis, text splitting, etc.)
- **data_handling**: Plugins for data manipulation (filtering, mapping, sorting, etc.)
- **web_api**: Plugins for interacting with web APIs
- **file_operations**: Plugins for file operations
- **control_flow**: Advanced control flow plugins

## Core vs. Plugins

Plugins differ from core nodes in the following ways:

1. **Specialized Functionality**: Plugins provide more specialized or advanced functionality.
2. **Modularity**: Plugins can be added or removed without affecting the core functionality.
3. **Extensibility**: Users can develop their own plugins to extend the workflow builder.
4. **Versioning**: Plugins can have their own versioning independent of the core system.

Core nodes, on the other hand, provide fundamental functionality that most workflows will need and are deeply integrated with the workflow engine.

## Development Guidelines

When developing plugins:

1. Follow the plugin interface defined in base_plugin.py
2. Document all inputs, outputs, and behavior
3. Include proper error handling
4. Provide clear and descriptive metadata
5. Test thoroughly with different inputs
6. Consider performance implications

## Plugin Structure

Each plugin should have the following structure:

```python
from .base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.__plugin_meta__ = {
            "name": "My Plugin",
            "category": "CATEGORY",
            "description": "Description of what the plugin does",
            "inputs": {
                "input1": {"type": "string", "required": True, "description": "Input description"},
                # More inputs...
            },
            "outputs": {
                "output1": {"type": "string", "description": "Output description"},
                # More outputs...
            },
            "configFields": [
                {"name": "field1", "type": "text", "label": "Field 1", "default": ""},
                # More config fields...
            ]
        }

    def execute(self, inputs, config):
        # Plugin implementation
        return {"output1": result}
```
