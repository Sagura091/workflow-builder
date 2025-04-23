"""
Plugin Interface

This module defines the interface for plugins in the workflow builder.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, ClassVar
from datetime import datetime
from enum import Enum

from backend.app.models.plugin_metadata import PluginMetadata


class PluginLifecycleState(str, Enum):
    """Plugin lifecycle states."""
    UNLOADED = "unloaded"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"


class PluginInterface(ABC):
    """Interface for workflow builder plugins.
    
    All plugins should implement this interface to ensure compatibility
    with the workflow builder.
    """
    
    # Class variables
    __plugin_meta__: ClassVar[PluginMetadata]
    __plugin_version__: ClassVar[str] = "1.0.0"
    __plugin_dependencies__: ClassVar[List[str]] = []
    __plugin_author__: ClassVar[str] = "Unknown"
    __plugin_license__: ClassVar[str] = "MIT"
    
    def __init__(self):
        """Initialize the plugin."""
        self._state = PluginLifecycleState.UNLOADED
        self._error = None
        self._created_at = datetime.now()
        self._last_executed = None
        self._execution_count = 0
        self._average_execution_time_ms = 0.0
        self._error_count = 0
        
    @abstractmethod
    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plugin.
        
        Args:
            inputs: Dictionary of input values
            config: Dictionary of configuration values
            
        Returns:
            Dictionary of output values
        """
        pass
    
    def generate_code(self, config: Dict[str, Any]) -> str:
        """Generate code for the plugin.
        
        Args:
            config: Dictionary of configuration values
            
        Returns:
            Generated code as a string
        """
        return ""
    
    def initialize(self) -> bool:
        """Initialize the plugin.
        
        This method is called when the plugin is first loaded.
        Use it to set up any resources needed by the plugin.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        self._state = PluginLifecycleState.INITIALIZED
        return True
    
    def cleanup(self) -> bool:
        """Clean up the plugin.
        
        This method is called when the plugin is unloaded.
        Use it to clean up any resources used by the plugin.
        
        Returns:
            True if cleanup was successful, False otherwise
        """
        return True
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize plugin configuration.
        
        Args:
            config: Dictionary of configuration values
            
        Returns:
            Validated and normalized configuration
        """
        return config
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize plugin inputs.
        
        Args:
            inputs: Dictionary of input values
            
        Returns:
            Validated and normalized inputs
        """
        return inputs
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata.
        
        Returns:
            Plugin metadata
        """
        if hasattr(self.__class__, "__plugin_meta__"):
            return self.__class__.__plugin_meta__
        
        # Create basic metadata
        return PluginMetadata(
            id=self.__class__.__name__,
            name=self.__class__.__name__.replace('_', ' ').title(),
            version=self.__class__.__plugin_version__,
            description=self.__class__.__doc__ or "",
            author=self.__class__.__plugin_author__,
            category="custom",
            inputs=[],
            outputs=[],
            config_fields=[]
        )
    
    def get_state(self) -> PluginLifecycleState:
        """Get the current state of the plugin.
        
        Returns:
            Current plugin state
        """
        return self._state
    
    def get_error(self) -> Optional[str]:
        """Get the last error that occurred in the plugin.
        
        Returns:
            Error message or None if no error
        """
        return self._error
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get plugin execution statistics.
        
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
    
    def update_statistics(self, execution_time_ms: float, error: bool = False) -> None:
        """Update plugin execution statistics.
        
        Args:
            execution_time_ms: Execution time in milliseconds
            error: Whether an error occurred during execution
        """
        self._execution_count += 1
        self._last_executed = datetime.now()
        
        # Update average execution time using weighted average
        if self._execution_count > 1:
            self._average_execution_time_ms = (
                (self._average_execution_time_ms * (self._execution_count - 1) + execution_time_ms) / 
                self._execution_count
            )
        else:
            self._average_execution_time_ms = execution_time_ms
            
        if error:
            self._error_count += 1


class PluginDependencyError(Exception):
    """Exception raised when a plugin dependency cannot be satisfied."""
    pass


class PluginVersionError(Exception):
    """Exception raised when a plugin version is incompatible."""
    pass


class PluginExecutionError(Exception):
    """Exception raised when a plugin execution fails."""
    pass
