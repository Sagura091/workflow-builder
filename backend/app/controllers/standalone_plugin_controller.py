"""
Standalone Plugin Controller

This module provides a controller for standalone plugins.
"""

import logging
from typing import Dict, Any, List, Optional

from backend.app.services.plugin_loader import PluginLoader

logger = logging.getLogger("workflow_builder")

class StandalonePluginController:
    """
    Controller for standalone plugins.
    
    This controller provides methods for working with standalone plugins.
    """
    
    def __init__(self, plugin_loader: PluginLoader):
        """
        Initialize the controller.
        
        Args:
            plugin_loader: Plugin loader service
        """
        self.plugin_loader = plugin_loader
    
    def get_all_standalone_plugins(self) -> List[Dict[str, Any]]:
        """
        Get all standalone plugins.
        
        Returns:
            List of standalone plugins with their metadata
        """
        standalone_plugins = self.plugin_loader.get_standalone_plugins()
        
        # Convert to list of metadata
        result = []
        for plugin_id, plugin_class in standalone_plugins.items():
            # Get plugin metadata
            meta = plugin_class.__plugin_meta__
            
            # Add to result
            result.append({
                "id": plugin_id,
                "name": meta.name,
                "version": getattr(plugin_class, "__plugin_version__", "1.0.0"),
                "description": meta.description,
                "author": getattr(plugin_class, "__plugin_author__", "Unknown"),
                "category": meta.category,
                "tags": meta.tags,
                "inputs": [port.dict() for port in meta.inputs],
                "outputs": [port.dict() for port in meta.outputs],
                "config_fields": [field.dict() for field in meta.config_fields],
                "standalone_capable": getattr(plugin_class, "__standalone_capable__", True),
                "execution_modes": ["direct", "standalone"]
            })
        
        return result
    
    def get_standalone_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a standalone plugin by ID.
        
        Args:
            plugin_id: ID of the plugin to get
            
        Returns:
            Plugin metadata or None if not found
        """
        standalone_plugins = self.plugin_loader.get_standalone_plugins()
        
        if plugin_id not in standalone_plugins:
            return None
        
        plugin_class = standalone_plugins[plugin_id]
        
        # Get plugin metadata
        meta = plugin_class.__plugin_meta__
        
        # Return metadata
        return {
            "id": plugin_id,
            "name": meta.name,
            "version": getattr(plugin_class, "__plugin_version__", "1.0.0"),
            "description": meta.description,
            "author": getattr(plugin_class, "__plugin_author__", "Unknown"),
            "category": meta.category,
            "tags": meta.tags,
            "inputs": [port.dict() for port in meta.inputs],
            "outputs": [port.dict() for port in meta.outputs],
            "config_fields": [field.dict() for field in meta.config_fields],
            "standalone_capable": getattr(plugin_class, "__standalone_capable__", True),
            "execution_modes": ["direct", "standalone"]
        }
    
    def execute_standalone_plugin(self, plugin_id: str, inputs: Optional[Dict[str, Any]] = None,
                                config: Optional[Dict[str, Any]] = None,
                                execution_mode: str = "direct") -> Dict[str, Any]:
        """
        Execute a standalone plugin.
        
        Args:
            plugin_id: ID of the plugin to execute
            inputs: Input values (optional)
            config: Configuration values (optional)
            execution_mode: Execution mode ('direct' or 'standalone')
            
        Returns:
            Execution result
            
        Raises:
            ValueError: If the plugin is not found or is not a standalone plugin
        """
        try:
            return self.plugin_loader.execute_standalone_plugin(
                plugin_name=plugin_id,
                inputs=inputs,
                config=config,
                execution_mode=execution_mode
            )
        except Exception as e:
            logger.error(f"Error executing standalone plugin {plugin_id}: {str(e)}")
            raise
