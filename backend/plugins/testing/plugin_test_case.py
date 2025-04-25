"""
Plugin Test Case

This module provides a base class for plugin test cases.
"""

import time
import logging
import traceback
from typing import Dict, Any, Type, Optional, List, Callable, Tuple, Union
from datetime import datetime

from backend.app.models.plugin_interface import PluginInterface
from backend.plugins.standalone_plugin_base import StandalonePluginBase

logger = logging.getLogger("workflow_builder")

class PluginTestCase:
    """
    Base class for plugin test cases.
    
    This class provides methods for testing plugins, including setup, teardown,
    and assertion utilities.
    """
    
    def __init__(self, plugin_class: Type[PluginInterface]):
        """
        Initialize the test case.
        
        Args:
            plugin_class: The plugin class to test
        """
        self.plugin_class = plugin_class
        self.plugin_instance = None
        self.test_results = []
        self.setup_executed = False
        self.teardown_executed = False
        
    def setup(self):
        """
        Set up the test case.
        
        This method is called before each test method.
        Override this method to perform setup tasks.
        """
        self.plugin_instance = self.plugin_class()
        self.setup_executed = True
        
    def teardown(self):
        """
        Tear down the test case.
        
        This method is called after each test method.
        Override this method to perform cleanup tasks.
        """
        self.plugin_instance = None
        self.teardown_executed = True
        
    def run_test(self, test_method: Callable) -> Dict[str, Any]:
        """
        Run a test method.
        
        Args:
            test_method: The test method to run
            
        Returns:
            Dictionary containing the test results
        """
        test_name = test_method.__name__
        start_time = time.time()
        
        try:
            # Set up
            self.setup()
            
            # Run the test
            test_method()
            
            # Tear down
            self.teardown()
            
            # Record success
            execution_time_ms = (time.time() - start_time) * 1000
            result = {
                "test_name": test_name,
                "status": "passed",
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
            
        except AssertionError as e:
            # Record assertion failure
            execution_time_ms = (time.time() - start_time) * 1000
            result = {
                "test_name": test_name,
                "status": "failed",
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            self.test_results.append(result)
            return result
            
        except Exception as e:
            # Record error
            execution_time_ms = (time.time() - start_time) * 1000
            result = {
                "test_name": test_name,
                "status": "error",
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            self.test_results.append(result)
            return result
            
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all test methods in the test case.
        
        Returns:
            Dictionary containing the test results
        """
        # Find all test methods
        test_methods = [
            method for method in dir(self)
            if method.startswith('test_') and callable(getattr(self, method))
        ]
        
        # Run each test method
        for method_name in test_methods:
            method = getattr(self, method_name)
            self.run_test(method)
            
        # Calculate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "passed")
        failed_tests = sum(1 for result in self.test_results if result["status"] == "failed")
        error_tests = sum(1 for result in self.test_results if result["status"] == "error")
        
        # Return summary
        return {
            "plugin": self.plugin_class.__name__,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": (passed_tests / total_tests) if total_tests > 0 else 0,
            "test_results": self.test_results
        }
        
    # Assertion methods
    
    def assert_equal(self, actual: Any, expected: Any, message: Optional[str] = None):
        """
        Assert that two values are equal.
        
        Args:
            actual: The actual value
            expected: The expected value
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the values are not equal
        """
        if actual != expected:
            error_message = message or f"Expected {expected}, but got {actual}"
            raise AssertionError(error_message)
            
    def assert_not_equal(self, actual: Any, expected: Any, message: Optional[str] = None):
        """
        Assert that two values are not equal.
        
        Args:
            actual: The actual value
            expected: The expected value
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the values are equal
        """
        if actual == expected:
            error_message = message or f"Expected {actual} to be different from {expected}"
            raise AssertionError(error_message)
            
    def assert_true(self, value: bool, message: Optional[str] = None):
        """
        Assert that a value is True.
        
        Args:
            value: The value to check
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the value is not True
        """
        if not value:
            error_message = message or f"Expected True, but got {value}"
            raise AssertionError(error_message)
            
    def assert_false(self, value: bool, message: Optional[str] = None):
        """
        Assert that a value is False.
        
        Args:
            value: The value to check
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the value is not False
        """
        if value:
            error_message = message or f"Expected False, but got {value}"
            raise AssertionError(error_message)
            
    def assert_is_none(self, value: Any, message: Optional[str] = None):
        """
        Assert that a value is None.
        
        Args:
            value: The value to check
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the value is not None
        """
        if value is not None:
            error_message = message or f"Expected None, but got {value}"
            raise AssertionError(error_message)
            
    def assert_is_not_none(self, value: Any, message: Optional[str] = None):
        """
        Assert that a value is not None.
        
        Args:
            value: The value to check
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the value is None
        """
        if value is None:
            error_message = message or "Expected a value, but got None"
            raise AssertionError(error_message)
            
    def assert_in(self, item: Any, container: Any, message: Optional[str] = None):
        """
        Assert that an item is in a container.
        
        Args:
            item: The item to check
            container: The container to check
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the item is not in the container
        """
        if item not in container:
            error_message = message or f"Expected {item} to be in {container}"
            raise AssertionError(error_message)
            
    def assert_not_in(self, item: Any, container: Any, message: Optional[str] = None):
        """
        Assert that an item is not in a container.
        
        Args:
            item: The item to check
            container: The container to check
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the item is in the container
        """
        if item in container:
            error_message = message or f"Expected {item} not to be in {container}"
            raise AssertionError(error_message)
            
    def assert_raises(self, exception_type: Type[Exception], callable_obj: Callable, *args, **kwargs):
        """
        Assert that a callable raises a specific exception.
        
        Args:
            exception_type: The expected exception type
            callable_obj: The callable to execute
            *args: Arguments to pass to the callable
            **kwargs: Keyword arguments to pass to the callable
        
        Raises:
            AssertionError: If the callable does not raise the expected exception
        """
        try:
            callable_obj(*args, **kwargs)
        except Exception as e:
            if isinstance(e, exception_type):
                return
            else:
                raise AssertionError(f"Expected {exception_type.__name__}, but got {type(e).__name__}")
        
        raise AssertionError(f"Expected {exception_type.__name__}, but no exception was raised")
        
    # Plugin-specific assertion methods
    
    def assert_plugin_output_contains(self, inputs: Dict[str, Any], config: Dict[str, Any], 
                                     expected_key: str, message: Optional[str] = None):
        """
        Assert that a plugin's output contains a specific key.
        
        Args:
            inputs: The inputs to pass to the plugin
            config: The configuration to pass to the plugin
            expected_key: The expected key in the output
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the plugin's output does not contain the expected key
        """
        result = self.plugin_instance.execute(inputs, config)
        if expected_key not in result:
            error_message = message or f"Expected plugin output to contain key '{expected_key}', but it was not found"
            raise AssertionError(error_message)
            
    def assert_plugin_output_equals(self, inputs: Dict[str, Any], config: Dict[str, Any], 
                                   expected_output: Dict[str, Any], message: Optional[str] = None):
        """
        Assert that a plugin's output equals the expected output.
        
        Args:
            inputs: The inputs to pass to the plugin
            config: The configuration to pass to the plugin
            expected_output: The expected output
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the plugin's output does not equal the expected output
        """
        result = self.plugin_instance.execute(inputs, config)
        if result != expected_output:
            error_message = message or f"Expected plugin output to be {expected_output}, but got {result}"
            raise AssertionError(error_message)
            
    def assert_plugin_output_key_equals(self, inputs: Dict[str, Any], config: Dict[str, Any], 
                                       key: str, expected_value: Any, message: Optional[str] = None):
        """
        Assert that a specific key in a plugin's output equals the expected value.
        
        Args:
            inputs: The inputs to pass to the plugin
            config: The configuration to pass to the plugin
            key: The key to check
            expected_value: The expected value
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the key in the plugin's output does not equal the expected value
        """
        result = self.plugin_instance.execute(inputs, config)
        if key not in result:
            error_message = message or f"Expected plugin output to contain key '{key}', but it was not found"
            raise AssertionError(error_message)
            
        if result[key] != expected_value:
            error_message = message or f"Expected plugin output key '{key}' to be {expected_value}, but got {result[key]}"
            raise AssertionError(error_message)
            
    def assert_plugin_execution_time_less_than(self, inputs: Dict[str, Any], config: Dict[str, Any], 
                                             max_time_ms: float, message: Optional[str] = None):
        """
        Assert that a plugin's execution time is less than a specific value.
        
        Args:
            inputs: The inputs to pass to the plugin
            config: The configuration to pass to the plugin
            max_time_ms: The maximum execution time in milliseconds
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the plugin's execution time is greater than or equal to the maximum time
        """
        start_time = time.time()
        self.plugin_instance.execute(inputs, config)
        execution_time_ms = (time.time() - start_time) * 1000
        
        if execution_time_ms >= max_time_ms:
            error_message = message or f"Expected plugin execution time to be less than {max_time_ms}ms, but got {execution_time_ms}ms"
            raise AssertionError(error_message)
            
    def assert_plugin_validates_inputs(self, invalid_inputs: Dict[str, Any], config: Dict[str, Any], 
                                      message: Optional[str] = None):
        """
        Assert that a plugin validates its inputs.
        
        Args:
            invalid_inputs: Invalid inputs to pass to the plugin
            config: The configuration to pass to the plugin
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the plugin does not validate its inputs
        """
        try:
            # First, check if the plugin has a validate_inputs method
            if not hasattr(self.plugin_instance, 'validate_inputs'):
                error_message = message or "Plugin does not have a validate_inputs method"
                raise AssertionError(error_message)
                
            # Then, check if the validate_inputs method actually validates the inputs
            validated_inputs = self.plugin_instance.validate_inputs(invalid_inputs)
            
            # If the validated inputs are the same as the invalid inputs, the plugin is not validating
            if validated_inputs == invalid_inputs:
                error_message = message or "Plugin does not validate its inputs"
                raise AssertionError(error_message)
                
        except Exception as e:
            # If an exception is raised during validation, that's good - it means the plugin is validating
            if not isinstance(e, AssertionError):
                return
            else:
                raise
                
    def assert_plugin_validates_config(self, invalid_config: Dict[str, Any], message: Optional[str] = None):
        """
        Assert that a plugin validates its configuration.
        
        Args:
            invalid_config: Invalid configuration to pass to the plugin
            message: Optional message to display on failure
        
        Raises:
            AssertionError: If the plugin does not validate its configuration
        """
        try:
            # First, check if the plugin has a validate_config method
            if not hasattr(self.plugin_instance, 'validate_config'):
                error_message = message or "Plugin does not have a validate_config method"
                raise AssertionError(error_message)
                
            # Then, check if the validate_config method actually validates the configuration
            validated_config = self.plugin_instance.validate_config(invalid_config)
            
            # If the validated configuration is the same as the invalid configuration, the plugin is not validating
            if validated_config == invalid_config:
                error_message = message or "Plugin does not validate its configuration"
                raise AssertionError(error_message)
                
        except Exception as e:
            # If an exception is raised during validation, that's good - it means the plugin is validating
            if not isinstance(e, AssertionError):
                return
            else:
                raise
