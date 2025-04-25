import os
import importlib.util
import sys
import inspect
import logging
from typing import Dict, Any, Optional, List, Type, Tuple
import json

from backend.app.models.plugin_interface import PluginInterface

logger = logging.getLogger("workflow_builder")

class PluginLoader:
    """
    Service for loading plugins.

    This service provides methods for loading plugins from the plugin directory,
    including standalone plugins that can be executed independently.
    """

    def __init__(self, plugin_dir: str = None, core_nodes_dir: str = None):
        """
        Initialize the plugin loader.

        Args:
            plugin_dir: Directory containing plugins (optional)
            core_nodes_dir: Directory containing core nodes (optional)
        """
        # Set plugin directory
        if plugin_dir is None:
            # Default to the plugins directory in the project root
            self.plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "plugins")
        else:
            self.plugin_dir = plugin_dir

        # Set core nodes directory
        if core_nodes_dir is None:
            # Default to the core_nodes directory in the project root
            self.core_nodes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "core_nodes")
        else:
            self.core_nodes_dir = core_nodes_dir

        # Cache for loaded plugins
        self.plugin_cache: Dict[str, Any] = {}

        # Cache for standalone plugins
        self.standalone_plugins: Dict[str, Type[PluginInterface]] = {}

    def load_plugin(self, plugin_name: str) -> Optional[Any]:
        """
        Load a plugin by name.

        This method loads a plugin from the plugin directory or core nodes directory.
        It supports both regular plugins and standalone plugins.

        Args:
            plugin_name: Name of the plugin to load

        Returns:
            Loaded plugin or None if the plugin could not be loaded
        """
        # Check if the plugin is already cached
        if plugin_name in self.plugin_cache:
            return self.plugin_cache[plugin_name]

        # Check if it's a core node
        if plugin_name.startswith("core."):
            node_name = plugin_name.split(".", 1)[1]
            node_path = os.path.join(self.core_nodes_dir, f"{node_name}.py")

            if os.path.exists(node_path):
                try:
                    # Load the core node module
                    spec = importlib.util.spec_from_file_location(plugin_name, node_path)
                    if spec is None:
                        return None

                    node_module = importlib.util.module_from_spec(spec)
                    sys.modules[plugin_name] = node_module
                    spec.loader.exec_module(node_module)

                    # Cache the node
                    self.plugin_cache[plugin_name] = node_module

                    return node_module
                except Exception as e:
                    logger.error(f"Error loading core node {plugin_name}: {str(e)}")
                    return None

        # Check if it's a plugin
        plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")

        # If the plugin file doesn't exist, try to find it in subdirectories
        if not os.path.exists(plugin_path):
            # Try to find the plugin in subdirectories
            for root, dirs, files in os.walk(self.plugin_dir):
                for file in files:
                    if file == f"{plugin_name.split('.')[-1]}.py":
                        plugin_path = os.path.join(root, file)
                        break

            # If still not found, return None
            if not os.path.exists(plugin_path):
                return None

        try:
            # Load the plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None:
                return None

            plugin_module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = plugin_module
            spec.loader.exec_module(plugin_module)

            # Check if it's a standalone plugin
            for name, obj in inspect.getmembers(plugin_module):
                if (inspect.isclass(obj) and
                    issubclass(obj, PluginInterface) and
                    hasattr(obj, "__standalone_capable__") and
                    obj.__standalone_capable__):
                    # Register as a standalone plugin
                    self.standalone_plugins[plugin_name] = obj
                    break

            # Cache the plugin
            self.plugin_cache[plugin_name] = plugin_module

            return plugin_module
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
            return None

    def load_all_plugins(self) -> Dict[str, Any]:
        """
        Load all plugins in the plugin directory.

        This method loads all plugins from the plugin directory and its subdirectories.
        It also discovers standalone plugins.

        Returns:
            Dictionary of loaded plugins
        """
        plugins = {}

        if not os.path.exists(self.plugin_dir):
            logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            return plugins

        # Load plugins from the root directory
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_name = filename[:-3]
                plugin = self.load_plugin(plugin_name)

                if plugin and hasattr(plugin, "__plugin_meta__"):
                    plugins[plugin_name] = plugin

        # Load plugins from subdirectories
        for root, _, files in os.walk(self.plugin_dir):
            # Skip the root directory (already processed)
            if root == self.plugin_dir:
                continue

            # Skip __pycache__ and other special directories
            if os.path.basename(root).startswith("__"):
                continue

            # Get the relative path from the plugin directory
            rel_path = os.path.relpath(root, self.plugin_dir)

            # Replace path separators with dots
            package_prefix = rel_path.replace(os.path.sep, ".")

            # Load plugins from this directory
            for filename in files:
                if filename.endswith(".py") and not filename.startswith("__"):
                    plugin_name = f"{package_prefix}.{filename[:-3]}"
                    plugin = self.load_plugin(plugin_name)

                    if plugin and hasattr(plugin, "__plugin_meta__"):
                        plugins[plugin_name] = plugin

        logger.info(f"Loaded {len(plugins)} plugins")
        logger.info(f"Discovered {len(self.standalone_plugins)} standalone plugins")

        return plugins

    def save_plugin(self, plugin_name: str, plugin_code: str) -> bool:
        """Save a plugin to the plugin directory."""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)

        plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")

        try:
            with open(plugin_path, "w") as f:
                f.write(plugin_code)

            return True
        except Exception as e:
            print(f"Error saving plugin {plugin_name}: {str(e)}")
            return False

    def delete_plugin(self, plugin_name: str) -> bool:
        """
        Delete a plugin from the plugin directory.

        Args:
            plugin_name: Name of the plugin to delete

        Returns:
            True if the plugin was deleted, False otherwise
        """
        plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")

        if not os.path.exists(plugin_path):
            return False

        try:
            os.remove(plugin_path)

            # Remove from cache
            if plugin_name in self.plugin_cache:
                del self.plugin_cache[plugin_name]

            # Remove from standalone plugins
            if plugin_name in self.standalone_plugins:
                del self.standalone_plugins[plugin_name]

            return True
        except Exception as e:
            logger.error(f"Error deleting plugin {plugin_name}: {str(e)}")
            return False

    def get_standalone_plugins(self) -> Dict[str, Type[PluginInterface]]:
        """
        Get all standalone plugins.

        Returns:
            Dictionary of standalone plugins
        """
        return self.standalone_plugins

    def execute_standalone_plugin(self, plugin_name: str, inputs: Optional[Dict[str, Any]] = None,
                                 config: Optional[Dict[str, Any]] = None,
                                 execution_mode: str = "direct") -> Dict[str, Any]:
        """
        Execute a standalone plugin.

        Args:
            plugin_name: Name of the plugin to execute
            inputs: Dictionary of input values (optional)
            config: Dictionary of configuration values (optional)
            execution_mode: Execution mode ('direct' or 'standalone')

        Returns:
            Dictionary containing the execution results

        Raises:
            ValueError: If the plugin is not found or is not a standalone plugin
        """
        # Load the plugin if not already loaded
        if plugin_name not in self.standalone_plugins:
            plugin = self.load_plugin(plugin_name)

            if not plugin or plugin_name not in self.standalone_plugins:
                raise ValueError(f"Plugin {plugin_name} not found or is not a standalone plugin")

        # Get the plugin class
        plugin_class = self.standalone_plugins[plugin_name]

        # Execute the plugin
        execution_context = {"execution_mode": execution_mode}
        result = plugin_class.run_standalone(inputs, config, execution_context)

        return result
