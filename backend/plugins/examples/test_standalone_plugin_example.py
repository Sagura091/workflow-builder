"""
Test case for StandalonePluginExample

This file demonstrates how to create a test case for a plugin.
"""

from backend.plugins.testing import PluginTestCase
from backend.plugins.examples.standalone_plugin_example import StandalonePluginExample

class StandalonePluginExampleTestCase(PluginTestCase):
    """Test case for StandalonePluginExample."""
    
    def __init__(self):
        """Initialize the test case."""
        super().__init__(StandalonePluginExample)
    
    def test_initialization(self):
        """Test plugin initialization."""
        self.assert_is_not_none(self.plugin_instance, "Plugin instance is None")
    
    def test_basic_execution(self):
        """Test basic plugin execution."""
        # Define inputs and config
        inputs = {
            "text": "Hello, World!",
            "count": 2
        }
        config = {
            "prefix": "Start: ",
            "suffix": " :End",
            "uppercase": False
        }
        
        # Execute plugin
        result = self.plugin_instance.execute(inputs, config)
        
        # Assert that the result contains the expected keys
        self.assert_in("result", result, "Result does not contain 'result' key")
        self.assert_in("length", result, "Result does not contain 'length' key")
        
        # Assert that the result is correct
        expected_result = "Start: Hello, World!Hello, World! :End"
        self.assert_equal(result["result"], expected_result, "Result is not correct")
        self.assert_equal(result["length"], len(expected_result), "Length is not correct")
    
    def test_uppercase(self):
        """Test uppercase config option."""
        # Define inputs and config
        inputs = {
            "text": "Hello, World!",
            "count": 1
        }
        config = {
            "prefix": "",
            "suffix": "",
            "uppercase": True
        }
        
        # Execute plugin
        result = self.plugin_instance.execute(inputs, config)
        
        # Assert that the result is uppercase
        self.assert_equal(result["result"], "HELLO, WORLD!", "Result is not uppercase")
    
    def test_input_validation(self):
        """Test input validation."""
        # Define invalid inputs
        inputs = {
            "text": 123,  # Should be a string
            "count": "not a number"  # Should be a number
        }
        config = {}
        
        # Validate inputs
        validated_inputs = self.plugin_instance.validate_inputs(inputs)
        
        # Assert that the inputs were validated
        self.assert_equal(type(validated_inputs["text"]), str, "Text was not converted to string")
        self.assert_equal(type(validated_inputs["count"]), int, "Count was not converted to integer")
    
    def test_config_validation(self):
        """Test config validation."""
        # Define invalid config
        config = {
            "prefix": 123,  # Should be a string
            "suffix": 456,  # Should be a string
            "uppercase": "not a boolean"  # Should be a boolean
        }
        
        # Validate config
        validated_config = self.plugin_instance.validate_config(config)
        
        # Assert that the config was validated
        self.assert_equal(type(validated_config["prefix"]), str, "Prefix was not converted to string")
        self.assert_equal(type(validated_config["suffix"]), str, "Suffix was not converted to string")
        self.assert_equal(type(validated_config["uppercase"]), bool, "Uppercase was not converted to boolean")
    
    def test_empty_inputs(self):
        """Test empty inputs."""
        # Execute plugin with empty inputs
        result = self.plugin_instance.execute({}, {})
        
        # Assert that the result contains the expected keys
        self.assert_in("result", result, "Result does not contain 'result' key")
        self.assert_in("length", result, "Result does not contain 'length' key")
        
        # Assert that the result is correct (empty string)
        self.assert_equal(result["result"], "", "Result is not an empty string")
        self.assert_equal(result["length"], 0, "Length is not 0")

if __name__ == "__main__":
    # Create test case
    test_case = StandalonePluginExampleTestCase()
    
    # Run all tests
    result = test_case.run_all_tests()
    
    # Print results
    print(f"Total tests: {result['total_tests']}")
    print(f"Passed tests: {result['passed_tests']}")
    print(f"Failed tests: {result['failed_tests']}")
    print(f"Error tests: {result['error_tests']}")
    
    # Print details
    for test_result in result["test_results"]:
        print(f"{test_result['test_name']}: {test_result['status']}")
        if test_result["status"] != "passed":
            print(f"  Error: {test_result.get('error', 'Unknown error')}")
            print(f"  Traceback: {test_result.get('traceback', 'No traceback')}")
