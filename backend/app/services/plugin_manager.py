import os
import importlib.util
import inspect
from typing import Dict, Any, List, Optional
import json

from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class PluginLoadError(Exception):
    """Exception raised when a plugin fails to load."""
    pass

class PluginManager:
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        self.plugins = {}
        self.plugin_metadata = {}

        # Load node_types.json for plugin metadata
        try:
            node_types_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'node_types.json')
            if os.path.exists(node_types_path):
                with open(node_types_path, 'r') as f:
                    node_types_data = json.load(f)
                    if 'plugins' in node_types_data and isinstance(node_types_data['plugins'], list):
                        for plugin_data in node_types_data['plugins']:
                            plugin_id = plugin_data.get('id')
                            if plugin_id:
                                self.plugin_metadata[plugin_id] = self._convert_dict_to_metadata(plugin_data, plugin_id)
        except Exception as e:
            print(f"Error loading node_types.json: {str(e)}")

    def load_all_plugins(self) -> Dict[str, Any]:
        """Load all plugins from the plugin directory."""
        if not os.path.exists(self.plugin_dir):
            print(f"Plugin directory not found: {self.plugin_dir}")
            return {}

        # Load plugins from the root directory
        self._load_plugins_from_directory(self.plugin_dir)

        # Load plugins from category subdirectories
        for item in os.listdir(self.plugin_dir):
            category_dir = os.path.join(self.plugin_dir, item)
            if os.path.isdir(category_dir) and not item.startswith('__') and not item == '__pycache__':
                self._load_plugins_from_directory(category_dir, category_prefix=item)

        return self.plugins

    def _load_plugins_from_directory(self, directory: str, category_prefix: str = None) -> None:
        """Load all plugins from a directory."""
        # Skip these directories and files
        skip_items = [
            '__pycache__', 'to_remove.txt', 'README.md', 'base_plugin.py',
            'control_flow', 'converters', 'data', 'file_storage', 'math',
            'text', 'utilities', 'variables', 'web_api', 'data_handling',
            'examples', 'file_operations', 'text_processing'
        ]

        for item in os.listdir(directory):
            # Skip special files and directories
            if item.startswith('__') or item in skip_items:
                continue

            # Check if it's a directory with an __init__.py file (Python package)
            if os.path.isdir(os.path.join(directory, item)) and \
               os.path.exists(os.path.join(directory, item, '__init__.py')):
                plugin_id = item
                if category_prefix:
                    plugin_id = f"{category_prefix}.{item}"
                self.load_plugin(plugin_id, directory)
            # Or a single Python file
            elif item.endswith('.py'):
                plugin_id = item[:-3]  # Remove .py extension
                if category_prefix:
                    plugin_id = f"{category_prefix}.{plugin_id}"
                self.load_plugin(plugin_id, directory)

    def load_plugin(self, plugin_id: str, directory: str = None) -> Any:
        """Load a specific plugin by ID."""
        if plugin_id in self.plugins:
            return self.plugins[plugin_id]

        if directory is None:
            directory = self.plugin_dir

        try:
            # Handle plugins in subdirectories
            if '.' in plugin_id:
                category, name = plugin_id.split('.', 1)
                category_dir = os.path.join(self.plugin_dir, category)

                # Check if it's a package or a single file
                if os.path.exists(os.path.join(category_dir, name, '__init__.py')):
                    # It's a package
                    spec = importlib.util.spec_from_file_location(
                        plugin_id,
                        os.path.join(category_dir, name, '__init__.py')
                    )
                else:
                    # It's a single file
                    spec = importlib.util.spec_from_file_location(
                        plugin_id,
                        os.path.join(category_dir, f"{name}.py")
                    )
            else:
                # Check if it's a package or a single file
                if os.path.exists(os.path.join(directory, plugin_id, '__init__.py')):
                    # It's a package
                    spec = importlib.util.spec_from_file_location(
                        plugin_id,
                        os.path.join(directory, plugin_id, '__init__.py')
                    )
                else:
                    # It's a single file
                    spec = importlib.util.spec_from_file_location(
                        plugin_id,
                        os.path.join(directory, f"{plugin_id}.py")
                    )

            if spec is None:
                raise PluginLoadError(f"Could not find plugin: {plugin_id}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # First, check for a class that has a method named 'execute' or 'run'
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and (
                    # Check for instance methods
                    (hasattr(obj, 'execute') and (inspect.isfunction(getattr(obj, 'execute')) or inspect.ismethod(getattr(obj, 'execute')))) or
                    (hasattr(obj, 'run') and (inspect.isfunction(getattr(obj, 'run')) or inspect.ismethod(getattr(obj, 'run')))) or
                    # Check for class methods
                    (hasattr(obj, 'execute') and isinstance(getattr(obj, 'execute'), classmethod)) or
                    (hasattr(obj, 'run') and isinstance(getattr(obj, 'run'), classmethod))
                ):
                    plugin_class = obj
                    break

            # If no class found, check for module-level functions
            if plugin_class is None:
                # Check if the module has a run or execute function
                if hasattr(module, 'run') and inspect.isfunction(getattr(module, 'run')):
                    # Create a wrapper class for the function
                    class FunctionWrapper:
                        @staticmethod
                        def execute(inputs, config):
                            return module.run(inputs, config)

                        @staticmethod
                        def generate_code(config):
                            if hasattr(module, 'generate_code') and inspect.isfunction(getattr(module, 'generate_code')):
                                return module.generate_code(config)
                            return ""

                    plugin_class = FunctionWrapper
                elif hasattr(module, 'execute') and inspect.isfunction(getattr(module, 'execute')):
                    # Create a wrapper class for the function
                    class FunctionWrapper:
                        @staticmethod
                        def execute(inputs, config):
                            return module.execute(inputs, config)

                        @staticmethod
                        def generate_code(config):
                            if hasattr(module, 'generate_code') and inspect.isfunction(getattr(module, 'generate_code')):
                                return module.generate_code(config)
                            return ""

                    plugin_class = FunctionWrapper

            if plugin_class is None:
                raise PluginLoadError(f"No valid plugin class or function found in {plugin_id}")

            # Initialize plugin
            plugin = plugin_class()

            # Extract metadata
            metadata = self._extract_metadata(plugin, plugin_id)
            self.plugin_metadata[plugin_id] = metadata

            # Store plugin
            self.plugins[plugin_id] = plugin
            return plugin

        except Exception as e:
            raise PluginLoadError(f"Failed to load plugin {plugin_id}: {str(e)}")

    def get_plugin(self, plugin_id: str) -> Optional[Any]:
        """Get a loaded plugin by ID."""
        if plugin_id not in self.plugins:
            try:
                return self.load_plugin(plugin_id)
            except PluginLoadError:
                # Try to find the plugin in subdirectories
                if '.' not in plugin_id:
                    for item in os.listdir(self.plugin_dir):
                        category_dir = os.path.join(self.plugin_dir, item)
                        if os.path.isdir(category_dir) and not item.startswith('__') and not item == '__pycache__':
                            try:
                                return self.load_plugin(f"{item}.{plugin_id}", category_dir)
                            except PluginLoadError:
                                continue
                return None
        return self.plugins.get(plugin_id)

    def get_plugin_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get metadata for a plugin."""
        if plugin_id not in self.plugin_metadata:
            if plugin_id not in self.plugins:
                try:
                    self.load_plugin(plugin_id)
                except PluginLoadError:
                    # Try to find the plugin in subdirectories
                    if '.' not in plugin_id:
                        for item in os.listdir(self.plugin_dir):
                            category_dir = os.path.join(self.plugin_dir, item)
                            if os.path.isdir(category_dir) and not item.startswith('__') and not item == '__pycache__':
                                try:
                                    self.load_plugin(f"{item}.{plugin_id}", category_dir)
                                    return self.plugin_metadata.get(f"{item}.{plugin_id}")
                                except PluginLoadError:
                                    continue
                    return None
        return self.plugin_metadata.get(plugin_id)

    def get_all_plugin_metadata(self) -> Dict[str, PluginMetadata]:
        """Get metadata for all loaded plugins."""
        return self.plugin_metadata

    def _extract_metadata(self, plugin: Any, plugin_id: str) -> PluginMetadata:
        """Extract metadata from a plugin."""
        # Check if plugin has a __plugin_meta__ attribute
        if hasattr(plugin, '__plugin_meta__'):
            meta = plugin.__plugin_meta__
            if isinstance(meta, dict):
                # Convert dict to PluginMetadata
                return self._convert_dict_to_metadata(meta, plugin_id)
            elif isinstance(meta, PluginMetadata):
                return meta

        # Check for metadata.json file
        metadata_file = None
        if os.path.exists(os.path.join(self.plugin_dir, plugin_id, 'metadata.json')):
            metadata_file = os.path.join(self.plugin_dir, plugin_id, 'metadata.json')
        elif os.path.exists(os.path.join(self.plugin_dir, f"{plugin_id}_metadata.json")):
            metadata_file = os.path.join(self.plugin_dir, f"{plugin_id}_metadata.json")

        if metadata_file:
            try:
                with open(metadata_file, 'r') as f:
                    meta = json.load(f)
                return self._convert_dict_to_metadata(meta, plugin_id)
            except Exception as e:
                print(f"Error loading metadata from {metadata_file}: {str(e)}")

        # Create basic metadata from plugin inspection
        return self._create_basic_metadata(plugin, plugin_id)

    def _convert_dict_to_metadata(self, meta: Dict[str, Any], plugin_id: str) -> PluginMetadata:
        """Convert a dictionary to PluginMetadata."""
        # Convert inputs
        inputs = []
        for input_def in meta.get('inputs', []):
            if isinstance(input_def, dict):
                inputs.append(PortDefinition(**input_def))
            elif isinstance(input_def, PortDefinition):
                inputs.append(input_def)

        # Convert outputs
        outputs = []
        for output_def in meta.get('outputs', []):
            if isinstance(output_def, dict):
                outputs.append(PortDefinition(**output_def))
            elif isinstance(output_def, PortDefinition):
                outputs.append(output_def)

        # Convert config fields
        config_fields = []
        for field_def in meta.get('config_fields', []):
            if isinstance(field_def, dict):
                config_fields.append(ConfigField(**field_def))
            elif isinstance(field_def, ConfigField):
                config_fields.append(field_def)

        # Create metadata
        return PluginMetadata(
            id=meta.get('id', plugin_id),
            name=meta.get('name', plugin_id),
            version=meta.get('version', '1.0.0'),
            description=meta.get('description', ''),
            author=meta.get('author', 'Unknown'),
            category=meta.get('category', NodeCategory.CUSTOM),
            tags=meta.get('tags', []),
            inputs=inputs,
            outputs=outputs,
            config_fields=config_fields,
            ui_properties=meta.get('ui_properties', {}),
            examples=meta.get('examples', []),
            documentation_url=meta.get('documentation_url')
        )

    def _create_basic_metadata(self, plugin: Any, plugin_id: str) -> PluginMetadata:
        """Create basic metadata from plugin inspection."""
        # Try to extract information from docstring
        doc = inspect.getdoc(plugin) or ''
        description = doc.split('\n\n')[0] if doc else ''

        # Try to extract inputs and outputs from execute method
        inputs = []
        outputs = []
        config_fields = []

        # Check for execute or run method
        method_name = None
        if hasattr(plugin, 'execute'):
            method_name = 'execute'
        elif hasattr(plugin, 'run'):
            method_name = 'run'

        if method_name:
            method = getattr(plugin, method_name)
            sig = inspect.signature(method)

            # Check for config parameter
            if 'config' in sig.parameters:
                config_fields.append(ConfigField(
                    id='config',
                    name='Configuration',
                    type='object',
                    description='Plugin configuration',
                    required=True
                ))

            # Check for inputs parameter
            if 'inputs' in sig.parameters:
                # Assume it's a dictionary of input values
                inputs.append(PortDefinition(
                    id='input',
                    name='Input',
                    type='any',
                    description='Plugin input',
                    required=True
                ))

            # Assume the plugin returns a dictionary of output values
            outputs.append(PortDefinition(
                id='output',
                name='Output',
                type='any',
                description='Plugin output',
                required=True
            ))

        return PluginMetadata(
            id=plugin_id,
            name=plugin_id.replace('_', ' ').title(),
            version='1.0.0',
            description=description,
            author='Unknown',
            category=NodeCategory.CUSTOM,
            inputs=inputs,
            outputs=outputs,
            config_fields=config_fields
        )
