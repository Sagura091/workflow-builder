#!/usr/bin/env python
"""
Standalone Plugin Testing Utility

This module provides a command-line utility for testing plugins outside the main backend environment.
Developers can use this utility to test their plugins locally before submitting them to the backend.
"""

import os
import sys
import argparse
import importlib.util
import json
import logging
from typing import Dict, Any, Type, Optional, List, Tuple, Union
from datetime import datetime
import inspect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("plugin_tester")

def import_module_from_path(module_path: str, module_name: Optional[str] = None) -> Any:
    """
    Import a module from a file path.
    
    Args:
        module_path: Path to the module file
        module_name: Name to give the module (optional)
        
    Returns:
        Imported module
    """
    if module_name is None:
        module_name = os.path.basename(module_path).replace(".py", "")
        
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise ImportError(f"Could not import module from {module_path}")
        
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    return module

def find_plugin_class(module: Any) -> Optional[Type]:
    """
    Find the plugin class in a module.
    
    Args:
        module: Module to search
        
    Returns:
        Plugin class or None if not found
    """
    # First, try to find classes that have __plugin_meta__ attribute
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and hasattr(obj, "__plugin_meta__"):
            return obj
            
    # If not found, look for classes that might be plugins
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and name.endswith(("Plugin", "Node")):
            return obj
            
    return None

