# Plugin Examples

This directory contains example plugins that demonstrate different plugin development techniques.

## Simple Plugins

### Simple Calculator

`simple_calculator.py` demonstrates a basic plugin that performs mathematical operations.

Features:
- Basic inputs and outputs
- Configuration options
- Error handling
- Code generation

### Text Processor Chain

`text_processor_chain.py` demonstrates how to use core nodes within a plugin.

Features:
- Using core nodes
- Chaining multiple operations
- Fallback logic
- Configuration options

## Complex Plugins

### RAG System

`rag_system.py` demonstrates a complex Retrieval-Augmented Generation (RAG) system.

Features:
- Multiple processing steps
- Using multiple core nodes
- Fallback implementations
- Performance tracking
- Complex configuration

## How to Use These Examples

1. Study the examples to understand plugin development patterns
2. Use them as templates for your own plugins
3. Experiment with modifications to learn how plugins work

## Creating Your Own Plugins

To create your own plugin:

1. Create a new Python file in the plugins directory
2. Import the BasePlugin class
3. Create a class that extends BasePlugin
4. Define the plugin metadata
5. Implement the run method
6. Optionally implement the generate_code method

See the [Plugin Development Guide](../../docs/PLUGIN_DEVELOPMENT.md) for more information.
