# Core Nodes

This directory contains the core nodes for the workflow builder. Core nodes are fundamental building blocks that provide essential functionality for most workflows.

## Categories

The core nodes are organized into the following categories:

- **control_flow**: Nodes for controlling the flow of execution (begin, end, conditional, loop, switch)
- **data**: Nodes for basic data manipulation (object properties, variable)
- **file_storage**: Nodes for reading and writing files
- **math**: Nodes for mathematical operations
- **text**: Nodes for text processing
- **utilities**: Utility nodes (delay, trigger)
- **web_api**: Nodes for interacting with web APIs

## Core vs. Plugins

Core nodes differ from plugins in the following ways:

1. **Essential Functionality**: Core nodes provide fundamental functionality that most workflows will need.
2. **Stability**: Core nodes have a more stable API and are less likely to change.
3. **Performance**: Core nodes are optimized for performance.
4. **Integration**: Core nodes are deeply integrated with the workflow engine.

Plugins, on the other hand, provide more specialized or advanced functionality and can be added or removed without affecting the core functionality of the workflow builder.

## Development Guidelines

When developing core nodes:

1. Keep the functionality focused and essential
2. Ensure thorough testing
3. Document all inputs, outputs, and behavior
4. Consider backward compatibility
5. Optimize for performance