def run_tests(plugin_path: str, output_dir: Optional[str] = None, generate_tests: bool = False) -> Dict[str, Any]:
    """
    Run tests for a plugin.
    
    Args:
        plugin_path: Path to the plugin file
        output_dir: Directory to store test results (optional)
        generate_tests: Whether to generate tests if none exist
        
    Returns:
        Dictionary containing the test results
    """
    # Add the current directory to the Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(plugin_path)))
    
    # Add the backend directory to the Python path if it exists
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if os.path.exists(backend_dir):
        sys.path.insert(0, backend_dir)
    
    try:
        # Import the plugin module
        plugin_module = import_module_from_path(plugin_path)
        
        # Find the plugin class
        plugin_class = find_plugin_class(plugin_module)
        if not plugin_class:
            raise ValueError(f"Could not find plugin class in {plugin_path}")
            
        # Import testing framework
        try:
            from backend.plugins.testing import (
                PluginTestCase,
                PluginTestRunner,
                PluginQualityChecker,
                ProductionValidator,
                PluginCertifier,
                PluginTestGenerator
            )
        except ImportError:
            # If the backend module is not available, use relative imports
            from plugin_test_case import PluginTestCase
            from test_runner import PluginTestRunner
            from quality_checker import PluginQualityChecker
            from production_validator import ProductionValidator
            from certification import PluginCertifier
            from test_generator import PluginTestGenerator
            
        # Check if there's a test file for the plugin
        plugin_dir = os.path.dirname(plugin_path)
        plugin_name = os.path.basename(plugin_path).replace(".py", "")
        test_file_path = os.path.join(plugin_dir, f"test_{plugin_name}.py")
        
        test_cases = []
        
        if os.path.exists(test_file_path):
            # Import the test module
            test_module = import_module_from_path(test_file_path)
            
            # Find test case classes
            for name, obj in inspect.getmembers(test_module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginTestCase) and 
                    obj != PluginTestCase):
                    # Create an instance of the test case
                    test_case = obj()
                    test_cases.append(test_case)
        elif generate_tests:
            # Generate a test case
            generator = PluginTestGenerator(plugin_class)
            test_case_class = generator.generate_test_case()
            test_case = test_case_class()
            test_cases.append(test_case)
            
            # Save the test case to a file if output_dir is specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                generator.generate_test_file(output_dir)
        
        # If no test cases found or generated, create a basic one
        if not test_cases:
            class BasicTestCase(PluginTestCase):
                def __init__(self):
                    super().__init__(plugin_class)
                
                def test_initialization(self):
                    self.assert_is_not_none(self.plugin_instance, "Plugin instance is None")
                    
                def test_metadata(self):
                    self.assert_true(hasattr(self.plugin_class, "__plugin_meta__"), "Plugin does not have __plugin_meta__ attribute")
                    
                def test_execute_method(self):
                    self.assert_true(hasattr(self.plugin_instance, "execute"), "Plugin does not have execute method")
            
            test_cases.append(BasicTestCase())
            
        # Run tests
        test_runner = PluginTestRunner(output_dir)
        test_results = test_runner.run_test_cases(test_cases)
        
        # Check quality
        quality_checker = PluginQualityChecker(plugin_class)
        quality_result = quality_checker.check_quality()
        
        # Validate production readiness
        validator = ProductionValidator(plugin_class, test_cases)
        production_result = validator.validate()
        
        # Certify the plugin
        certifier = PluginCertifier(plugin_class, test_cases)
        certification_result = certifier.certify()
        
        # Create final result
        result = {
            "plugin": plugin_class.__name__,
            "test_results": test_results,
            "quality": quality_result,
            "production_readiness": production_result,
            "certification": certification_result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save the result to a file if output_dir is specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            result_file_path = os.path.join(output_dir, f"{plugin_class.__name__}_test_result.json")
            with open(result_file_path, "w") as f:
                json.dump(result, f, indent=4)
                
        return result
        
    except Exception as e:
        logger.error(f"Error running tests: {e}", exc_info=True)
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def check_quality(plugin_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Check the quality of a plugin.
    
    Args:
        plugin_path: Path to the plugin file
        output_dir: Directory to store quality check results (optional)
        
    Returns:
        Dictionary containing the quality check results
    """
    # Add the current directory to the Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(plugin_path)))
    
    # Add the backend directory to the Python path if it exists
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if os.path.exists(backend_dir):
        sys.path.insert(0, backend_dir)
    
    try:
        # Import the plugin module
        plugin_module = import_module_from_path(plugin_path)
        
        # Find the plugin class
        plugin_class = find_plugin_class(plugin_module)
        if not plugin_class:
            raise ValueError(f"Could not find plugin class in {plugin_path}")
            
        # Import testing framework
        try:
            from backend.plugins.testing import PluginQualityChecker
        except ImportError:
            # If the backend module is not available, use relative imports
            from quality_checker import PluginQualityChecker
            
        # Check quality
        quality_checker = PluginQualityChecker(plugin_class)
        quality_result = quality_checker.check_quality()
        
        # Save the result to a file if output_dir is specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            result_file_path = os.path.join(output_dir, f"{plugin_class.__name__}_quality_check.json")
            with open(result_file_path, "w") as f:
                json.dump(quality_result, f, indent=4)
                
        return quality_result
        
    except Exception as e:
        logger.error(f"Error checking quality: {e}", exc_info=True)
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def generate_tests(plugin_path: str, output_dir: str) -> Dict[str, Any]:
    """
    Generate tests for a plugin.
    
    Args:
        plugin_path: Path to the plugin file
        output_dir: Directory to store generated tests
        
    Returns:
        Dictionary containing the test generation results
    """
    # Add the current directory to the Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(plugin_path)))
    
    # Add the backend directory to the Python path if it exists
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if os.path.exists(backend_dir):
        sys.path.insert(0, backend_dir)
    
    try:
        # Import the plugin module
        plugin_module = import_module_from_path(plugin_path)
        
        # Find the plugin class
        plugin_class = find_plugin_class(plugin_module)
        if not plugin_class:
            raise ValueError(f"Could not find plugin class in {plugin_path}")
            
        # Import testing framework
        try:
            from backend.plugins.testing import PluginTestGenerator
        except ImportError:
            # If the backend module is not available, use relative imports
            from test_generator import PluginTestGenerator
            
        # Generate tests
        generator = PluginTestGenerator(plugin_class)
        test_file_path = generator.generate_test_file(output_dir)
        
        return {
            "plugin": plugin_class.__name__,
            "test_file_path": test_file_path,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating tests: {e}", exc_info=True)
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Main entry point for the command-line utility."""
    parser = argparse.ArgumentParser(description="Standalone Plugin Testing Utility")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests for a plugin")
    test_parser.add_argument("plugin_path", help="Path to the plugin file")
    test_parser.add_argument("--output-dir", help="Directory to store test results")
    test_parser.add_argument("--generate-tests", action="store_true", help="Generate tests if none exist")
    
    # Quality command
    quality_parser = subparsers.add_parser("quality", help="Check the quality of a plugin")
    quality_parser.add_argument("plugin_path", help="Path to the plugin file")
    quality_parser.add_argument("--output-dir", help="Directory to store quality check results")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate tests for a plugin")
    generate_parser.add_argument("plugin_path", help="Path to the plugin file")
    generate_parser.add_argument("output_dir", help="Directory to store generated tests")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the appropriate command
    if args.command == "test":
        result = run_tests(args.plugin_path, args.output_dir, args.generate_tests)
        print(json.dumps(result, indent=4))
    elif args.command == "quality":
        result = check_quality(args.plugin_path, args.output_dir)
        print(json.dumps(result, indent=4))
    elif args.command == "generate":
        result = generate_tests(args.plugin_path, args.output_dir)
        print(json.dumps(result, indent=4))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
