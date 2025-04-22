# Workflow Builder Backend

## Introduction

The Workflow Builder is a powerful, extensible platform for creating and executing visual workflows. This backend component provides the core infrastructure for managing workflows, plugins, and execution.

```
+---------------------+       +---------------------+       +---------------------+
|                     |       |                     |       |                     |
|  Frontend Interface |<----->|  Backend API Layer  |<----->|  Workflow Executor  |
|                     |       |                     |       |                     |
+---------------------+       +---------------------+       +---------------------+
                                       ^                            ^
                                       |                            |
                                       v                            v
                              +---------------------+       +---------------------+
                              |                     |       |                     |
                              |   Plugin Manager    |<----->|    Type System     |
                              |                     |       |                     |
                              +---------------------+       +---------------------+
                                       ^
                                       |
                                       v
                              +---------------------+
                              |                     |
                              |  Core Nodes/Plugins |
                              |                     |
                              +---------------------+
```

## System Architecture

The Workflow Builder backend is built on a modular architecture that separates concerns and promotes extensibility:

1. **API Layer**: Handles HTTP requests from the frontend, manages authentication, and routes requests to the appropriate controllers.

2. **Controllers**: Implement business logic for workflows, plugins, and type system management.

3. **Services**: Provide core functionality like workflow execution, plugin management, and type validation.

4. **Models**: Define data structures for workflows, nodes, plugins, and type definitions.

5. **Core Nodes**: Built-in nodes that provide essential functionality for all workflows.

6. **Plugins**: User-defined or system-provided extensions that add specific functionality.

7. **Type System**: Ensures type safety and validates connections between nodes.

## Key Components

### Workflow Executor

The Workflow Executor is responsible for:
- Validating workflow structure and connections
- Executing nodes in the correct order (topological sort)
- Managing data flow between nodes
- Handling errors and providing execution logs

### Plugin Manager

The Plugin Manager handles:
- Loading plugins from the filesystem
- Extracting plugin metadata
- Providing plugin information to the frontend
- Managing plugin lifecycle

### Type System

The Type System ensures type safety by:
- Defining data types and their properties
- Establishing compatibility rules between types
- Validating connections between nodes
- Providing type information to the frontend for UI enhancements

## Core Nodes System

The Core Nodes system provides essential building blocks for all workflows. Unlike plugins, core nodes are always available and provide fundamental functionality that most workflows will need.

### Core Node Architecture

Core nodes are organized into categories based on their functionality:

```
core_nodes/
├── base_node.py              # Base class for all core nodes
├── __init__.py               # Exports all core nodes
├── control_flow/             # Nodes for controlling workflow execution
│   ├── __init__.py
│   ├── begin.py              # Starting point for workflows
│   ├── end.py                # Ending point for workflows
│   ├── conditional.py        # Branching based on conditions
│   ├── delay.py              # Pause execution
│   └── trigger.py            # Trigger execution based on events
├── data/                     # Nodes for data manipulation
│   ├── __init__.py
│   ├── json_parser.py        # Parse and generate JSON
│   ├── csv_parser.py         # Parse and generate CSV
│   └── data_merger.py        # Combine multiple data sources
├── text/                     # Nodes for text processing
│   ├── __init__.py
│   ├── text_input.py         # Manual text input
│   ├── text_output.py        # Display text results
│   ├── text_template.py      # Create text from templates
│   └── regex.py              # Apply regular expressions
├── math/                     # Nodes for mathematical operations
│   ├── __init__.py
│   ├── number_input.py       # Manual number input
│   ├── number_formatter.py   # Format numbers for display
│   └── random_generator.py   # Generate random values
├── file_storage/             # Nodes for file operations
│   ├── __init__.py
│   └── file_reader.py        # Read data from files
├── web_api/                  # Nodes for web interactions
│   └── __init__.py
└── utilities/                # Utility nodes
    └── __init__.py
```

### BaseNode Class

All core nodes inherit from the `BaseNode` class, which provides common functionality:

