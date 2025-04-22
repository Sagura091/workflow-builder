"""
Plugin Loader Service

This module provides functionality to load plugins from the plugins directory.
"""

import os
import importlib.util
from typing import Any, Optional

class PluginLoaderService:
    """Service for loading plugins."""
    
    def __init__(self, plugin_dir: Optional[str] = None):
        """
        Initialize the plugin loader service.
        
        Args:
            plugin_dir: Path to the plugins directory. If None, uses the default.
        """
        if plugin_dir is None:
            # Get the path to the plugins directory
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.plugin_dir = os.path.join(current_dir, "plugins")
        else:
            self.plugin_dir = plugin_dir
    
    def load_plugin(self, name: str) -> Any:
        """
        Load a plugin by name.
        
        Args:
            name: The name of the plugin to load
            
        Returns:
            The loaded plugin module
            
        Raises:
            FileNotFoundError: If the plugin is not found
        """
        plugin_path = os.path.join(self.plugin_dir, f"{name}.py")
        if not os.path.exists(plugin_path):
            raise FileNotFoundError(f"Plugin {name} not found.")
        
        spec = importlib.util.spec_from_file_location(name, plugin_path)
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)
        return plugin

# For backwards compatibility
def load_plugin(name: str) -> Any:
    """
    Load a plugin by name.
    
    Args:
        name: The name of the plugin to load
        
    Returns:
        The loaded plugin module
        
    Raises:
        FileNotFoundError: If the plugin is not found
    """
    loader = PluginLoaderService()
    return loader.load_plugin(name)
