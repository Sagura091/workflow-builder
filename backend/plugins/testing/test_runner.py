"""
Plugin Test Runner

This module provides a test runner for executing plugin tests.
"""

import time
import logging
import json
import os
from typing import Dict, Any, Type, Optional, List, Tuple, Union
from datetime import datetime

from backend.app.models.plugin_interface import PluginInterface
from backend.plugins.testing.plugin_test_case import PluginTestCase

logger = logging.getLogger("workflow_builder")

class PluginTestRunner:
    """
    Test runner for executing plugin tests.
    
    This class provides methods for running plugin tests and generating reports.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the test runner.
        
        Args:
            output_dir: Directory to store test reports (optional)
        """
        self.output_dir = output_dir
        self.test_results = []
        
        # Create output directory if it doesn't exist
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def run_test_case(self, test_case: PluginTestCase) -> Dict[str, Any]:
        """
        Run a test case.
        
        Args:
            test_case: The test case to run
            
        Returns:
            Dictionary containing the test results
        """
        start_time = time.time()
        
        # Run all tests in the test case
        result = test_case.run_all_tests()
        
        # Add execution time
        execution_time_ms = (time.time() - start_time) * 1000
        result["execution_time_ms"] = execution_time_ms
        
        # Add timestamp
        result["timestamp"] = datetime.now().isoformat()
        
        # Add to test results
        self.test_results.append(result)
        
        # Save report
        if self.output_dir:
            self._save_report(result)
            
        return result
        
    def run_test_cases(self, test_cases: List[PluginTestCase]) -> Dict[str, Any]:
        """
        Run multiple test cases.
        
        Args:
            test_cases: The test cases to run
            
        Returns:
            Dictionary containing the test results
        """
        start_time = time.time()
        
        # Run each test case
        for test_case in test_cases:
            self.run_test_case(test_case)
            
        # Calculate summary
        total_tests = sum(result["total_tests"] for result in self.test_results)
        passed_tests = sum(result["passed_tests"] for result in self.test_results)
        failed_tests = sum(result["failed_tests"] for result in self.test_results)
        error_tests = sum(result["error_tests"] for result in self.test_results)
        
        # Create summary
        summary = {
            "total_test_cases": len(self.test_results),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": (passed_tests / total_tests) if total_tests > 0 else 0,
            "execution_time_ms": (time.time() - start_time) * 1000,
            "timestamp": datetime.now().isoformat(),
            "test_results": self.test_results
        }
        
        # Save summary report
        if self.output_dir:
            self._save_summary_report(summary)
            
        return summary
        
    def _save_report(self, result: Dict[str, Any]) -> None:
        """
        Save a test report to a file.
        
        Args:
            result: The test result to save
        """
        plugin_name = result["plugin"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{plugin_name}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(result, f, indent=4)
            
        logger.info(f"Saved test report to {filepath}")
        
    def _save_summary_report(self, summary: Dict[str, Any]) -> None:
        """
        Save a summary report to a file.
        
        Args:
            summary: The summary to save
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(summary, f, indent=4)
            
        logger.info(f"Saved summary report to {filepath}")
        
    def get_test_results(self) -> List[Dict[str, Any]]:
        """
        Get the test results.
        
        Returns:
            List of test results
        """
        return self.test_results
        
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the test results.
        
        Returns:
            Dictionary containing the summary
        """
        # Calculate summary
        total_tests = sum(result["total_tests"] for result in self.test_results)
        passed_tests = sum(result["passed_tests"] for result in self.test_results)
        failed_tests = sum(result["failed_tests"] for result in self.test_results)
        error_tests = sum(result["error_tests"] for result in self.test_results)
        
        # Create summary
        return {
            "total_test_cases": len(self.test_results),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": (passed_tests / total_tests) if total_tests > 0 else 0
        }
        
    def clear_results(self) -> None:
        """Clear the test results."""
        self.test_results = []