```python
class BaseNode:
    """Base class for all core nodes."""

    def __init__(self):
        """Initialize the node."""
        self.__plugin_meta__ = self.get_metadata()

    def get_metadata(self) -> PluginMetadata:
        """Get the metadata for this node."""
        raise NotImplementedError("Subclasses must implement get_metadata()")

    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node."""
        raise NotImplementedError("Subclasses must implement execute()")

    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        return None
```

### Core Node Categories

#### Control Flow Nodes

These nodes control the execution flow of workflows:

- **Begin**: Starting point of any workflow
- **End**: Ending point of any workflow
- **Conditional**: Branching based on conditions
- **Delay**: Pause execution for a specified time
- **Trigger**: Execute a workflow based on events

#### Data Handling Nodes

These nodes manipulate and transform data:

- **JSON Parser**: Convert between JSON strings and objects
- **CSV Parser**: Convert between CSV strings and arrays of objects
- **Data Merger**: Combine multiple data sources

#### Text Processing Nodes

These nodes work with text data:

- **Text Input**: Enter text manually
- **Text Output**: Display text results
- **Text Template**: Create text from templates
- **Regex**: Apply regular expressions

#### Math & Logic Nodes

These nodes perform mathematical and logical operations:

- **Number Input**: Enter numbers manually
- **Number Formatter**: Format numbers for display
- **Random Generator**: Generate random values

#### File & Data Storage Nodes

These nodes interact with the filesystem:

- **File Reader**: Read data from files

## Plugin System

The Plugin System allows users to extend the Workflow Builder with custom functionality. Plugins are loaded dynamically and can be created, edited, and deleted at runtime.

### Plugin Architecture

Plugins are Python modules or packages that define classes with specific methods and metadata:

```
plugins/
├── __init__.py
├── base_plugin.py           # Base class for all plugins
├── http_request.py          # Make HTTP requests
├── text_processor.py        # Process text data
├── conditional.py          # Conditional branching
├── loop.py                 # Iterate over data
└── ...
```

### Plugin Manager

The Plugin Manager is responsible for loading and managing plugins:

```python
class PluginManager:
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        self.plugins = {}
        self.plugin_metadata = {}

    def load_all_plugins(self) -> Dict[str, Any]:
        """Load all plugins from the plugin directory."""
        # Implementation details...

    def load_plugin(self, plugin_id: str) -> Any:
        """Load a specific plugin by ID."""
        # Implementation details...

    def get_plugin(self, plugin_id: str) -> Optional[Any]:
        """Get a loaded plugin by ID."""
        # Implementation details...

    def get_plugin_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get metadata for a plugin."""
        # Implementation details...
```

### Plugin Metadata

Plugins provide metadata that describes their functionality, inputs, outputs, and configuration options:

```python
class PluginMetadata:
    id: str
    name: str
    version: str
    description: str
    author: str
    category: NodeCategory
    tags: List[str]
    inputs: List[PortDefinition]
    outputs: List[PortDefinition]
    config_fields: List[ConfigField]
    ui_properties: Dict[str, Any]
    examples: List[Dict[str, Any]]
    documentation_url: Optional[str]
```

### Creating a Plugin

Here's an example of a simple plugin that processes text:

