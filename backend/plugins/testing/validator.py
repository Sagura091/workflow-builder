"""
Plugin Validator

This module provides a validator for checking if a plugin meets the backend's requirements.
"""

import os
import sys
import importlib.util
import inspect
import json
import logging
from typing import Dict, Any, Type, Optional, List, Tuple, Union
from datetime import datetime

logger = logging.getLogger("workflow_builder")

class PluginValidator:
    """
    Validator for checking if a plugin meets the backend's requirements.
    
    This class provides methods for validating plugins against the backend's requirements.
    """
    
    def __init__(self, plugin_class: Type):
        """
        Initialize the validator.
        
        Args:
            plugin_class: The plugin class to validate
        """
        self.plugin_class = plugin_class
        
    def validate(self) -> Dict[str, Any]:
        """
        Validate the plugin against the backend's requirements.
        
        Returns:
            Dictionary containing the validation results
        """
        # Run all validation checks
        structure_check = self._check_structure()
        metadata_check = self._check_metadata()
        implementation_check = self._check_implementation()
        compatibility_check = self._check_compatibility()
        
        # Determine if the plugin is valid
        is_valid = (
            structure_check["valid"] and
            metadata_check["valid"] and
            implementation_check["valid"] and
            compatibility_check["valid"]
        )
        
        # Create result
        return {
            "plugin": self.plugin_class.__name__,
            "valid": is_valid,
            "structure": structure_check,
            "metadata": metadata_check,
            "implementation": implementation_check,
            "compatibility": compatibility_check,
            "timestamp": datetime.now().isoformat()
        }
        
    def _check_structure(self) -> Dict[str, Any]:
        """
        Check the structure of the plugin.
        
        Returns:
            Dictionary containing the structure check results
        """
        issues = []
        
        # Check if the plugin has the required attributes
        if not hasattr(self.plugin_class, "__plugin_meta__"):
            issues.append("Plugin does not have __plugin_meta__ attribute")
            
        # Check if the plugin has the required methods
        if not hasattr(self.plugin_class, "execute"):
            issues.append("Plugin does not have execute method")
            
        # Determine if the structure is valid
        is_valid = len(issues) == 0
        
        return {
            "valid": is_valid,
            "issues": issues
        }
        
    def _check_metadata(self) -> Dict[str, Any]:
        """
        Check the metadata of the plugin.
        
        Returns:
            Dictionary containing the metadata check results
        """
        issues = []
        
        # Check if the plugin has metadata
        if not hasattr(self.plugin_class, "__plugin_meta__"):
            issues.append("Plugin does not have __plugin_meta__ attribute")
            return {
                "valid": False,
                "issues": issues
            }
            
        # Get metadata
        meta = self.plugin_class.__plugin_meta__
        
        # Check required metadata fields
        required_fields = ["id", "name", "version", "description", "category", "tags"]
        for field in required_fields:
            if not hasattr(meta, field) or not getattr(meta, field):
                issues.append(f"Plugin metadata does not have {field}")
                
        # Check inputs and outputs
        if not hasattr(meta, "inputs") or not meta.inputs:
            issues.append("Plugin metadata does not have inputs")
            
        if not hasattr(meta, "outputs") or not meta.outputs:
            issues.append("Plugin metadata does not have outputs")
            
        # Determine if the metadata is valid
        is_valid = len(issues) == 0
        
        return {
            "valid": is_valid,
            "issues": issues
        }
        
    def _check_implementation(self) -> Dict[str, Any]:
        """
        Check the implementation of the plugin.
        
        Returns:
            Dictionary containing the implementation check results
        """
        issues = []
        
        # Check if the plugin has an execute method
        if not hasattr(self.plugin_class, "execute"):
            issues.append("Plugin does not have execute method")
            return {
                "valid": False,
                "issues": issues
            }
            
        # Check execute method signature
        execute_method = getattr(self.plugin_class, "execute")
        if not callable(execute_method):
            issues.append("execute is not a method")
        else:
            # Check method signature
            sig = inspect.signature(execute_method)
            params = sig.parameters
            
            # Check number of parameters
            if len(params) < 3:  # self, inputs, config
                issues.append(f"execute method has {len(params)} parameters, expected at least 3")
                
            # Check parameter names
            param_names = list(params.keys())
            if len(param_names) >= 3 and param_names[1] != "inputs":
                issues.append(f"Second parameter of execute method is named '{param_names[1]}', expected 'inputs'")
                
            if len(param_names) >= 3 and param_names[2] != "config":
                issues.append(f"Third parameter of execute method is named '{param_names[2]}', expected 'config'")
                
        # Check validation methods
        if not hasattr(self.plugin_class, "validate_inputs"):
            issues.append("Plugin does not have validate_inputs method")
            
        if not hasattr(self.plugin_class, "validate_config"):
            issues.append("Plugin does not have validate_config method")
            
        # Determine if the implementation is valid
        is_valid = len(issues) == 0
        
        return {
            "valid": is_valid,
            "issues": issues
        }
        
    def _check_compatibility(self) -> Dict[str, Any]:
        """
        Check the compatibility of the plugin with the backend.
        
        Returns:
            Dictionary containing the compatibility check results
        """
        issues = []
        
        # Check if the plugin is compatible with the backend
        # This is a placeholder for more specific compatibility checks
        
        # Determine if the plugin is compatible
        is_valid = len(issues) == 0
        
        return {
            "valid": is_valid,
            "issues": issues
        }
        
    @staticmethod
    def validate_plugin_file(plugin_path: str) -> Dict[str, Any]:
        """
        Validate a plugin file.
        
        Args:
            plugin_path: Path to the plugin file
            
        Returns:
            Dictionary containing the validation results
        """
        try:
            # Import the plugin module
            spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
            if spec is None:
                return {
                    "valid": False,
                    "issues": [f"Could not import module from {plugin_path}"]
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
                    "valid": False,
                    "issues": [f"Could not find plugin class in {plugin_path}"]
                }
                
            # Validate the plugin
            validator = PluginValidator(plugin_class)
            return validator.validate()
            
        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Error validating plugin: {str(e)}"]
            }
