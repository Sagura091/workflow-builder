"""
Plugin Quality Checker

This module provides a quality checker for plugins.
"""

import inspect
import logging
import re
from typing import Dict, Any, Type, Optional, List, Tuple, Union

from backend.app.models.plugin_interface import PluginInterface
from backend.plugins.standalone_plugin_base import StandalonePluginBase

logger = logging.getLogger("workflow_builder")

class PluginQualityChecker:
    """
    Quality checker for plugins.
    
    This class provides methods for checking the quality of plugins.
    """
    
    def __init__(self, plugin_class: Type[PluginInterface]):
        """
        Initialize the quality checker.
        
        Args:
            plugin_class: The plugin class to check
        """
        self.plugin_class = plugin_class
        
    def check_quality(self) -> Dict[str, Any]:
        """
        Check the quality of the plugin.
        
        Returns:
            Dictionary containing the quality check results
        """
        # Run all checks
        structure_check = self.check_structure()
        metadata_check = self.check_metadata()
        implementation_check = self.check_implementation()
        documentation_check = self.check_documentation()
        
        # Calculate overall quality score
        total_checks = (
            structure_check["total_checks"] +
            metadata_check["total_checks"] +
            implementation_check["total_checks"] +
            documentation_check["total_checks"]
        )
        
        passed_checks = (
            structure_check["passed_checks"] +
            metadata_check["passed_checks"] +
            implementation_check["passed_checks"] +
            documentation_check["passed_checks"]
        )
        
        quality_score = (passed_checks / total_checks) if total_checks > 0 else 0
        
        # Determine quality level
        quality_level = "unknown"
        if quality_score >= 0.9:
            quality_level = "excellent"
        elif quality_score >= 0.8:
            quality_level = "good"
        elif quality_score >= 0.7:
            quality_level = "acceptable"
        elif quality_score >= 0.6:
            quality_level = "needs improvement"
        else:
            quality_level = "poor"
            
        # Create result
        return {
            "plugin": self.plugin_class.__name__,
            "quality_score": quality_score,
            "quality_level": quality_level,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "structure_check": structure_check,
            "metadata_check": metadata_check,
            "implementation_check": implementation_check,
            "documentation_check": documentation_check
        }
        
    def check_structure(self) -> Dict[str, Any]:
        """
        Check the structure of the plugin.
        
        Returns:
            Dictionary containing the structure check results
        """
        issues = []
        
        # Check if the plugin inherits from PluginInterface
        if not issubclass(self.plugin_class, PluginInterface):
            issues.append({
                "type": "error",
                "message": f"Plugin {self.plugin_class.__name__} does not inherit from PluginInterface"
            })
            
        # Check if the plugin has the required attributes
        if not hasattr(self.plugin_class, "__plugin_meta__"):
            issues.append({
                "type": "error",
                "message": f"Plugin {self.plugin_class.__name__} does not have __plugin_meta__ attribute"
            })
            
        # Check if the plugin has the required methods
        if not hasattr(self.plugin_class, "execute"):
            issues.append({
                "type": "error",
                "message": f"Plugin {self.plugin_class.__name__} does not have execute method"
            })
            
        # Check if the plugin has validation methods
        if not hasattr(self.plugin_class, "validate_inputs"):
            issues.append({
                "type": "warning",
                "message": f"Plugin {self.plugin_class.__name__} does not have validate_inputs method"
            })
            
        if not hasattr(self.plugin_class, "validate_config"):
            issues.append({
                "type": "warning",
                "message": f"Plugin {self.plugin_class.__name__} does not have validate_config method"
            })
            
        # If it's a standalone plugin, check additional requirements
        if issubclass(self.plugin_class, StandalonePluginBase):
            if not hasattr(self.plugin_class, "__standalone_capable__"):
                issues.append({
                    "type": "warning",
                    "message": f"Standalone plugin {self.plugin_class.__name__} does not have __standalone_capable__ attribute"
                })
                
        # Calculate results
        total_checks = 6
        passed_checks = total_checks - len(issues)
        
        return {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "issues": issues
        }
        
    def check_metadata(self) -> Dict[str, Any]:
        """
        Check the metadata of the plugin.
        
        Returns:
            Dictionary containing the metadata check results
        """
        issues = []
        
        # Check if the plugin has metadata
        if not hasattr(self.plugin_class, "__plugin_meta__"):
            issues.append({
                "type": "error",
                "message": f"Plugin {self.plugin_class.__name__} does not have __plugin_meta__ attribute"
            })
            return {
                "total_checks": 1,
                "passed_checks": 0,
                "issues": issues
            }
            
        # Get metadata
        meta = self.plugin_class.__plugin_meta__
        
        # Check required metadata fields
        if not hasattr(meta, "id") or not meta.id:
            issues.append({
                "type": "error",
                "message": "Plugin metadata does not have id"
            })
            
        if not hasattr(meta, "name") or not meta.name:
            issues.append({
                "type": "error",
                "message": "Plugin metadata does not have name"
            })
            
        if not hasattr(meta, "version") or not meta.version:
            issues.append({
                "type": "error",
                "message": "Plugin metadata does not have version"
            })
            
        if not hasattr(meta, "description") or not meta.description:
            issues.append({
                "type": "warning",
                "message": "Plugin metadata does not have description"
            })
            
        if not hasattr(meta, "category") or not meta.category:
            issues.append({
                "type": "warning",
                "message": "Plugin metadata does not have category"
            })
            
        if not hasattr(meta, "tags") or not meta.tags:
            issues.append({
                "type": "warning",
                "message": "Plugin metadata does not have tags"
            })
            
        # Check inputs and outputs
        if not hasattr(meta, "inputs") or not meta.inputs:
            issues.append({
                "type": "warning",
                "message": "Plugin metadata does not have inputs"
            })
        else:
            # Check each input
            for i, input_def in enumerate(meta.inputs):
                if not hasattr(input_def, "id") or not input_def.id:
                    issues.append({
                        "type": "error",
                        "message": f"Input {i} does not have id"
                    })
                    
                if not hasattr(input_def, "name") or not input_def.name:
                    issues.append({
                        "type": "warning",
                        "message": f"Input {input_def.id} does not have name"
                    })
                    
                if not hasattr(input_def, "type") or not input_def.type:
                    issues.append({
                        "type": "error",
                        "message": f"Input {input_def.id} does not have type"
                    })
                    
                if not hasattr(input_def, "description") or not input_def.description:
                    issues.append({
                        "type": "warning",
                        "message": f"Input {input_def.id} does not have description"
                    })
            
        if not hasattr(meta, "outputs") or not meta.outputs:
            issues.append({
                "type": "warning",
                "message": "Plugin metadata does not have outputs"
            })
        else:
            # Check each output
            for i, output_def in enumerate(meta.outputs):
                if not hasattr(output_def, "id") or not output_def.id:
                    issues.append({
                        "type": "error",
                        "message": f"Output {i} does not have id"
                    })
                    
                if not hasattr(output_def, "name") or not output_def.name:
                    issues.append({
                        "type": "warning",
                        "message": f"Output {output_def.id} does not have name"
                    })
                    
                if not hasattr(output_def, "type") or not output_def.type:
                    issues.append({
                        "type": "error",
                        "message": f"Output {output_def.id} does not have type"
                    })
                    
                if not hasattr(output_def, "description") or not output_def.description:
                    issues.append({
                        "type": "warning",
                        "message": f"Output {output_def.id} does not have description"
                    })
            
        # Check config fields
        if not hasattr(meta, "config_fields") or not meta.config_fields:
            issues.append({
                "type": "warning",
                "message": "Plugin metadata does not have config_fields"
            })
        else:
            # Check each config field
            for i, config_field in enumerate(meta.config_fields):
                if not hasattr(config_field, "id") or not config_field.id:
                    issues.append({
                        "type": "error",
                        "message": f"Config field {i} does not have id"
                    })
                    
                if not hasattr(config_field, "name") or not config_field.name:
                    issues.append({
                        "type": "warning",
                        "message": f"Config field {config_field.id} does not have name"
                    })
                    
                if not hasattr(config_field, "type") or not config_field.type:
                    issues.append({
                        "type": "error",
                        "message": f"Config field {config_field.id} does not have type"
                    })
                    
                if not hasattr(config_field, "description") or not config_field.description:
                    issues.append({
                        "type": "warning",
                        "message": f"Config field {config_field.id} does not have description"
                    })
        
        # Calculate results
        total_checks = 9  # Base checks
        
        # Add checks for each input, output, and config field
        if hasattr(meta, "inputs"):
            total_checks += len(meta.inputs) * 4
            
        if hasattr(meta, "outputs"):
            total_checks += len(meta.outputs) * 4
            
        if hasattr(meta, "config_fields"):
            total_checks += len(meta.config_fields) * 4
            
        passed_checks = total_checks - len(issues)
        
        return {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "issues": issues
        }
        
    def check_implementation(self) -> Dict[str, Any]:
        """
        Check the implementation of the plugin.
        
        Returns:
            Dictionary containing the implementation check results
        """
        issues = []
        
        # Check if the plugin has an execute method
        if not hasattr(self.plugin_class, "execute"):
            issues.append({
                "type": "error",
                "message": f"Plugin {self.plugin_class.__name__} does not have execute method"
            })
            return {
                "total_checks": 1,
                "passed_checks": 0,
                "issues": issues
            }
            
        # Check execute method signature
        execute_method = getattr(self.plugin_class, "execute")
        if not callable(execute_method):
            issues.append({
                "type": "error",
                "message": "execute is not a method"
            })
        else:
            # Check method signature
            sig = inspect.signature(execute_method)
            params = sig.parameters
            
            # Check number of parameters
            if len(params) < 3:  # self, inputs, config
                issues.append({
                    "type": "error",
                    "message": f"execute method has {len(params)} parameters, expected at least 3"
                })
                
            # Check parameter names
            param_names = list(params.keys())
            if len(param_names) >= 3 and param_names[1] != "inputs":
                issues.append({
                    "type": "warning",
                    "message": f"Second parameter of execute method is named '{param_names[1]}', expected 'inputs'"
                })
                
            if len(param_names) >= 3 and param_names[2] != "config":
                issues.append({
                    "type": "warning",
                    "message": f"Third parameter of execute method is named '{param_names[2]}', expected 'config'"
                })
                
        # Check validation methods
        if hasattr(self.plugin_class, "validate_inputs"):
            validate_inputs_method = getattr(self.plugin_class, "validate_inputs")
            if not callable(validate_inputs_method):
                issues.append({
                    "type": "error",
                    "message": "validate_inputs is not a method"
                })
            else:
                # Check method signature
                sig = inspect.signature(validate_inputs_method)
                params = sig.parameters
                
                # Check number of parameters
                if len(params) < 2:  # self, inputs
                    issues.append({
                        "type": "error",
                        "message": f"validate_inputs method has {len(params)} parameters, expected at least 2"
                    })
                    
                # Check parameter names
                param_names = list(params.keys())
                if len(param_names) >= 2 and param_names[1] != "inputs":
                    issues.append({
                        "type": "warning",
                        "message": f"Second parameter of validate_inputs method is named '{param_names[1]}', expected 'inputs'"
                    })
        else:
            issues.append({
                "type": "warning",
                "message": f"Plugin {self.plugin_class.__name__} does not have validate_inputs method"
            })
            
        if hasattr(self.plugin_class, "validate_config"):
            validate_config_method = getattr(self.plugin_class, "validate_config")
            if not callable(validate_config_method):
                issues.append({
                    "type": "error",
                    "message": "validate_config is not a method"
                })
            else:
                # Check method signature
                sig = inspect.signature(validate_config_method)
                params = sig.parameters
                
                # Check number of parameters
                if len(params) < 2:  # self, config
                    issues.append({
                        "type": "error",
                        "message": f"validate_config method has {len(params)} parameters, expected at least 2"
                    })
                    
                # Check parameter names
                param_names = list(params.keys())
                if len(param_names) >= 2 and param_names[1] != "config":
                    issues.append({
                        "type": "warning",
                        "message": f"Second parameter of validate_config method is named '{param_names[1]}', expected 'config'"
                    })
        else:
            issues.append({
                "type": "warning",
                "message": f"Plugin {self.plugin_class.__name__} does not have validate_config method"
            })
            
        # Calculate results
        total_checks = 7  # Base checks
        passed_checks = total_checks - len(issues)
        
        return {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "issues": issues
        }
        
    def check_documentation(self) -> Dict[str, Any]:
        """
        Check the documentation of the plugin.
        
        Returns:
            Dictionary containing the documentation check results
        """
        issues = []
        
        # Check class docstring
        if not self.plugin_class.__doc__:
            issues.append({
                "type": "warning",
                "message": f"Plugin {self.plugin_class.__name__} does not have a docstring"
            })
        elif len(self.plugin_class.__doc__.strip()) < 10:
            issues.append({
                "type": "warning",
                "message": f"Plugin {self.plugin_class.__name__} has a very short docstring"
            })
            
        # Check execute method docstring
        if hasattr(self.plugin_class, "execute"):
            execute_method = getattr(self.plugin_class, "execute")
            if not execute_method.__doc__:
                issues.append({
                    "type": "warning",
                    "message": "execute method does not have a docstring"
                })
            elif len(execute_method.__doc__.strip()) < 10:
                issues.append({
                    "type": "warning",
                    "message": "execute method has a very short docstring"
                })
                
        # Check validate_inputs method docstring
        if hasattr(self.plugin_class, "validate_inputs"):
            validate_inputs_method = getattr(self.plugin_class, "validate_inputs")
            if not validate_inputs_method.__doc__:
                issues.append({
                    "type": "warning",
                    "message": "validate_inputs method does not have a docstring"
                })
            elif len(validate_inputs_method.__doc__.strip()) < 10:
                issues.append({
                    "type": "warning",
                    "message": "validate_inputs method has a very short docstring"
                })
                
        # Check validate_config method docstring
        if hasattr(self.plugin_class, "validate_config"):
            validate_config_method = getattr(self.plugin_class, "validate_config")
            if not validate_config_method.__doc__:
                issues.append({
                    "type": "warning",
                    "message": "validate_config method does not have a docstring"
                })
            elif len(validate_config_method.__doc__.strip()) < 10:
                issues.append({
                    "type": "warning",
                    "message": "validate_config method has a very short docstring"
                })
                
        # Calculate results
        total_checks = 4  # Base checks
        passed_checks = total_checks - len(issues)
        
        return {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "issues": issues
        }
