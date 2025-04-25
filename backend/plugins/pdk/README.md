# Plugin Development Kit (PDK)

The Plugin Development Kit (PDK) provides tools and utilities for developing plugins for the workflow builder. It includes classes and utilities for creating standalone plugins that can be executed independently without requiring begin and end nodes from the core system.

## Features

- **Standalone Plugin Base**: A base class for plugins that can be executed independently
- **Testing Utilities**: Tools for testing and benchmarking plugins
- **Execution Utilities**: Tools for executing plugins from the command line or from Python code
- **Documentation**: Comprehensive documentation and examples

## Getting Started

To create a standalone plugin, follow these steps:

1. Import the necessary classes from the PDK:

```python
from backend.plugins.pdk import StandalonePluginBase, PluginMetadata, PortDefinition, ConfigField
```

2. Create your plugin class by inheriting from `StandalonePluginBase`:

```python
class MyStandalonePlugin(StandalonePluginBase):
    """
    My standalone plugin.
    """
    
    # Plugin metadata
    __plugin_meta__ = PluginMetadata(
        id="my_plugin.standalone_example",
        name="My Standalone Plugin",
        version="1.0.0",
        description="Example standalone plugin",
        author="Your Name",
        category="examples",
        tags=["example", "standalone"],
        inputs=[
            PortDefinition(
                id="input1",
                name="Input 1",
                type="string",
                description="First input",
                required=True
            )
        ],
        outputs=[
            PortDefinition(
                id="output1",
                name="Output 1",
                type="string",
                description="First output",
                required=True
            )
        ],
        config_fields=[
            ConfigField(
                id="config1",
                name="Config 1",
                type="string",
                description="First config field",
                required=False,
                default_value=""
            )
        ]
    )
    
    # Plugin version
    __plugin_version__ = "1.0.0"
    
    # Plugin dependencies
    __plugin_dependencies__ = []
    
    # Plugin author
    __plugin_author__ = "Your Name"
    
    # Plugin license
    __plugin_license__ = "MIT"
    
    # Standalone execution flag
    __standalone_capable__ = True
    
    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plugin.
        
        Args:
            inputs: Dictionary of input values
            config: Dictionary of configuration values
            
        Returns:
            Dictionary of output values
        """
        # Get inputs
        input1 = inputs.get("input1", "")
        
        # Get config
        config1 = config.get("config1", "")
        
        # Process inputs
        result = f"{input1} - {config1}"
        
        # Return outputs
        return {
            "output1": result
        }
```

3. Test your plugin using the testing utilities:

```python
from backend.plugins.pdk.testing import PluginTester

# Test the plugin
result = PluginTester.test_plugin(
    plugin_class=MyStandalonePlugin,
    inputs={"input1": "Hello"},
    config={"config1": "World"},
    execution_mode="direct"
)

print(result)
```

4. Execute your plugin from the command line:

```bash
python -m backend.plugins.pdk.execution MyStandalonePlugin --inputs '{"input1": "Hello"}' --config '{"config1": "World"}' --mode direct
```

## Execution Modes

Standalone plugins can be executed in two modes:

- **Direct Mode**: The plugin is executed directly without creating a workflow
- **Standalone Mode**: A mini-workflow is created with begin and end nodes, and the plugin is executed within this workflow

## Command Line Interface

The PDK provides a command line interface for executing plugins:

```bash
python -m backend.plugins.pdk.execution <plugin_class> [options]
```

Options:
- `--inputs`: JSON string or file path for inputs
- `--config`: JSON string or file path for configuration
- `--mode`: Execution mode (direct or standalone)
- `--output`: Output file path
- `--pretty`: Pretty print JSON output
- `--benchmark`: Run benchmark
- `--iterations`: Number of benchmark iterations

## Examples

See the `examples` directory for example plugins that demonstrate the use of the PDK.

## API Reference

### StandalonePluginBase

Base class for plugins that can be executed independently.

#### Methods

- `execute(inputs, config)`: Execute the plugin
- `run_standalone(inputs, config, execution_context)`: Run the plugin in standalone mode
- `get_standalone_capabilities()`: Get information about the plugin's standalone capabilities

### PluginTester

Utility class for testing plugins.

#### Methods

- `test_plugin(plugin_class, inputs, config, execution_mode)`: Test a plugin with the given inputs and configuration
- `benchmark_plugin(plugin_class, inputs, config, iterations)`: Benchmark a plugin by running it multiple times
- `validate_plugin(plugin_class)`: Validate a plugin by checking its metadata and implementation

### PluginExecutor

Utility class for executing plugins from the command line.

#### Methods

- `execute_plugin_from_cli(plugin_class)`: Execute a plugin from the command line
- `execute_plugin(plugin_class, inputs, config, execution_mode, output_file, pretty_print)`: Execute a plugin with the given inputs and configuration
