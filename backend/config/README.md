# Configuration Files

This directory contains configuration files for the workflow builder backend.

## Files

- **core_nodes.json**: Defines the core nodes available in the workflow builder.
- **node_types.json**: Defines the node types and their connection points.
- **type_system.json**: Defines the data types supported by the workflow builder.
- **type_rules.json**: Defines the rules for connecting different data types.

## Usage

These files are loaded by the backend API to provide information about the available nodes, types, and connection rules to the frontend.

### Type System

The type system defines the data types that can flow between nodes in the workflow. Each type has:
- A description
- UI properties (color, icon)
- Optional base type

### Type Rules

The type rules define which types can be connected to which other types. Each rule has:
- A source type (`from`)
- A list of target types (`to`)
- An optional `bidirectional` flag

### Core Nodes

Core nodes are the built-in nodes available in the workflow builder. Each node has:
- An ID
- A name
- A category
- A description
- Input and output ports
- UI properties

### Node Types

Node types define the available node types and their connection points. This includes both core nodes and plugins.
