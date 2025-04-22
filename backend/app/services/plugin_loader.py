import os
import importlib.util
import sys
from typing import Dict, Any, Optional
import json

class PluginLoader:
    """Service for loading plugins."""
    
    def __init__(self, plugin_dir: str = None):
        """Initialize the plugin loader."""
        if plugin_dir is None:
            # Default to the plugins directory in the project root
            self.plugin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "plugins")
        else:
            self.plugin_dir = plugin_dir
    
    def load_plugin(self, plugin_name: str) -> Optional[Any]:
        """Load a plugin by name."""
        plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")
        
        if not os.path.exists(plugin_path):
            return None
        
        try:
            # Load the plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None:
                return None
                
            plugin = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = plugin
            spec.loader.exec_module(plugin)
            
            return plugin
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {str(e)}")
            return None
    
    def load_all_plugins(self) -> Dict[str, Any]:
        """Load all plugins in the plugin directory."""
        plugins = {}
        
        if not os.path.exists(self.plugin_dir):
            return plugins
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_name = filename[:-3]
                plugin = self.load_plugin(plugin_name)
                
                if plugin and hasattr(plugin, "__plugin_meta__"):
                    plugins[plugin_name] = plugin
        
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
        """Delete a plugin from the plugin directory."""
        plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")
        
        if not os.path.exists(plugin_path):
            return False
        
        try:
            os.remove(plugin_path)
            return True
        except Exception as e:
            print(f"Error deleting plugin {plugin_name}: {str(e)}")
            return False
