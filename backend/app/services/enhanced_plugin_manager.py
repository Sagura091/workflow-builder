"""
Enhanced Plugin Manager

This module provides an enhanced plugin manager with improved plugin discovery,
dependency resolution, and lifecycle management.
"""

import os
import sys
import time
import logging
import importlib.util
import inspect
import json
from typing import Dict, Any, List, Optional, Set, Tuple, Type
from datetime import datetime

from backend.app.models.plugin_interface import (
    PluginInterface,
    PluginLifecycleState,
    PluginDependencyError,
    PluginVersionError,
    PluginExecutionError
)
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

# Configure logger
logger = logging.getLogger("workflow_builder")


class PluginLoadError(Exception):
    """Exception raised when a plugin fails to load."""
    pass


class EnhancedPluginManager:
    """Enhanced plugin manager with improved plugin discovery and lifecycle management."""
    
    def __init__(self, plugin_dir: str):
        """Initialize the plugin manager.
        
        Args:
            plugin_dir: Directory containing plugins
        """
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.plugin_classes: Dict[str, Type[PluginInterface]] = {}
        self.plugin_modules: Dict[str, Any] = {}
        self.plugin_dependencies: Dict[str, List[str]] = {}
        self.plugin_dependents: Dict[str, List[str]] = {}
        self.disabled_plugins: Set[str] = set()
        
        # Performance metrics
        self.performance_metrics = {
            "load_time": 0.0,
            "execution_time": 0.0,
            "execution_count": 0,
            "error_count": 0
        }
        
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
            logger.error(f"Error loading node_types.json: {str(e)}")
    
    def load_all_plugins(self) -> Dict[str, PluginInterface]:
        """Load all plugins from the plugin directory.
        
        Returns:
            Dictionary of loaded plugins
        """
        start_time = time.time()
        
        if not os.path.exists(self.plugin_dir):
            logger.error(f"Plugin directory not found: {self.plugin_dir}")
            return {}
        
        # Discover all plugins
        self._discover_plugins()
        
        # Build dependency graph
        self._build_dependency_graph()
        
        # Load plugins in dependency order
        self._load_plugins_in_order()
        
        # Update performance metrics
        self.performance_metrics["load_time"] = time.time() - start_time
        
        logger.info(f"Loaded {len(self.plugins)} plugins in {self.performance_metrics['load_time']:.2f} seconds")
        return self.plugins
    
    def _discover_plugins(self) -> None:
        """Discover all plugins in the plugin directory."""
        # Load plugins from the root directory
        self._discover_plugins_in_directory(self.plugin_dir)
        
        # Load plugins from category subdirectories
        for item in os.listdir(self.plugin_dir):
            category_dir = os.path.join(self.plugin_dir, item)
            if os.path.isdir(category_dir) and not item.startswith('__') and not item == '__pycache__':
                self._discover_plugins_in_directory(category_dir, category_prefix=item)
    
    def _discover_plugins_in_directory(self, directory: str, category_prefix: str = None) -> None:
        """Discover plugins in a directory.
        
        Args:
            directory: Directory to search for plugins
            category_prefix: Optional category prefix for plugin IDs
        """
        # Skip these directories and files
        skip_items = [
            '__pycache__', 'to_remove.txt', 'README.md', 'base_plugin.py'
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
                self._discover_plugin(plugin_id, directory)
            # Or a single Python file
            elif item.endswith('.py'):
                plugin_id = item[:-3]  # Remove .py extension
                if category_prefix:
                    plugin_id = f"{category_prefix}.{plugin_id}"
                self._discover_plugin(plugin_id, directory)
    
    def _discover_plugin(self, plugin_id: str, directory: str) -> None:
        """Discover a plugin and its dependencies.
        
        Args:
            plugin_id: Plugin ID
            directory: Directory containing the plugin
        """
        try:
            # Get the plugin module path
            module_path = self._get_plugin_module_path(plugin_id, directory)
            if not module_path:
                logger.warning(f"Could not find module path for plugin {plugin_id}")
                return
            
            # Load the module
            spec = importlib.util.spec_from_file_location(plugin_id, module_path)
            if spec is None:
                logger.warning(f"Could not create spec for plugin {plugin_id}")
                return
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_id] = module
            spec.loader.exec_module(module)
            
            # Store the module
            self.plugin_modules[plugin_id] = module
            
            # Find plugin class
            plugin_class = self._find_plugin_class(module, plugin_id)
            if plugin_class:
                self.plugin_classes[plugin_id] = plugin_class
                
                # Extract dependencies
                if hasattr(plugin_class, "__plugin_dependencies__"):
                    self.plugin_dependencies[plugin_id] = plugin_class.__plugin_dependencies__
                else:
                    self.plugin_dependencies[plugin_id] = []
                
                # Extract metadata
                if hasattr(plugin_class, "__plugin_meta__"):
                    metadata = self._convert_dict_to_metadata(plugin_class.__plugin_meta__, plugin_id)
                    self.plugin_metadata[plugin_id] = metadata
                else:
                    # Create basic metadata
                    metadata = self._create_basic_metadata(plugin_class, plugin_id)
                    self.plugin_metadata[plugin_id] = metadata
            else:
                logger.warning(f"No valid plugin class found in {plugin_id}")
        
        except Exception as e:
            logger.error(f"Error discovering plugin {plugin_id}: {str(e)}")
    
    def _get_plugin_module_path(self, plugin_id: str, directory: str) -> Optional[str]:
        """Get the module path for a plugin.
        
        Args:
            plugin_id: Plugin ID
            directory: Directory containing the plugin
            
        Returns:
            Module path or None if not found
        """
        # Handle plugins in subdirectories
        if '.' in plugin_id:
            category, name = plugin_id.split('.', 1)
            category_dir = os.path.join(self.plugin_dir, category)
            
            # Check if it's a package or a single file
            if os.path.exists(os.path.join(category_dir, name, '__init__.py')):
                # It's a package
                return os.path.join(category_dir, name, '__init__.py')
            else:
                # It's a single file
                return os.path.join(category_dir, f"{name}.py")
        else:
            # Check if it's a package or a single file
            if os.path.exists(os.path.join(directory, plugin_id, '__init__.py')):
                # It's a package
                return os.path.join(directory, plugin_id, '__init__.py')
            else:
                # It's a single file
                return os.path.join(directory, f"{plugin_id}.py")
    
    def _find_plugin_class(self, module: Any, plugin_id: str) -> Optional[Type[PluginInterface]]:
        """Find the plugin class in a module.
        
        Args:
            module: Module to search
            plugin_id: Plugin ID
            
        Returns:
            Plugin class or None if not found
        """
        # First, look for classes that inherit from PluginInterface
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, PluginInterface) and obj != PluginInterface:
                return obj
        
        # If not found, look for classes with execute or run methods
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and (
                (hasattr(obj, 'execute') and (inspect.isfunction(getattr(obj, 'execute')) or inspect.ismethod(getattr(obj, 'execute')))) or
                (hasattr(obj, 'run') and (inspect.isfunction(getattr(obj, 'run')) or inspect.ismethod(getattr(obj, 'run'))))
            ):
                # Create a wrapper class that inherits from PluginInterface
                class PluginWrapper(PluginInterface):
                    def __init__(self):
                        super().__init__()
                        self._wrapped = obj()
                    
                    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
                        if hasattr(self._wrapped, 'execute'):
                            return self._wrapped.execute(inputs, config)
                        elif hasattr(self._wrapped, 'run'):
                            return self._wrapped.run(inputs, config)
                        return {}
                    
                    def generate_code(self, config: Dict[str, Any]) -> str:
                        if hasattr(self._wrapped, 'generate_code'):
                            return self._wrapped.generate_code(config)
                        return ""
                
                # Copy metadata from original class
                if hasattr(obj, "__plugin_meta__"):
                    PluginWrapper.__plugin_meta__ = obj.__plugin_meta__
                if hasattr(obj, "__plugin_version__"):
                    PluginWrapper.__plugin_version__ = obj.__plugin_version__
                if hasattr(obj, "__plugin_dependencies__"):
                    PluginWrapper.__plugin_dependencies__ = obj.__plugin_dependencies__
                if hasattr(obj, "__plugin_author__"):
                    PluginWrapper.__plugin_author__ = obj.__plugin_author__
                if hasattr(obj, "__plugin_license__"):
                    PluginWrapper.__plugin_license__ = obj.__plugin_license__
                
                return PluginWrapper
        
        # If still not found, check for module-level functions
        if hasattr(module, 'run') and inspect.isfunction(getattr(module, 'run')):
            # Create a wrapper class for the function
            class FunctionWrapper(PluginInterface):
                def execute(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
                    return module.run(inputs, config)
                
                def generate_code(self, config: Dict[str, Any]) -> str:
                    if hasattr(module, 'generate_code') and inspect.isfunction(getattr(module, 'generate_code')):
                        return module.generate_code(config)
                    return ""
            
            # Copy metadata from module
            if hasattr(module, "__plugin_meta__"):
                FunctionWrapper.__plugin_meta__ = module.__plugin_meta__
            if hasattr(module, "__plugin_version__"):
                FunctionWrapper.__plugin_version__ = module.__plugin_version__
            if hasattr(module, "__plugin_dependencies__"):
                FunctionWrapper.__plugin_dependencies__ = module.__plugin_dependencies__
            if hasattr(module, "__plugin_author__"):
                FunctionWrapper.__plugin_author__ = module.__plugin_author__
            if hasattr(module, "__plugin_license__"):
                FunctionWrapper.__plugin_license__ = module.__plugin_license__
            
            return FunctionWrapper
        elif hasattr(module, 'execute') and inspect.isfunction(getattr(module, 'execute')):
            # Create a wrapper class for the function
            class FunctionWrapper(PluginInterface):
                def execute(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
                    return module.execute(inputs, config)
                
                def generate_code(self, config: Dict[str, Any]) -> str:
                    if hasattr(module, 'generate_code') and inspect.isfunction(getattr(module, 'generate_code')):
                        return module.generate_code(config)
                    return ""
            
            # Copy metadata from module
            if hasattr(module, "__plugin_meta__"):
                FunctionWrapper.__plugin_meta__ = module.__plugin_meta__
            if hasattr(module, "__plugin_version__"):
                FunctionWrapper.__plugin_version__ = module.__plugin_version__
            if hasattr(module, "__plugin_dependencies__"):
                FunctionWrapper.__plugin_dependencies__ = module.__plugin_dependencies__
            if hasattr(module, "__plugin_author__"):
                FunctionWrapper.__plugin_author__ = module.__plugin_author__
            if hasattr(module, "__plugin_license__"):
                FunctionWrapper.__plugin_license__ = module.__plugin_license__
            
            return FunctionWrapper
        
        return None
    
    def _build_dependency_graph(self) -> None:
        """Build the plugin dependency graph."""
        # Initialize dependents
        self.plugin_dependents = {plugin_id: [] for plugin_id in self.plugin_classes}
        
        # Build dependents
        for plugin_id, dependencies in self.plugin_dependencies.items():
            for dependency in dependencies:
                if dependency in self.plugin_dependents:
                    self.plugin_dependents[dependency].append(plugin_id)
                else:
                    logger.warning(f"Plugin {plugin_id} depends on unknown plugin {dependency}")
    
    def _load_plugins_in_order(self) -> None:
        """Load plugins in dependency order."""
        # Get plugins with no dependencies
        to_load = [plugin_id for plugin_id, dependencies in self.plugin_dependencies.items() if not dependencies]
        loaded = set()
        
        # Load plugins in order
        while to_load:
            plugin_id = to_load.pop(0)
            
            # Skip if already loaded
            if plugin_id in loaded:
                continue
            
            # Check if all dependencies are loaded
            dependencies = self.plugin_dependencies.get(plugin_id, [])
            if not all(dep in loaded for dep in dependencies):
                # Put back at the end of the queue
                to_load.append(plugin_id)
                continue
            
            # Load the plugin
            try:
                plugin = self.plugin_classes[plugin_id]()
                
                # Initialize the plugin
                if plugin.initialize():
                    self.plugins[plugin_id] = plugin
                    loaded.add(plugin_id)
                    
                    # Add dependents to the load queue
                    for dependent in self.plugin_dependents.get(plugin_id, []):
                        if dependent not in loaded and dependent not in to_load:
                            to_load.append(dependent)
                else:
                    logger.error(f"Failed to initialize plugin {plugin_id}")
                    self.disabled_plugins.add(plugin_id)
            
            except Exception as e:
                logger.error(f"Error loading plugin {plugin_id}: {str(e)}")
                self.disabled_plugins.add(plugin_id)
        
        # Check for unloaded plugins (circular dependencies)
        unloaded = set(self.plugin_classes.keys()) - loaded - self.disabled_plugins
        if unloaded:
            logger.warning(f"Could not load plugins due to circular dependencies: {', '.join(unloaded)}")
            for plugin_id in unloaded:
                self.disabled_plugins.add(plugin_id)
    
    def execute_plugin(self, plugin_id: str, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a plugin.
        
        Args:
            plugin_id: Plugin ID
            inputs: Input values
            config: Configuration values
            
        Returns:
            Output values
            
        Raises:
            PluginExecutionError: If the plugin execution fails
        """
        start_time = time.time()
        
        try:
            # Get the plugin
            plugin = self.get_plugin(plugin_id)
            if not plugin:
                raise PluginExecutionError(f"Plugin {plugin_id} not found")
            
            # Set plugin state to running
            plugin._state = PluginLifecycleState.RUNNING
            
            # Validate inputs and config
            validated_inputs = plugin.validate_inputs(inputs)
            validated_config = plugin.validate_config(config)
            
            # Execute the plugin
            result = plugin.execute(validated_inputs, validated_config)
            
            # Update statistics
            execution_time_ms = (time.time() - start_time) * 1000
            plugin.update_statistics(execution_time_ms)
            
            # Update performance metrics
            self.performance_metrics["execution_time"] += time.time() - start_time
            self.performance_metrics["execution_count"] += 1
            
            # Reset plugin state
            plugin._state = PluginLifecycleState.INITIALIZED
            
            return result
        
        except Exception as e:
            # Update error statistics
            self.performance_metrics["error_count"] += 1
            
            # Get the plugin if it exists
            plugin = self.plugins.get(plugin_id)
            if plugin:
                # Update plugin state and error
                plugin._state = PluginLifecycleState.ERROR
                plugin._error = str(e)
                plugin.update_statistics((time.time() - start_time) * 1000, error=True)
            
            logger.error(f"Error executing plugin {plugin_id}: {str(e)}")
            raise PluginExecutionError(f"Error executing plugin {plugin_id}: {str(e)}")
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginInterface]:
        """Get a plugin by ID.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Plugin or None if not found
        """
        # Check if plugin is already loaded
        if plugin_id in self.plugins:
            return self.plugins[plugin_id]
        
        # Check if plugin is disabled
        if plugin_id in self.disabled_plugins:
            logger.warning(f"Plugin {plugin_id} is disabled")
            return None
        
        # Try to load the plugin
        try:
            # Check if plugin class is discovered
            if plugin_id in self.plugin_classes:
                plugin = self.plugin_classes[plugin_id]()
                
                # Initialize the plugin
                if plugin.initialize():
                    self.plugins[plugin_id] = plugin
                    return plugin
                else:
                    logger.error(f"Failed to initialize plugin {plugin_id}")
                    self.disabled_plugins.add(plugin_id)
                    return None
            
            # Try to discover the plugin
            self._discover_plugin(plugin_id, self.plugin_dir)
            
            # Check if plugin was discovered
            if plugin_id in self.plugin_classes:
                plugin = self.plugin_classes[plugin_id]()
                
                # Initialize the plugin
                if plugin.initialize():
                    self.plugins[plugin_id] = plugin
                    return plugin
                else:
                    logger.error(f"Failed to initialize plugin {plugin_id}")
                    self.disabled_plugins.add(plugin_id)
                    return None
            
            # Try to find the plugin in subdirectories
            if '.' not in plugin_id:
                for item in os.listdir(self.plugin_dir):
                    category_dir = os.path.join(self.plugin_dir, item)
                    if os.path.isdir(category_dir) and not item.startswith('__') and not item == '__pycache__':
                        qualified_id = f"{item}.{plugin_id}"
                        self._discover_plugin(qualified_id, category_dir)
                        
                        # Check if plugin was discovered
                        if qualified_id in self.plugin_classes:
                            plugin = self.plugin_classes[qualified_id]()
                            
                            # Initialize the plugin
                            if plugin.initialize():
                                self.plugins[qualified_id] = plugin
                                return plugin
                            else:
                                logger.error(f"Failed to initialize plugin {qualified_id}")
                                self.disabled_plugins.add(qualified_id)
                                return None
            
            return None
        
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_id}: {str(e)}")
            self.disabled_plugins.add(plugin_id)
            return None
    
    def get_plugin_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get metadata for a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Plugin metadata or None if not found
        """
        # Check if metadata is already loaded
        if plugin_id in self.plugin_metadata:
            return self.plugin_metadata[plugin_id]
        
        # Try to get the plugin
        plugin = self.get_plugin(plugin_id)
        if plugin:
            # Get metadata from plugin
            metadata = plugin.get_metadata()
            self.plugin_metadata[plugin_id] = metadata
            return metadata
        
        return None
    
    def get_all_plugin_metadata(self) -> Dict[str, PluginMetadata]:
        """Get metadata for all plugins.
        
        Returns:
            Dictionary of plugin metadata
        """
        return self.plugin_metadata
    
    def get_plugin_statistics(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Plugin statistics or None if not found
        """
        plugin = self.get_plugin(plugin_id)
        if plugin:
            return plugin.get_statistics()
        return None
    
    def get_all_plugin_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all plugins.
        
        Returns:
            Dictionary of plugin statistics
        """
        return {plugin_id: plugin.get_statistics() for plugin_id, plugin in self.plugins.items()}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the plugin manager.
        
        Returns:
            Dictionary of performance metrics
        """
        return self.performance_metrics
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if the plugin was disabled, False otherwise
        """
        # Check if plugin is loaded
        if plugin_id in self.plugins:
            # Clean up the plugin
            plugin = self.plugins[plugin_id]
            plugin.cleanup()
            
            # Remove from loaded plugins
            del self.plugins[plugin_id]
            
            # Add to disabled plugins
            self.disabled_plugins.add(plugin_id)
            
            logger.info(f"Disabled plugin {plugin_id}")
            return True
        
        # Add to disabled plugins even if not loaded
        self.disabled_plugins.add(plugin_id)
        return False
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a disabled plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if the plugin was enabled, False otherwise
        """
        # Check if plugin is disabled
        if plugin_id in self.disabled_plugins:
            # Remove from disabled plugins
            self.disabled_plugins.remove(plugin_id)
            
            # Try to load the plugin
            plugin = self.get_plugin(plugin_id)
            if plugin:
                logger.info(f"Enabled plugin {plugin_id}")
                return True
        
        return False
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """Reload a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if the plugin was reloaded, False otherwise
        """
        # Disable the plugin
        self.disable_plugin(plugin_id)
        
        # Remove from discovered plugins
        if plugin_id in self.plugin_classes:
            del self.plugin_classes[plugin_id]
        if plugin_id in self.plugin_modules:
            del self.plugin_modules[plugin_id]
        if plugin_id in self.plugin_metadata:
            del self.plugin_metadata[plugin_id]
        if plugin_id in self.plugin_dependencies:
            del self.plugin_dependencies[plugin_id]
        if plugin_id in self.plugin_dependents:
            del self.plugin_dependents[plugin_id]
        
        # Enable the plugin
        return self.enable_plugin(plugin_id)
    
    def cleanup(self) -> None:
        """Clean up all plugins."""
        for plugin_id, plugin in list(self.plugins.items()):
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up plugin {plugin_id}: {str(e)}")
        
        self.plugins.clear()
        logger.info("All plugins cleaned up")
    
    def _convert_dict_to_metadata(self, meta: Dict[str, Any], plugin_id: str) -> PluginMetadata:
        """Convert a dictionary to PluginMetadata.
        
        Args:
            meta: Dictionary containing metadata
            plugin_id: Plugin ID
            
        Returns:
            Plugin metadata
        """
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
    
    def _create_basic_metadata(self, plugin_class: Type[PluginInterface], plugin_id: str) -> PluginMetadata:
        """Create basic metadata from plugin class.
        
        Args:
            plugin_class: Plugin class
            plugin_id: Plugin ID
            
        Returns:
            Plugin metadata
        """
        # Try to extract information from docstring
        doc = inspect.getdoc(plugin_class) or ''
        description = doc.split('\n\n')[0] if doc else ''
        
        # Try to extract inputs and outputs from execute method
        inputs = []
        outputs = []
        config_fields = []
        
        # Check for execute method
        if hasattr(plugin_class, 'execute'):
            method = getattr(plugin_class, 'execute')
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
            version=getattr(plugin_class, '__plugin_version__', '1.0.0'),
            description=description,
            author=getattr(plugin_class, '__plugin_author__', 'Unknown'),
            category=NodeCategory.CUSTOM,
            inputs=inputs,
            outputs=outputs,
            config_fields=config_fields
        )