```python
from typing import Dict, Any, Optional
from app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class TextProcessor:
    """A plugin for processing text."""

    def get_metadata(self) -> PluginMetadata:
        """Get the plugin metadata."""
        return PluginMetadata(
            id="text_processor",
            name="Text Processor",
            version="1.0.0",
            description="Process text data",
            author="Workflow Builder",
            category=NodeCategory.TEXT,
            tags=["text", "processing"],
            inputs=[
                PortDefinition(
                    id="text",
                    name="Text",
                    type="string",
                    description="The text to process",
                    required=True
                )
            ],
            outputs=[
                PortDefinition(
                    id="processed_text",
                    name="Processed Text",
                    type="string",
                    description="The processed text"
                ),
                PortDefinition(
                    id="character_count",
                    name="Character Count",
                    type="number",
                    description="The number of characters"
                )
            ],
            config_fields=[
                ConfigField(
                    id="operation",
                    name="Operation",
                    type="select",
                    description="The operation to perform",
                    options=[
                        {"label": "Uppercase", "value": "uppercase"},
                        {"label": "Lowercase", "value": "lowercase"},
                        {"label": "Capitalize", "value": "capitalize"},
                        {"label": "Trim", "value": "trim"}
                    ],
                    default_value="uppercase"
                )
            ],
            ui_properties={
                "color": "#3498db",
                "icon": "font"
            }
        )

    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plugin."""
        # Get input text
        text = inputs.get("text", "")
        if not isinstance(text, str):
            text = str(text)

        # Get configuration
        operation = config.get("operation", "uppercase")

        # Process text based on operation
        if operation == "uppercase":
            processed_text = text.upper()
        elif operation == "lowercase":
            processed_text = text.lower()
        elif operation == "capitalize":
            processed_text = text.capitalize()
        elif operation == "trim":
            processed_text = text.strip()
        else:
            processed_text = text

        # Return outputs
        return {
            "processed_text": processed_text,
            "character_count": len(processed_text)
        }
```

## Type System Details

The Type System ensures that connections between nodes are valid by defining types and compatibility rules.

### Type Definitions

Types are defined in a JSON file (`type_system.json`):

```json
{
  "types": {
    "string": {
      "description": "A text value",
      "ui_properties": {
        "color": "#2ecc71",
        "icon": "font"
      }
    },
    "number": {
      "description": "A numeric value",
      "ui_properties": {
        "color": "#3498db",
        "icon": "hashtag"
      }
    },
    "boolean": {
      "description": "A true/false value",
      "ui_properties": {
        "color": "#9b59b6",
        "icon": "toggle-on"
      }
    },
    // More types...
  }
}
```

### Type Compatibility Rules

Rules define which types can be connected to each other:

```json
{
  "rules": [
    {
      "from": "string",
      "to": ["string", "object", "array"],
      "bidirectional": false
    },
    {
      "from": "number",
      "to": ["number", "string"],
      "bidirectional": false
    },
    // More rules...
  ]
}
```

### Type Registry

The Type Registry manages type definitions and rules:

```python
class TypeRegistry:
    def __init__(self, type_system_file: str = None):
        self.type_system = TypeSystem()
        if type_system_file and os.path.exists(type_system_file):
            self.load_from_file(type_system_file)

    def is_compatible(self, source_type: str, target_type: str) -> bool:
        """Check if source_type is compatible with target_type."""
        # Same types are always compatible
        if source_type == target_type:
            return True

        # 'any' type is compatible with everything
        if source_type == 'any' or target_type == 'any':
            return True

        # Check direct rules
        for rule in self.type_system.rules:
            if rule.source_type == source_type and target_type in rule.target_types:
                return True
            if rule.bidirectional and rule.source_type == target_type and source_type in rule.target_types:
                return True

        # Check inheritance (base types)
        source_def = self.get_type(source_type)
        if source_def and source_def.base_type:
            return self.is_compatible(source_def.base_type, target_type)

        return False
```

## Workflow Execution

The Workflow Executor is responsible for executing workflows by running nodes in the correct order and managing data flow between them.

### Workflow Structure

A workflow consists of nodes and edges:

```python
class Node:
    id: str
    type: str
    config: Dict[str, Any]
    x: Optional[float]  # Position for UI
    y: Optional[float]  # Position for UI
    width: Optional[float]  # Size for UI
    height: Optional[float]  # Size for UI

class Edge:
    id: str
    source: str  # Source node ID
    target: str  # Target node ID
    source_port: Optional[str]  # Source port ID
    target_port: Optional[str]  # Target port ID
```

### Execution Process

The workflow execution process follows these steps:

1. **Validation**: Ensure the workflow structure is valid and all connections are compatible.
2. **Topological Sort**: Determine the execution order of nodes based on their dependencies.
3. **Node Execution**: Execute each node in order, passing outputs from upstream nodes as inputs.
4. **Result Collection**: Collect the results from all nodes and return them along with execution logs.

