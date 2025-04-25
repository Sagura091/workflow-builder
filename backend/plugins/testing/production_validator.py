"""
Plugin Production Validator

This module provides a validator for determining if a plugin is ready for production.
"""

import logging
import os
import json
from typing import Dict, Any, Type, Optional, List, Tuple, Union
from datetime import datetime

from backend.app.models.plugin_interface import PluginInterface
from backend.plugins.testing.quality_checker import PluginQualityChecker
from backend.plugins.testing.plugin_test_case import PluginTestCase
from backend.plugins.testing.test_runner import PluginTestRunner

logger = logging.getLogger("workflow_builder")

class ProductionValidator:
    """
    Validator for determining if a plugin is ready for production.
    
    This class provides methods for validating if a plugin is ready for production.
    """
    
    def __init__(self, plugin_class: Type[PluginInterface], test_cases: Optional[List[PluginTestCase]] = None):
        """
        Initialize the production validator.
        
        Args:
            plugin_class: The plugin class to validate
            test_cases: List of test cases for the plugin (optional)
        """
        self.plugin_class = plugin_class
        self.test_cases = test_cases or []
        self.quality_checker = PluginQualityChecker(plugin_class)
        
    def validate(self) -> Dict[str, Any]:
        """
        Validate if the plugin is ready for production.
        
        Returns:
            Dictionary containing the validation results
        """
        # Check quality
        quality_result = self.quality_checker.check_quality()
        
        # Run tests
        test_results = {}
        if self.test_cases:
            test_runner = PluginTestRunner()
            for test_case in self.test_cases:
                test_results[test_case.__class__.__name__] = test_runner.run_test_case(test_case)
                
        # Calculate test coverage
        test_coverage = self._calculate_test_coverage()
        
        # Determine production readiness
        is_ready, reasons = self._determine_production_readiness(quality_result, test_results, test_coverage)
        
        # Create result
        return {
            "plugin": self.plugin_class.__name__,
            "is_ready": is_ready,
            "reasons": reasons,
            "quality": quality_result,
            "test_results": test_results,
            "test_coverage": test_coverage,
            "timestamp": datetime.now().isoformat()
        }
        
    def _calculate_test_coverage(self) -> Dict[str, Any]:
        """
        Calculate test coverage for the plugin.
        
        Returns:
            Dictionary containing the test coverage
        """
        # Get plugin metadata
        if not hasattr(self.plugin_class, "__plugin_meta__"):
            return {
                "inputs_coverage": 0,
                "outputs_coverage": 0,
                "config_fields_coverage": 0,
                "overall_coverage": 0
            }
            
        meta = self.plugin_class.__plugin_meta__
        
        # Get inputs, outputs, and config fields
        inputs = meta.inputs if hasattr(meta, "inputs") else []
        outputs = meta.outputs if hasattr(meta, "outputs") else []
        config_fields = meta.config_fields if hasattr(meta, "config_fields") else []
        
        # Calculate coverage
        inputs_coverage = 0
        outputs_coverage = 0
        config_fields_coverage = 0
        
        # Check if we have test cases
        if not self.test_cases:
            return {
                "inputs_coverage": 0,
                "outputs_coverage": 0,
                "config_fields_coverage": 0,
                "overall_coverage": 0
            }
            
        # Calculate coverage based on test cases
        # This is a simplified calculation - in a real implementation, you would
        # analyze the test cases to determine which inputs, outputs, and config fields
        # are actually tested
        
        # For now, we'll just use a simple heuristic based on the number of test cases
        num_test_cases = len(self.test_cases)
        num_test_methods = sum(
            len([method for method in dir(test_case) if method.startswith("test_")])
            for test_case in self.test_cases
        )
        
        # Calculate coverage based on the number of test methods
        if inputs:
            inputs_coverage = min(1.0, num_test_methods / (len(inputs) * 2))
            
        if outputs:
            outputs_coverage = min(1.0, num_test_methods / (len(outputs) * 2))
            
        if config_fields:
            config_fields_coverage = min(1.0, num_test_methods / (len(config_fields) * 2))
            
        # Calculate overall coverage
        overall_coverage = (inputs_coverage + outputs_coverage + config_fields_coverage) / 3
        
        return {
            "inputs_coverage": inputs_coverage,
            "outputs_coverage": outputs_coverage,
            "config_fields_coverage": config_fields_coverage,
            "overall_coverage": overall_coverage
        }
        
    def _determine_production_readiness(self, quality_result: Dict[str, Any],
                                       test_results: Dict[str, Dict[str, Any]],
                                       test_coverage: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Determine if the plugin is ready for production.
        
        Args:
            quality_result: Quality check results
            test_results: Test results
            test_coverage: Test coverage
            
        Returns:
            Tuple of (is_ready, reasons)
        """
        reasons = []
        
        # Check quality
        quality_score = quality_result["quality_score"]
        if quality_score < 0.8:
            reasons.append(f"Quality score is too low: {quality_score:.2f} (minimum 0.8)")
            
        # Check for critical issues
        for check_type in ["structure_check", "metadata_check", "implementation_check"]:
            if check_type in quality_result:
                check = quality_result[check_type]
                for issue in check.get("issues", []):
                    if issue["type"] == "error":
                        reasons.append(f"Critical issue: {issue['message']}")
                        
        # Check test results
        if not test_results:
            reasons.append("No tests have been run")
        else:
            for test_name, result in test_results.items():
                if result["failed_tests"] > 0 or result["error_tests"] > 0:
                    reasons.append(f"Test {test_name} has {result['failed_tests']} failed tests and {result['error_tests']} errors")
                    
        # Check test coverage
        overall_coverage = test_coverage["overall_coverage"]
        if overall_coverage < 0.7:
            reasons.append(f"Test coverage is too low: {overall_coverage:.2f} (minimum 0.7)")
            
        # Determine if the plugin is ready for production
        is_ready = len(reasons) == 0
        
        return is_ready, reasons
        
    def generate_report(self, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a production readiness report.
        
        Args:
            output_dir: Directory to store the report (optional)
            
        Returns:
            Dictionary containing the report
        """
        # Validate the plugin
        result = self.validate()
        
        # Save the report
        if output_dir:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            plugin_name = self.plugin_class.__name__
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{plugin_name}_production_report_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "w") as f:
                json.dump(result, f, indent=4)
                
            logger.info(f"Saved production readiness report to {filepath}")
            
        return result
