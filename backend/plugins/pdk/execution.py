"""
Plugin Execution Utilities

This module provides utilities for executing plugins.
"""

import os
import sys
import json
import time
import logging
import argparse
from typing import Dict, Any, Type, Optional, List

from backend.plugins.standalone_plugin_base import StandalonePluginBase
from backend.app.models.plugin_interface import PluginInterface
from backend.plugins.pdk.testing import PluginTester

logger = logging.getLogger("workflow_builder")

class PluginExecutor:
    """
    Utility class for executing plugins from the command line.
    
    This class provides methods for executing plugins with inputs and configuration
    from the command line or from Python code.
    """
    
    @staticmethod
    def execute_plugin_from_cli(plugin_class: Type[PluginInterface]) -> None:
        """
        Execute a plugin from the command line.
        
        This method parses command line arguments and executes the plugin with
        the provided inputs and configuration.
        
        Args:
            plugin_class: The plugin class to execute
        """
        parser = argparse.ArgumentParser(description=f"Execute {plugin_class.__name__} plugin")
        
        # Add arguments
        parser.add_argument("--inputs", type=str, help="JSON string or file path for inputs")
        parser.add_argument("--config", type=str, help="JSON string or file path for configuration")
        parser.add_argument("--mode", type=str, default="direct", choices=["direct", "standalone"],
                           help="Execution mode (direct or standalone)")
        parser.add_argument("--output", type=str, help="Output file path")
        parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
        parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
        parser.add_argument("--iterations", type=int, default=10, help="Number of benchmark iterations")
        
        # Parse arguments
        args = parser.parse_args()
        
        # Parse inputs
        inputs = None
        if args.inputs:
            if os.path.isfile(args.inputs):
                with open(args.inputs, "r") as f:
                    inputs = json.load(f)
            else:
                try:
                    inputs = json.loads(args.inputs)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON for inputs: {args.inputs}")
                    sys.exit(1)
        
        # Parse config
        config = None
        if args.config:
            if os.path.isfile(args.config):
                with open(args.config, "r") as f:
                    config = json.load(f)
            else:
                try:
                    config = json.loads(args.config)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON for config: {args.config}")
                    sys.exit(1)
        
        # Execute the plugin
        if args.benchmark:
            result = PluginTester.benchmark_plugin(
                plugin_class=plugin_class,
                inputs=inputs,
                config=config,
                iterations=args.iterations
            )
        else:
            result = PluginTester.test_plugin(
                plugin_class=plugin_class,
                inputs=inputs,
                config=config,
                execution_mode=args.mode
            )
        
        # Output the result
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=4 if args.pretty else None)
        else:
            print(json.dumps(result, indent=4 if args.pretty else None))
    
    @staticmethod
    def execute_plugin(plugin_class: Type[PluginInterface],
                      inputs: Optional[Dict[str, Any]] = None,
                      config: Optional[Dict[str, Any]] = None,
                      execution_mode: str = "direct",
                      output_file: Optional[str] = None,
                      pretty_print: bool = True) -> Dict[str, Any]:
        """
        Execute a plugin with the given inputs and configuration.
        
        Args:
            plugin_class: The plugin class to execute
            inputs: Dictionary of input values (optional)
            config: Dictionary of configuration values (optional)
            execution_mode: Execution mode ('direct' or 'standalone')
            output_file: Output file path (optional)
            pretty_print: Whether to pretty print JSON output
            
        Returns:
            Dictionary containing the execution results
        """
        # Execute the plugin
        result = PluginTester.test_plugin(
            plugin_class=plugin_class,
            inputs=inputs,
            config=config,
            execution_mode=execution_mode
        )
        
        # Output the result
        if output_file:
            with open(output_file, "w") as f:
                json.dump(result, f, indent=4 if pretty_print else None)
        
        return result
