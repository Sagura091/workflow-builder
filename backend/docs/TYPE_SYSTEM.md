# Type System Documentation

This document explains the type system used in the workflow builder.

## Overview

The type system is designed to ensure type safety when connecting nodes in the workflow builder. It defines:

1. **Types**: The data types that can be used in the workflow builder
2. **Type Rules**: Rules for valid connections between different types
3. **Type Hierarchies**: Relationships between types (e.g., subtypes and supertypes)

## Basic Types

The workflow builder supports the following basic types:

| Type | Description | Example Values |
|------|-------------|----------------|
| `string` | Text values | `"Hello, world!"`, `"42"` |
| `number` | Numeric values | `42`, `3.14` |
| `boolean` | True/false values | `true`, `false` |
| `object` | Key-value pairs | `{"name": "John", "age": 30}` |
| `array` | Lists of values | `[1, 2, 3]`, `["a", "b", "c"]` |
| `any` | Any type of value | Any value |
| `trigger` | Workflow trigger signal | Internal signal |
| `null` | No value | `null` |

## Type Hierarchies

The type system includes hierarchies of types, where subtypes can be used wherever their supertypes are expected.

### Numeric Types

- `number`
  - `integer`
  - `float`
  - `percentage`

### Text Types

- `string`
  - `text`
    - `html`
    - `markdown`
  - `json`
  - `xml`
  - `script`
  - `prompt`
  - `token`

### File Types

- `file`
  - `image`
  - `audio`
  - `video`
  - `document`

### Data Types

- `array`
  - `vector`
    - `embedding`
  - `dataset`
    - `table`
  - `matrix`

### ML Types

- `object`
  - `ml_model`
    - `model`
- `array`
  - `features`
  - `labels`
  - `predictions`
- `object`
  - `metrics`

## Connection Rules

Connections between nodes are valid if the output type is compatible with the input type. Type compatibility is determined by the following rules:

1. **Same Type**: A type is always compatible with itself (e.g., `string` → `string`)
2. **Type Hierarchy**: A subtype is compatible with its supertype (e.g., `integer` → `number`)
3. **Explicit Rules**: Some types have explicit rules allowing connections to other types (e.g., `number` → `string`)
4. **Any Type**: The `any` type is compatible with any other type, and any type is compatible with `any`

## Bidirectional Rules

Some type rules are bidirectional, meaning that the types can be connected in either direction. For example, `number` ↔ `string` means that a number can be connected to a string, and a string can be connected to a number.

## Conversion Nodes

When you need to connect nodes with incompatible types, you can use conversion nodes to convert between types:

- **String Converter**: Converts various types to strings
- **Number Converter**: Converts various types to numbers
- **Boolean Converter**: Converts various types to booleans
- **Array Converter**: Converts various types to arrays
- **Object Converter**: Converts various types to objects

## Type Checking

The workflow builder performs type checking when:

1. **Creating Connections**: When you try to connect two nodes, the workflow builder checks if the connection is valid
2. **Validating Workflows**: Before executing a workflow, the workflow builder validates all connections
3. **Executing Workflows**: During execution, the workflow builder ensures that data passed between nodes has the correct type

## Custom Types

Plugins can define custom types that extend the basic type system. Custom types should specify their base type to ensure proper type checking.

## Examples

Here are some examples of valid and invalid connections:

### Valid Connections

- `string` → `string`
- `number` → `string`
- `boolean` → `string`
- `integer` → `number`
- `image` → `file`
- `any` → `string`
- `string` → `any`

### Invalid Connections

- `string` → `number` (use a Number Converter node)
- `string` → `boolean` (use a Boolean Converter node)
- `number` → `array` (use an Array Converter node)
- `trigger` → `string` (triggers can only connect to other triggers)

## Best Practices

1. **Use Appropriate Types**: Choose the most specific type for your data
2. **Avoid Overusing `any`**: While convenient, using `any` bypasses type checking
3. **Use Conversion Nodes**: When connecting incompatible types, use conversion nodes
4. **Check Type Compatibility**: Before creating a connection, check if the types are compatible
