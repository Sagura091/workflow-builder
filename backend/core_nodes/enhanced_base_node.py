"""
Enhanced Base Node

This module provides an enhanced base class for all core nodes with improved
functionality, error handling, and lifecycle management.
"""

import time
import logging
import inspect
import traceback
from typing import Dict, Any, Optional, List, Set, ClassVar, Type
from enum import Enum
from datetime import datetime

from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

# Configure logger
logger = logging.getLogger("workflow_builder")


class NodeLifecycleState(str, Enum):
    """Node lifecycle states."""
    UNINITIALIZED = "uninitialized"
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    DISABLED = "disabled"


class NodeExecutionResult:
    """Result of a node execution."""
    
    def __init__(
        self,
        outputs: Dict[str, Any],
        success: bool = True,
        error_message: Optional[str] = None,
        execution_time_ms: float = 0.0,
        state: NodeLifecycleState = NodeLifecycleState.COMPLETED
    ):
        """Initialize the execution result."""
        self.outputs = outputs
        self.success = success
        self.error_message = error_message
        self.execution_time_ms = execution_time_ms
        self.state = state
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "outputs": self.outputs,
            "success": self.success,
            "error_message": self.error_message,
            "execution_time_ms": self.execution_time_ms,
            "state": self.state,
            "timestamp": self.timestamp.isoformat()
        }


