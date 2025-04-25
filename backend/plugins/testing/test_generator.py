"""
Plugin Test Generator

This module provides a generator for plugin test cases.
"""

import logging
import os
import json
import random
import string
from typing import Dict, Any, Type, Optional, List, Tuple, Union
from datetime import datetime

from backend.app.models.plugin_interface import PluginInterface
from backend.plugins.testing.plugin_test_case import PluginTestCase

logger = logging.getLogger("workflow_builder")

class PluginTestGenerator:
    """
    Generator for plugin test cases.
    
    This class provides methods for generating test cases for plugins.
    """
    
    def __init__(self, plugin_class: Type[PluginInterface]):
        """
        Initialize the test generator.
        
        Args:
            plugin_class: The plugin class to generate tests for
        """
        self.plugin_class = plugin_class
        
    def generate_test_case(self, test_case_name: Optional[str] = None) -> Type[PluginTestCase]:
        """
        Generate a test case for the plugin.
        
        Args:
            test_case_name: Name of the test case class (optional)
            
        Returns:
            Test case class
        """
        # Get plugin metadata
        if not hasattr(self.plugin_class, "__plugin_meta__"):
            raise ValueError(f"Plugin {self.plugin_class.__name__} does not have __plugin_meta__ attribute")
            
        meta = self.plugin_class.__plugin_meta__
        
        # Get inputs, outputs, and config fields
        inputs = meta.inputs if hasattr(meta, "inputs") else []
        outputs = meta.outputs if hasattr(meta, "outputs") else []
        config_fields = meta.config_fields if hasattr(meta, "config_fields") else []
        
        # Generate test case name
        if not test_case_name:
            test_case_name = f"{self.plugin_class.__name__}TestCase"
            
        # Generate test methods
        test_methods = {}
        
        # Generate basic test method
        test_methods["test_plugin_initialization"] = self._generate_initialization_test()
        
        # Generate test methods for inputs
        for input_def in inputs:
            test_methods[f"test_input_{input_def.id}"] = self._generate_input_test(input_def)
            
        # Generate test methods for outputs
        for output_def in outputs:
            test_methods[f"test_output_{output_def.id}"] = self._generate_output_test(output_def)
            
        # Generate test methods for config fields
        for config_field in config_fields:
            test_methods[f"test_config_{config_field.id}"] = self._generate_config_test(config_field)
            
        # Generate test methods for validation
        test_methods["test_input_validation"] = self._generate_input_validation_test()
        test_methods["test_config_validation"] = self._generate_config_validation_test()
        
        # Generate test methods for edge cases
        test_methods["test_empty_inputs"] = self._generate_empty_inputs_test()
        test_methods["test_empty_config"] = self._generate_empty_config_test()
        
        # Generate test case class
        test_case_class = type(
            test_case_name,
            (PluginTestCase,),
            {
                "__doc__": f"Test case for {self.plugin_class.__name__}",
                **test_methods
            }
        )
        
        return test_case_class
        
    def _generate_initialization_test(self) -> callable:
        """
        Generate a test method for plugin initialization.
        
        Returns:
            Test method
        """
        def test_plugin_initialization(self):
            """Test plugin initialization."""
            self.assert_is_not_none(self.plugin_instance, "Plugin instance is None")
            
        return test_plugin_initialization
        
    def _generate_input_test(self, input_def) -> callable:
        """
        Generate a test method for an input.
        
        Args:
            input_def: Input definition
            
        Returns:
            Test method
        """
        def test_input(self):
            """Test input."""
            # Generate test input
            inputs = {input_def.id: self._generate_test_value(input_def.type)}
            
            # Execute plugin
            result = self.plugin_instance.execute(inputs, {})
            
            # Assert that the plugin executed without errors
            self.assert_is_not_none(result, f"Plugin execution with input {input_def.id} returned None")
            
        test_input.__doc__ = f"Test input {input_def.id}."
        return test_input
        
    def _generate_output_test(self, output_def) -> callable:
        """
        Generate a test method for an output.
        
        Args:
            output_def: Output definition
            
        Returns:
            Test method
        """
        def test_output(self):
            """Test output."""
            # Generate test inputs
            inputs = self._generate_test_inputs()
            
            # Execute plugin
            result = self.plugin_instance.execute(inputs, {})
            
            # Assert that the output is present
            self.assert_in(output_def.id, result, f"Output {output_def.id} not found in plugin result")
            
        test_output.__doc__ = f"Test output {output_def.id}."
        return test_output
        
    def _generate_config_test(self, config_field) -> callable:
        """
        Generate a test method for a config field.
        
        Args:
            config_field: Config field definition
            
        Returns:
            Test method
        """
        def test_config(self):
            """Test config field."""
            # Generate test inputs
            inputs = self._generate_test_inputs()
            
            # Generate test config
            config = {config_field.id: self._generate_test_value(config_field.type)}
            
            # Execute plugin
            result = self.plugin_instance.execute(inputs, config)
            
            # Assert that the plugin executed without errors
            self.assert_is_not_none(result, f"Plugin execution with config {config_field.id} returned None")
            
        test_config.__doc__ = f"Test config field {config_field.id}."
        return test_config
        
    def _generate_input_validation_test(self) -> callable:
        """
        Generate a test method for input validation.
        
        Returns:
            Test method
        """
        def test_input_validation(self):
            """Test input validation."""
            # Check if the plugin has a validate_inputs method
            if not hasattr(self.plugin_instance, 'validate_inputs'):
                self.assert_true(False, "Plugin does not have a validate_inputs method")
                return
                
            # Generate invalid inputs
            invalid_inputs = {"invalid_input": "invalid_value"}
            
            # Validate inputs
            try:
                validated_inputs = self.plugin_instance.validate_inputs(invalid_inputs)
                
                # If validation doesn't raise an exception, check if the inputs were modified
                self.assert_not_equal(validated_inputs, invalid_inputs, "Plugin does not validate inputs")
            except Exception:
                # If validation raises an exception, that's also acceptable
                pass
                
        return test_input_validation
        
    def _generate_config_validation_test(self) -> callable:
        """
        Generate a test method for config validation.
        
        Returns:
            Test method
        """
        def test_config_validation(self):
            """Test config validation."""
            # Check if the plugin has a validate_config method
            if not hasattr(self.plugin_instance, 'validate_config'):
                self.assert_true(False, "Plugin does not have a validate_config method")
                return
                
            # Generate invalid config
            invalid_config = {"invalid_config": "invalid_value"}
            
            # Validate config
            try:
                validated_config = self.plugin_instance.validate_config(invalid_config)
                
                # If validation doesn't raise an exception, check if the config was modified
                self.assert_not_equal(validated_config, invalid_config, "Plugin does not validate config")
            except Exception:
                # If validation raises an exception, that's also acceptable
                pass
                
        return test_config_validation
        
    def _generate_empty_inputs_test(self) -> callable:
        """
        Generate a test method for empty inputs.
        
        Returns:
            Test method
        """
        def test_empty_inputs(self):
            """Test empty inputs."""
            # Execute plugin with empty inputs
            try:
                result = self.plugin_instance.execute({}, {})
                
                # Assert that the plugin executed without errors
                self.assert_is_not_none(result, "Plugin execution with empty inputs returned None")
            except Exception as e:
                # If the plugin requires inputs, it should validate them and raise an exception
                # with a meaningful error message
                self.assert_true(str(e), "Plugin raised an exception with empty inputs but without an error message")
                
        return test_empty_inputs
        
    def _generate_empty_config_test(self) -> callable:
        """
        Generate a test method for empty config.
        
        Returns:
            Test method
        """
        def test_empty_config(self):
            """Test empty config."""
            # Generate test inputs
            inputs = self._generate_test_inputs()
            
            # Execute plugin with empty config
            try:
                result = self.plugin_instance.execute(inputs, {})
                
                # Assert that the plugin executed without errors
                self.assert_is_not_none(result, "Plugin execution with empty config returned None")
            except Exception as e:
                # If the plugin requires config, it should validate it and raise an exception
                # with a meaningful error message
                self.assert_true(str(e), "Plugin raised an exception with empty config but without an error message")
                
        return test_empty_config
        
    def _generate_test_inputs(self) -> Dict[str, Any]:
        """
        Generate test inputs for the plugin.
        
        Returns:
            Dictionary of test inputs
        """
        # Get plugin metadata
        if not hasattr(self.plugin_class, "__plugin_meta__"):
            return {}
            
        meta = self.plugin_class.__plugin_meta__
        
        # Get inputs
        inputs = meta.inputs if hasattr(meta, "inputs") else []
        
        # Generate test inputs
        test_inputs = {}
        for input_def in inputs:
            if input_def.required:
                test_inputs[input_def.id] = self._generate_test_value(input_def.type)
                
        return test_inputs
        
    def _generate_test_value(self, value_type: str) -> Any:
        """
        Generate a test value for a specific type.
        
        Args:
            value_type: Type of the value
            
        Returns:
            Test value
        """
        if value_type == "string":
            return "test_value_" + ''.join(random.choices(string.ascii_lowercase, k=5))
        elif value_type == "number":
            return random.randint(1, 100)
        elif value_type == "boolean":
            return random.choice([True, False])
        elif value_type == "array":
            return [self._generate_test_value("string") for _ in range(3)]
        elif value_type == "object":
            return {"key": self._generate_test_value("string")}
        else:
            return "test_value"
            
    def generate_test_file(self, output_dir: str, test_case_name: Optional[str] = None) -> str:
        """
        Generate a test file for the plugin.
        
        Args:
            output_dir: Directory to store the test file
            test_case_name: Name of the test case class (optional)
            
        Returns:
            Path to the generated test file
        """
        # Generate test case
        test_case_class = self.generate_test_case(test_case_name)
        
        # Generate file content
        content = f'''"""
Test case for {self.plugin_class.__name__}

This file was automatically generated by PluginTestGenerator.
"""

import unittest
from backend.plugins.testing.plugin_test_case import PluginTestCase
from {self.plugin_class.__module__} import {self.plugin_class.__name__}

class {test_case_class.__name__}(PluginTestCase):
    """Test case for {self.plugin_class.__name__}."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the test case."""
        super().__init__({self.plugin_class.__name__})
'''
        
        # Add test methods
        for name, method in test_case_class.__dict__.items():
            if name.startswith('test_') and callable(method):
                # Get method source
                source = f'''
    def {name}(self):
        """{method.__doc__}"""
        # TODO: Implement test
        pass
'''
                content += source
                
        # Add main block
        content += '''

if __name__ == '__main__':
    # Create test case
    test_case = {test_case_class.__name__}()
    
    # Run all tests
    result = test_case.run_all_tests()
    
    # Print results
    print(f"Total tests: {result['total_tests']}")
    print(f"Passed tests: {result['passed_tests']}")
    print(f"Failed tests: {result['failed_tests']}")
    print(f"Error tests: {result['error_tests']}")
    
    # Print details
    for test_result in result['test_results']:
        print(f"{test_result['test_name']}: {test_result['status']}")
        if test_result['status'] != 'passed':
            print(f"  Error: {test_result.get('error', 'Unknown error')}")
'''
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Generate file name
        plugin_name = self.plugin_class.__name__
        filename = f"test_{plugin_name.lower()}.py"
        filepath = os.path.join(output_dir, filename)
        
        # Write file
        with open(filepath, "w") as f:
            f.write(content)
            
        logger.info(f"Generated test file: {filepath}")
        
        return filepath
