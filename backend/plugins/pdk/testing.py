"""
Plugin Testing Utilities

This module provides utilities for testing plugins.
"""

import time
import json
import logging
from typing import Dict, Any, Type, Optional, List, Tuple

from backend.plugins.standalone_plugin_base import StandalonePluginBase
from backend.app.models.plugin_interface import PluginInterface

logger = logging.getLogger("workflow_builder")

class PluginTester:
    """
    Utility class for testing plugins.
    
    This class provides methods for testing plugins in various execution modes.
    """
    
    @staticmethod
    def test_plugin(plugin_class: Type[PluginInterface], 
                   inputs: Optional[Dict[str, Any]] = None,
                   config: Optional[Dict[str, Any]] = None,
                   execution_mode: str = "direct") -> Dict[str, Any]:
        """
        Test a plugin with the given inputs and configuration.
        
        Args:
            plugin_class: The plugin class to test
            inputs: Dictionary of input values (optional)
            config: Dictionary of configuration values (optional)
            execution_mode: Execution mode ('direct' or 'standalone')
            
        Returns:
            Dictionary containing the test results
        """
        # Check if the plugin is a standalone plugin
        if not issubclass(plugin_class, StandalonePluginBase):
            logger.warning(f"Plugin {plugin_class.__name__} is not a standalone plugin")
            
            # Create an instance and execute directly
            plugin = plugin_class()
            
            start_time = time.time()
            result = plugin.execute(inputs or {}, config or {})
            execution_time_ms = (time.time() - start_time) * 1000
            
            return {
                "result": result,
                "execution_time_ms": execution_time_ms,
                "execution_mode": "direct",
                "plugin": plugin_class.__name__
            }
        
        # Execute the plugin in the specified mode
        execution_context = {"execution_mode": execution_mode}
        result = plugin_class.run_standalone(inputs, config, execution_context)
        
        return result
    
    @staticmethod
    def benchmark_plugin(plugin_class: Type[PluginInterface],
                        inputs: Optional[Dict[str, Any]] = None,
                        config: Optional[Dict[str, Any]] = None,
                        iterations: int = 10) -> Dict[str, Any]:
        """
        Benchmark a plugin by running it multiple times and measuring performance.
        
        Args:
            plugin_class: The plugin class to benchmark
            inputs: Dictionary of input values (optional)
            config: Dictionary of configuration values (optional)
            iterations: Number of iterations to run
            
        Returns:
            Dictionary containing benchmark results
        """
        execution_times = []
        results = []
        
        for i in range(iterations):
            start_time = time.time()
            
            # Execute the plugin
            if issubclass(plugin_class, StandalonePluginBase):
                result = plugin_class.run_standalone(inputs, config, {"execution_mode": "direct"})
            else:
                plugin = plugin_class()
                result = plugin.execute(inputs or {}, config or {})
            
            execution_time_ms = (time.time() - start_time) * 1000
            execution_times.append(execution_time_ms)
            results.append(result)
        
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        return {
            "iterations": iterations,
            "average_time_ms": avg_time,
            "min_time_ms": min_time,
            "max_time_ms": max_time,
            "total_time_ms": sum(execution_times),
            "results": results,
            "plugin": plugin_class.__name__
        }
    
    @staticmethod
    def validate_plugin(plugin_class: Type[PluginInterface]) -> Tuple[bool, List[str]]:
        """
        Validate a plugin by checking its metadata and implementation.
        
        Args:
            plugin_class: The plugin class to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check if the plugin has metadata
        if not hasattr(plugin_class, "__plugin_meta__"):
            errors.append("Plugin does not have __plugin_meta__ attribute")
        
        # Check if the plugin has an execute method
        if not hasattr(plugin_class, "execute"):
            errors.append("Plugin does not have execute method")
        
        # If it's a standalone plugin, check additional requirements
        if issubclass(plugin_class, StandalonePluginBase):
            # Check if the plugin has standalone capabilities
            if not hasattr(plugin_class, "__standalone_capable__"):
                errors.append("Standalone plugin does not have __standalone_capable__ attribute")
        
        # Check metadata
        if hasattr(plugin_class, "__plugin_meta__"):
            meta = plugin_class.__plugin_meta__
            
            # Check required metadata fields
            if not hasattr(meta, "id") or not meta.id:
                errors.append("Plugin metadata does not have id")
            
            if not hasattr(meta, "name") or not meta.name:
                errors.append("Plugin metadata does not have name")
            
            if not hasattr(meta, "version") or not meta.version:
                errors.append("Plugin metadata does not have version")
        
        return len(errors) == 0, errors