class EnhancedBaseNode:
    """
    Enhanced base class for all core nodes.
    
    This class provides improved functionality, error handling, and lifecycle management
    for core nodes in the workflow builder.
    """
    
    # Class variables
    __node_id__: ClassVar[str] = ""
    __node_version__: ClassVar[str] = "1.0.0"
    __node_category__: ClassVar[str] = NodeCategory.CUSTOM
    __node_description__: ClassVar[str] = ""
    
    def __init__(self):
        """Initialize the node."""
        # Node identity
        self.id = self.__class__.__node_id__ or self.__class__.__name__.lower()
        self.name = self.__class__.__name__
        self.category = self.__class__.__node_category__
        self.description = self.__class__.__node_description__ or self.__class__.__doc__ or ""
        
        # Node state
        self._state = NodeLifecycleState.UNINITIALIZED
        self._error = None
        self._created_at = datetime.now()
        self._last_executed = None
        
        # Performance metrics
        self._execution_count = 0
        self._average_execution_time_ms = 0.0
        self._error_count = 0
        
        # Cache for metadata
        self._metadata_cache = None
        
        # Initialize the node
        self.initialize()
    
    def initialize(self) -> bool:
        """
        Initialize the node.
        
        This method is called when the node is first created.
        Override this method to perform any initialization tasks.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        self._state = NodeLifecycleState.INITIALIZED
        return True
    
    def cleanup(self) -> bool:
        """
        Clean up the node.
        
        This method is called when the node is being destroyed.
        Override this method to perform any cleanup tasks.
        
        Returns:
            True if cleanup was successful, False otherwise
        """
        return True
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node.
        
        This method should be overridden by subclasses.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The output values
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def safe_execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> NodeExecutionResult:
        """
        Safely execute the node with error handling and performance tracking.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The execution result
        """
        start_time = time.time()
        
        try:
            # Update state
            self._state = NodeLifecycleState.RUNNING
            self._last_executed = datetime.now()
            
            # Validate inputs and config
            validated_inputs = self.validate_inputs(inputs)
            validated_config = self.validate_config(config)
            
            # Execute the node
            outputs = self.execute(validated_config, validated_inputs)
            
            # Update state
            self._state = NodeLifecycleState.COMPLETED
            
            # Update statistics
            execution_time_ms = (time.time() - start_time) * 1000
            self._update_statistics(execution_time_ms)
            
            return NodeExecutionResult(
                outputs=outputs,
                success=True,
                execution_time_ms=execution_time_ms,
                state=NodeLifecycleState.COMPLETED
            )
        
        except Exception as e:
            # Update state
            self._state = NodeLifecycleState.ERROR
            self._error = str(e)
            
            # Update statistics
            execution_time_ms = (time.time() - start_time) * 1000
            self._update_statistics(execution_time_ms, error=True)
            
            # Log the error
            logger.error(f"Error executing node {self.id}: {str(e)}")
            logger.debug(traceback.format_exc())
            
            return NodeExecutionResult(
                outputs={},
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time_ms,
                state=NodeLifecycleState.ERROR
            )
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the node configuration.
        
        Override this method to perform custom validation.
        
        Args:
            config: The node configuration
            
        Returns:
            The validated and normalized configuration
            
        Raises:
            ValueError: If the configuration is invalid
        """
        return config
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the node inputs.
        
        Override this method to perform custom validation.
        
        Args:
            inputs: The input values
            
        Returns:
            The validated and normalized inputs
            
        Raises:
            ValueError: If the inputs are invalid
        """
        return inputs
    
    def get_metadata(self) -> PluginMetadata:
        """
        Get the node metadata.
        
        Override this method to provide custom metadata.
        
        Returns:
            The node metadata
        """
        # Return cached metadata if available
        if self._metadata_cache:
            return self._metadata_cache
        
        # Create metadata from class attributes
        metadata = self._create_metadata_from_attributes()
        
        # Cache the metadata
        self._metadata_cache = metadata
        
        return metadata
    
    def _create_metadata_from_attributes(self) -> PluginMetadata:
        """
        Create metadata from class attributes.
        
        Returns:
            The node metadata
        """
        # Get inputs and outputs from method signature
        inputs = []
        outputs = []
        
        # Get execute method signature
        sig = inspect.signature(self.execute)
        
        # Check for inputs parameter
        if "inputs" in sig.parameters:
            # Try to get input annotations from docstring
            doc = inspect.getdoc(self.execute) or ""
            input_types = self._parse_docstring_params(doc, "inputs")
            
            # Add a generic input if no specific inputs found
            if not input_types:
                inputs.append(PortDefinition(
                    id="input",
                    name="Input",
                    type="any",
                    description="Node input",
                    required=True
                ))
            else:
                # Add specific inputs
                for name, type_info in input_types.items():
                    inputs.append(PortDefinition(
                        id=name,
                        name=name.replace("_", " ").title(),
                        type=type_info.get("type", "any"),
                        description=type_info.get("description", ""),
                        required=type_info.get("required", True)
                    ))
        
        # Try to get output annotations from docstring
        doc = inspect.getdoc(self.execute) or ""
        output_types = self._parse_docstring_params(doc, "returns")
        
        # Add a generic output if no specific outputs found
        if not output_types:
            outputs.append(PortDefinition(
                id="output",
                name="Output",
                type="any",
                description="Node output",
                required=True
            ))
        else:
            # Add specific outputs
            for name, type_info in output_types.items():
                outputs.append(PortDefinition(
                    id=name,
                    name=name.replace("_", " ").title(),
                    type=type_info.get("type", "any"),
                    description=type_info.get("description", ""),
                    required=type_info.get("required", True)
                ))
        
        # Create metadata
        return PluginMetadata(
            id=self.id,
            name=self.name,
            version=self.__class__.__node_version__,
            description=self.description,
            author="Workflow Builder",
            category=self.category,
            tags=[],
            inputs=inputs,
            outputs=outputs,
            config_fields=[],
            ui_properties={}
        )
    
    def _parse_docstring_params(self, docstring: str, section: str) -> Dict[str, Dict[str, Any]]:
        """
        Parse parameters from a docstring.
        
        Args:
            docstring: The docstring to parse
            section: The section to parse (e.g., "Args", "Returns")
            
        Returns:
            Dictionary of parameter names and types
        """
        params = {}
        
        # Find the section
        section_start = docstring.find(f"{section}:")
        if section_start == -1:
            return params
        
        # Find the end of the section
        section_end = docstring.find("\n\n", section_start)
        if section_end == -1:
            section_end = len(docstring)
        
        # Extract the section
        section_text = docstring[section_start:section_end]
        
        # Parse parameters
        lines = section_text.split("\n")[1:]  # Skip the section header
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse parameter name and description
            parts = line.split(":", 1)
            if len(parts) < 2:
                continue
            
            param_name = parts[0].strip()
            param_desc = parts[1].strip()
            
            # Extract type information
            type_info = {}
            type_info["description"] = param_desc
            
            # Try to extract type from description
            type_match = param_desc.lower()
            if "string" in type_match or "str" in type_match:
                type_info["type"] = "string"
            elif "number" in type_match or "int" in type_match or "float" in type_match:
                type_info["type"] = "number"
            elif "boolean" in type_match or "bool" in type_match:
                type_info["type"] = "boolean"
            elif "object" in type_match or "dict" in type_match:
                type_info["type"] = "object"
            elif "array" in type_match or "list" in type_match:
                type_info["type"] = "array"
            else:
                type_info["type"] = "any"
            
            # Check if required
            type_info["required"] = "required" in param_desc.lower() and "not required" not in param_desc.lower()
            
            params[param_name] = type_info
        
        return params
    
    def _update_statistics(self, execution_time_ms: float, error: bool = False) -> None:
        """
        Update execution statistics.
        
        Args:
            execution_time_ms: The execution time in milliseconds
            error: Whether an error occurred
        """
        self._execution_count += 1
        
        # Update average execution time using weighted average
        if self._execution_count > 1:
            self._average_execution_time_ms = (
                (self._average_execution_time_ms * (self._execution_count - 1) + execution_time_ms) / 
                self._execution_count
            )
        else:
            self._average_execution_time_ms = execution_time_ms
        
        # Update error count
        if error:
            self._error_count += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            "execution_count": self._execution_count,
            "average_execution_time_ms": self._average_execution_time_ms,
            "error_count": self._error_count,
            "created_at": self._created_at.isoformat(),
            "last_executed": self._last_executed.isoformat() if self._last_executed else None,
            "state": self._state
        }
    
    def get_state(self) -> NodeLifecycleState:
        """
        Get the current state of the node.
        
        Returns:
            The current state
        """
        return self._state
    
    def get_error(self) -> Optional[str]:
        """
        Get the last error message.
        
        Returns:
            The last error message, or None if no error
        """
        return self._error
    
    def reset(self) -> None:
        """Reset the node to its initial state."""
        self._state = NodeLifecycleState.INITIALIZED
        self._error = None
    
    def disable(self) -> None:
        """Disable the node."""
        self._state = NodeLifecycleState.DISABLED
    
    def enable(self) -> None:
        """Enable the node."""
        self._state = NodeLifecycleState.INITIALIZED