```python
def execute_workflow(nodes, edges):
    # Validate workflow
    validation_errors = validate_workflow(nodes, edges)
    if validation_errors:
        raise ValueError(f"Workflow validation failed: {validation_errors}")

    # Build graph and get execution order
    G = build_graph(nodes, edges)
    execution_order = topological_sort(G)

    # Build node map for quick lookup
    node_map = {node.id: node for node in nodes}

    # Execute nodes in order
    results = {}
    logs = []

    for node_id in execution_order:
        node = node_map[node_id]
        plugin = load_plugin(node.type)

        # Gather inputs from upstream nodes
        inputs = {}
        for edge in edges:
            if edge.target == node_id:
                # Map outputs from source node to inputs of target node
                # Implementation details...

        # Execute plugin
        try:
            result = plugin.execute(node.config, inputs)
            results[node_id] = result
            logs.append({
                "node": node_id,
                "value": "Execution completed",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logs.append({
                "node": node_id,
                "value": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
            raise ValueError(f"Error executing node {node_id}: {str(e)}")

    return {
        "node_outputs": results,
        "log": logs
    }
```

## Future Plans

### Core Nodes to Implement

1. **Web & API Nodes**
   - HTTP Request: Make HTTP requests to external APIs
   - API Response Parser: Parse API responses
   - Webhook Receiver: Receive webhook events
   - Web Scraper: Extract data from web pages
   - Authentication: Handle API authentication

2. **File & Data Storage Nodes**
   - File Writer: Write data to files
   - File Lister: List files in a directory
   - Database Query: Execute database queries
   - Database Writer: Write data to databases
   - Cache: Store temporary data

3. **Utility Nodes**
   - Logger: Log information for debugging
   - Comment: Add notes to workflows
   - Date/Time: Work with dates and times
   - Error Handler: Handle and recover from errors
   - Code Executor: Run custom code snippets
   - Debugger: Inspect data during workflow execution

### Future Plugins

1. **AI & ML Plugins**
   - Text to Embeddings: Convert text to vector embeddings
   - Prompt Template: Create prompts for LLMs
   - LLM Query: Send requests to language models
   - Response Parser: Extract structured data from LLM responses
   - Image Generator: Generate images from text
   - Model Loader: Load ML models
   - Model Predictor: Make predictions with ML models

2. **Data Processing Plugins**
   - Data Transformation: Transform data between formats
   - Data Validation: Validate data against schemas
   - Data Enrichment: Enrich data with external sources
   - Data Aggregation: Aggregate data by groups
   - Data Visualization: Generate visualizations

3. **Integration Plugins**
   - Email Integration: Send and receive emails
   - SMS Integration: Send SMS messages
   - Slack Integration: Post messages to Slack
   - GitHub Integration: Interact with GitHub repositories
   - Google Sheets Integration: Read and write to Google Sheets
   - AWS Integration: Interact with AWS services

### Backend Enhancements

1. **Performance Improvements**
   - Implement caching for frequently used plugins and type information
   - Optimize workflow execution with parallel processing where possible
   - Add support for streaming results during long-running workflows

2. **Security Enhancements**
   - Add authentication and authorization for API endpoints
   - Implement plugin sandboxing for secure execution
   - Add support for encrypted configuration values

3. **Developer Experience**
   - Create a plugin development kit (PDK) for easier plugin creation
   - Add support for plugin versioning and dependency management
   - Implement a testing framework for plugins and workflows

4. **Monitoring and Debugging**
   - Add detailed execution logs with timing information
   - Implement a visual debugger for workflows
   - Add support for breakpoints and step-by-step execution

5. **Workflow Management**
   - Add support for workflow versioning and history
   - Implement workflow templates and sharing
   - Add support for workflow scheduling and triggers

## Conclusion

The Workflow Builder backend provides a robust foundation for creating and executing visual workflows. With its modular architecture, type system, and extensible plugin system, it can be adapted to a wide range of use cases and integrated with various external systems.

By following the roadmap outlined above, the Workflow Builder will continue to evolve into an even more powerful and user-friendly platform for automation and data processing.
