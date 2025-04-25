"""
Plugin Testing Controller

This module provides a controller for the plugin testing framework.
"""

import logging
import os
import json
import importlib
import inspect
from typing import Dict, Any, Type, Optional, List, Tuple, Union
from datetime import datetime

from backend.app.models.plugin_interface import PluginInterface
from backend.app.services.plugin_loader import PluginLoader
from backend.plugins.testing import (
    PluginTestCase,
    PluginTestRunner,
    PluginQualityChecker,
    ProductionValidator,
    PluginCertifier,
    CertificationLevel,
    PluginTestGenerator
)

logger = logging.getLogger("workflow_builder")

class PluginTestingController:
    """
    Controller for the plugin testing framework.

    This class provides methods for testing plugins.
    """

    def __init__(self, plugin_loader: PluginLoader):
        """
        Initialize the controller.

        Args:
            plugin_loader: Plugin loader service
        """
        self.plugin_loader = plugin_loader
        self.test_output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test_results")

        # Create test output directory if it doesn't exist
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)

    def check_plugin_quality(self, plugin_id: str) -> Dict[str, Any]:
        """
        Check the quality of a plugin.

        Args:
            plugin_id: ID of the plugin to check

        Returns:
            Dictionary containing the quality check results

        Raises:
            ValueError: If the plugin is not found
        """
        # Load the plugin
        plugin_module = self.plugin_loader.load_plugin(plugin_id)
        if not plugin_module:
            raise ValueError(f"Plugin {plugin_id} not found")

        # Find the plugin class
        plugin_class = self._find_plugin_class(plugin_module)
        if not plugin_class:
            raise ValueError(f"Plugin class not found in module {plugin_id}")

        # Check quality
        quality_checker = PluginQualityChecker(plugin_class)
        return quality_checker.check_quality()

    def validate_plugin_production_readiness(self, plugin_id: str) -> Dict[str, Any]:
        """
        Validate if a plugin is ready for production.

        Args:
            plugin_id: ID of the plugin to validate

        Returns:
            Dictionary containing the validation results

        Raises:
            ValueError: If the plugin is not found
        """
        # Load the plugin
        plugin_module = self.plugin_loader.load_plugin(plugin_id)
        if not plugin_module:
            raise ValueError(f"Plugin {plugin_id} not found")

        # Find the plugin class
        plugin_class = self._find_plugin_class(plugin_module)
        if not plugin_class:
            raise ValueError(f"Plugin class not found in module {plugin_id}")

        # Find test cases
        test_cases = self._find_test_cases(plugin_id, plugin_class)

        # Validate production readiness
        validator = ProductionValidator(plugin_class, test_cases)
        return validator.validate()

    def certify_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """
        Certify a plugin.

        Args:
            plugin_id: ID of the plugin to certify

        Returns:
            Dictionary containing the certification results

        Raises:
            ValueError: If the plugin is not found
        """
        # Load the plugin
        plugin_module = self.plugin_loader.load_plugin(plugin_id)
        if not plugin_module:
            raise ValueError(f"Plugin {plugin_id} not found")

        # Find the plugin class
        plugin_class = self._find_plugin_class(plugin_module)
        if not plugin_class:
            raise ValueError(f"Plugin class not found in module {plugin_id}")

        # Find test cases
        test_cases = self._find_test_cases(plugin_id, plugin_class)

        # Certify the plugin
        certifier = PluginCertifier(plugin_class, test_cases)
        return certifier.certify()

    def generate_plugin_tests(self, plugin_id: str) -> Dict[str, Any]:
        """
        Generate tests for a plugin.

        Args:
            plugin_id: ID of the plugin to generate tests for

        Returns:
            Dictionary containing the test generation results

        Raises:
            ValueError: If the plugin is not found
        """
        # Load the plugin
        plugin_module = self.plugin_loader.load_plugin(plugin_id)
        if not plugin_module:
            raise ValueError(f"Plugin {plugin_id} not found")

        # Find the plugin class
        plugin_class = self._find_plugin_class(plugin_module)
        if not plugin_class:
            raise ValueError(f"Plugin class not found in module {plugin_id}")

        # Generate tests
        generator = PluginTestGenerator(plugin_class)

        # Create test output directory
        plugin_test_dir = os.path.join(self.test_output_dir, plugin_id)
        if not os.path.exists(plugin_test_dir):
            os.makedirs(plugin_test_dir)

        # Generate test file
        test_file_path = generator.generate_test_file(plugin_test_dir)

        return {
            "plugin": plugin_id,
            "test_file_path": test_file_path,
            "timestamp": datetime.now().isoformat()
        }

    def run_plugin_tests(self, plugin_id: str) -> Dict[str, Any]:
        """
        Run tests for a plugin.

        Args:
            plugin_id: ID of the plugin to run tests for

        Returns:
            Dictionary containing the test results

        Raises:
            ValueError: If the plugin is not found
        """
        # Load the plugin
        plugin_module = self.plugin_loader.load_plugin(plugin_id)
        if not plugin_module:
            raise ValueError(f"Plugin {plugin_id} not found")

        # Find the plugin class
        plugin_class = self._find_plugin_class(plugin_module)
        if not plugin_class:
            raise ValueError(f"Plugin class not found in module {plugin_id}")

        # Find test cases
        test_cases = self._find_test_cases(plugin_id, plugin_class)

        # If no test cases found, generate one
        if not test_cases:
            generator = PluginTestGenerator(plugin_class)
            test_case_class = generator.generate_test_case()
            test_cases = [test_case_class()]

        # Run tests
        test_runner = PluginTestRunner(os.path.join(self.test_output_dir, plugin_id))
        return test_runner.run_test_cases(test_cases)

    def test_external_plugin(self, plugin_path: str) -> Dict[str, Any]:
        """
        Test an external plugin.

        Args:
            plugin_path: Path to the plugin file

        Returns:
            Dictionary containing the test results

        Raises:
            ValueError: If the plugin file is not found or is invalid
        """
        # Check if the plugin file exists
        if not os.path.exists(plugin_path):
            raise ValueError(f"Plugin file {plugin_path} not found")

        # Import the plugin module
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("external_plugin", plugin_path)
            if spec is None:
                raise ValueError(f"Could not import module from {plugin_path}")

            plugin_module = importlib.util.module_from_spec(spec)
            import sys
            sys.modules["external_plugin"] = plugin_module
            spec.loader.exec_module(plugin_module)

            # Find the plugin class
            plugin_class = self._find_plugin_class(plugin_module)
            if not plugin_class:
                raise ValueError(f"Plugin class not found in module {plugin_path}")

            # Validate the plugin
            from backend.plugins.testing.validator import PluginValidator
            validator = PluginValidator(plugin_class)
            validation_result = validator.validate()

            if not validation_result["valid"]:
                return {
                    "success": False,
                    "message": "Plugin validation failed",
                    "validation_result": validation_result
                }

            # Generate a test case
            generator = PluginTestGenerator(plugin_class)
            test_case_class = generator.generate_test_case()
            test_case = test_case_class()

            # Run tests
            test_runner = PluginTestRunner()
            test_results = test_runner.run_test_case(test_case)

            # Check quality
            quality_checker = PluginQualityChecker(plugin_class)
            quality_result = quality_checker.check_quality()

            # Validate production readiness
            validator = ProductionValidator(plugin_class, [test_case])
            production_result = validator.validate()

            # Certify the plugin
            certifier = PluginCertifier(plugin_class, [test_case])
            certification_result = certifier.certify()

            # Create final result
            return {
                "success": True,
                "plugin": plugin_class.__name__,
                "test_results": test_results,
                "quality": quality_result,
                "production_readiness": production_result,
                "certification": certification_result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error testing external plugin: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error testing external plugin: {str(e)}"
            }

    def import_external_plugin(self, plugin_path: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Import an external plugin into the backend.

        Args:
            plugin_path: Path to the plugin file
            category: Category to import the plugin into (optional)

        Returns:
            Dictionary containing the import results

        Raises:
            ValueError: If the plugin file is not found or is invalid
        """
        # Check if the plugin file exists
        if not os.path.exists(plugin_path):
            raise ValueError(f"Plugin file {plugin_path} not found")

        # Test the plugin first
        test_result = self.test_external_plugin(plugin_path)
        if not test_result.get("success", False):
            return test_result

        # Import the plugin
        from backend.plugins.testing.importer import PluginImporter
        plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        plugin_dir = os.path.join(plugin_dir, "plugins")

        importer = PluginImporter(plugin_dir)
        return importer.import_plugin(plugin_path, category)

    def _find_plugin_class(self, plugin_module) -> Optional[Type[PluginInterface]]:
        """
        Find the plugin class in a module.

        Args:
            plugin_module: Plugin module

        Returns:
            Plugin class or None if not found
        """
        # Find all classes in the module that inherit from PluginInterface
        plugin_classes = []
        for name, obj in inspect.getmembers(plugin_module):
            if inspect.isclass(obj) and issubclass(obj, PluginInterface) and obj != PluginInterface:
                plugin_classes.append(obj)

        # If only one class found, return it
        if len(plugin_classes) == 1:
            return plugin_classes[0]

        # If multiple classes found, return the one with __plugin_meta__
        for plugin_class in plugin_classes:
            if hasattr(plugin_class, "__plugin_meta__"):
                return plugin_class

        # If no class found, return None
        return None

    def _find_test_cases(self, plugin_id: str, plugin_class: Type[PluginInterface]) -> List[PluginTestCase]:
        """
        Find test cases for a plugin.

        Args:
            plugin_id: ID of the plugin
            plugin_class: Plugin class

        Returns:
            List of test cases
        """
        test_cases = []

        # Check if there's a test file for the plugin
        plugin_test_dir = os.path.join(self.test_output_dir, plugin_id)
        if os.path.exists(plugin_test_dir):
            for filename in os.listdir(plugin_test_dir):
                if filename.startswith("test_") and filename.endswith(".py"):
                    # Try to import the test module
                    try:
                        # Create a unique module name
                        module_name = f"plugin_tests.{plugin_id}.{filename[:-3]}"

                        # Add the test directory to the Python path
                        import sys
                        if self.test_output_dir not in sys.path:
                            sys.path.insert(0, self.test_output_dir)

                        # Import the module
                        spec = importlib.util.spec_from_file_location(
                            module_name,
                            os.path.join(plugin_test_dir, filename)
                        )
                        if spec is None:
                            continue

                        test_module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = test_module
                        spec.loader.exec_module(test_module)

                        # Find test case classes
                        for name, obj in inspect.getmembers(test_module):
                            if (inspect.isclass(obj) and
                                issubclass(obj, PluginTestCase) and
                                obj != PluginTestCase):
                                # Create an instance of the test case
                                test_case = obj(plugin_class)
                                test_cases.append(test_case)

                    except Exception as e:
                        logger.error(f"Error importing test module {filename}: {e}")

        return test_cases
