"""
Plugin Importer

This module provides utilities for importing plugins into the backend.
"""

import os
import sys
import shutil
import importlib.util
import inspect
import json
import logging
from typing import Dict, Any, Type, Optional, List, Tuple, Union
from datetime import datetime

from backend.plugins.testing.validator import PluginValidator

logger = logging.getLogger("workflow_builder")

class PluginImporter:
    """
    Importer for importing plugins into the backend.
    
    This class provides methods for importing plugins into the backend.
    """
    
    def __init__(self, plugin_dir: str):
        """
        Initialize the importer.
        
        Args:
            plugin_dir: Directory where plugins are stored
        """
        self.plugin_dir = plugin_dir
        
    def import_plugin(self, plugin_path: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Import a plugin into the backend.
        
        Args:
            plugin_path: Path to the plugin file
            category: Category to import the plugin into (optional)
            
        Returns:
            Dictionary containing the import results
        """
        try:
            # Validate the plugin
            validation_result = PluginValidator.validate_plugin_file(plugin_path)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "message": "Plugin validation failed",
                    "validation_result": validation_result
                }
                
            # Import the plugin module
            spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
            if spec is None:
                return {
                    "success": False,
                    "message": f"Could not import module from {plugin_path}"
                }
                
            plugin_module = importlib.util.module_from_spec(spec)
            sys.modules["plugin_module"] = plugin_module
            spec.loader.exec_module(plugin_module)
            
            # Find the plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(plugin_module):
                if inspect.isclass(obj) and hasattr(obj, "__plugin_meta__"):
                    plugin_class = obj
                    break
                    
            if not plugin_class:
                return {
                    "success": False,
                    "message": f"Could not find plugin class in {plugin_path}"
                }
                
            # Get plugin metadata
            meta = plugin_class.__plugin_meta__
            
            # Determine the destination directory
            if category:
                dest_dir = os.path.join(self.plugin_dir, category)
            else:
                dest_dir = os.path.join(self.plugin_dir, meta.category)
                
            # Create the destination directory if it doesn't exist
            os.makedirs(dest_dir, exist_ok=True)
            
            # Determine the destination file name
            plugin_id = meta.id
            plugin_name = plugin_id.split(".")[-1]
            dest_file = os.path.join(dest_dir, f"{plugin_name}.py")
            
            # Copy the plugin file
            shutil.copy2(plugin_path, dest_file)
            
            return {
                "success": True,
                "message": f"Plugin imported successfully to {dest_file}",
                "plugin_id": plugin_id,
                "plugin_name": meta.name,
                "plugin_version": meta.version,
                "plugin_category": meta.category,
                "destination": dest_file
            }
            
        except Exception as e:
            logger.error(f"Error importing plugin: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error importing plugin: {str(e)}"
            }
            
    @staticmethod
    def import_plugin_to_backend(plugin_path: str, backend_dir: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Import a plugin into the backend.
        
        Args:
            plugin_path: Path to the plugin file
            backend_dir: Path to the backend directory
            category: Category to import the plugin into (optional)
            
        Returns:
            Dictionary containing the import results
        """
        # Determine the plugin directory
        plugin_dir = os.path.join(backend_dir, "plugins")
        
        # Create the importer
        importer = PluginImporter(plugin_dir)
        
        # Import the plugin
        return importer.import_plugin(plugin_path, category)
