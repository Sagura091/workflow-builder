"""
Standalone Plugin Base

This module provides a base class for plugins that can be executed independently
without requiring begin and end nodes from the core system.
"""

from typing import Dict, Any, Optional, List, ClassVar
import uuid
import time
import logging
from datetime import datetime

from backend.app.models.plugin_interface import PluginInterface
from backend.app.models.plugin_metadata import PluginMetadata
from backend.app.models.node import Node
from backend.app.models.connection import Edge
from backend.app.models.workflow import NodeExecutionResult, NodeExecutionStatus
from backend.app.services.workflow_executor import WorkflowExecutor

logger = logging.getLogger("workflow_builder")

class StandalonePluginBase(PluginInterface):
    """
    Base class for plugins that can be executed independently.
    
    This class extends the standard PluginInterface to add standalone execution
    capabilities, allowing plugins to be executed without requiring begin and end
    nodes from the core system.
    """
    
    # Class variables
    __plugin_meta__: ClassVar[PluginMetadata]
    __plugin_version__: ClassVar[str] = "1.0.0"
    __plugin_dependencies__: ClassVar[List[str]] = []
    __plugin_author__: ClassVar[str] = "Unknown"
    __plugin_license__: ClassVar[str] = "MIT"
    
    # Standalone execution flag
    __standalone_capable__: ClassVar[bool] = True
    
    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
    
    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the plugin.
        
        Args:
            inputs: Dictionary of input values
            config: Dictionary of configuration values
            
        Returns:
            Dictionary of output values
        """
        raise NotImplementedError("Plugin must implement execute method")
    
    @classmethod
    def run_standalone(cls, inputs: Optional[Dict[str, Any]] = None, 
                      config: Optional[Dict[str, Any]] = None,
                      execution_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the plugin in standalone mode.
        
        This method creates a mini-workflow with just this plugin and executes it.
        
        Args:
            inputs: Dictionary of input values (optional)
            config: Dictionary of configuration values (optional)
            execution_context: Additional execution context (optional)
            
        Returns:
            Dictionary containing the execution results
        """
        # Initialize inputs and config if not provided
        if inputs is None:
            inputs = {}
        
        if config is None:
            config = {}
            
        if execution_context is None:
            execution_context = {}
        
        # Create an instance of the plugin
        plugin_instance = cls()
        
        # Check if the plugin is standalone capable
        if not getattr(cls, "__standalone_capable__", True):
            logger.warning(f"Plugin {cls.__name__} is not marked as standalone capable")
        
        # Determine execution mode
        execution_mode = execution_context.get("execution_mode", "standalone")
        
        # If direct execution is requested, just run the plugin
        if execution_mode == "direct":
            logger.info(f"Executing plugin {cls.__name__} in direct mode")
            start_time = time.time()
            
            try:
                # Validate inputs and config
                validated_inputs = plugin_instance.validate_inputs(inputs)
                validated_config = plugin_instance.validate_config(config)
                
                # Execute the plugin
                result = plugin_instance.execute(validated_inputs, validated_config)
                
                # Calculate execution time
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Add execution metadata
                result["_execution_info"] = {
                    "execution_time_ms": execution_time_ms,
                    "execution_mode": "direct",
                    "timestamp": datetime.now().isoformat(),
                    "plugin": cls.__name__
                }
                
                return result
                
            except Exception as e:
                logger.error(f"Error executing plugin {cls.__name__} in direct mode: {str(e)}")
                return {
                    "error": str(e),
                    "_execution_info": {
                        "execution_time_ms": (time.time() - start_time) * 1000,
                        "execution_mode": "direct",
                        "timestamp": datetime.now().isoformat(),
                        "plugin": cls.__name__,
                        "status": "error"
                    }
                }
        
        # Otherwise, create a mini-workflow
        logger.info(f"Executing plugin {cls.__name__} in standalone mode with mini-workflow")
        
        try:
            # Create a workflow executor
            executor = WorkflowExecutor()
            
            # Generate node IDs
            begin_node_id = f"auto-begin-{uuid.uuid4()}"
            plugin_node_id = f"auto-plugin-{uuid.uuid4()}"
            end_node_id = f"auto-end-{uuid.uuid4()}"
            
            # Create nodes
            begin_node = Node(
                id=begin_node_id,
                type="core.begin",
                x=100,
                y=100,
                config={
                    "workflow_name": f"Standalone {cls.__name__} Execution",
                    "initial_data": "{}"
                }
            )
            
            plugin_node = Node(
                id=plugin_node_id,
                type=cls.__plugin_meta__.id,
                x=300,
                y=100,
                config=config
            )
            
            end_node = Node(
                id=end_node_id,
                type="core.end",
                x=500,
                y=100,
                config={
                    "log_result": True
                }
            )
            
            # Create connections
            connections = [
                Edge(
                    id=f"conn-{uuid.uuid4()}",
                    source=begin_node_id,
                    target=plugin_node_id,
                    source_port="trigger",
                    target_port=list(cls.__plugin_meta__.inputs)[0] if cls.__plugin_meta__.inputs else None
                ),
                Edge(
                    id=f"conn-{uuid.uuid4()}",
                    source=plugin_node_id,
                    target=end_node_id,
                    source_port=list(cls.__plugin_meta__.outputs)[0] if cls.__plugin_meta__.outputs else None,
                    target_port="result"
                )
            ]
            
            # Add input connections if provided
            if inputs:
                # TODO: Add input connections based on provided inputs
                pass
            
            # Execute the workflow
            execution_id = str(uuid.uuid4())
            result = executor.execute(
                nodes=[begin_node, plugin_node, end_node],
                edges=connections,
                execution_id=execution_id,
                execution_options={
                    "standalone_execution": True,
                    "plugin_inputs": inputs
                }
            )
            
            # Extract plugin result from workflow result
            if "node_outputs" in result and plugin_node_id in result["node_outputs"]:
                plugin_result = result["node_outputs"][plugin_node_id]
                
                # Add execution metadata
                plugin_result["_execution_info"] = {
                    "execution_id": execution_id,
                    "execution_time_ms": result.get("execution_time_ms", 0),
                    "execution_mode": "standalone",
                    "timestamp": datetime.now().isoformat(),
                    "plugin": cls.__name__
                }
                
                return plugin_result
            
            # If plugin result not found, return the whole workflow result
            return result
            
        except Exception as e:
            logger.error(f"Error executing plugin {cls.__name__} in standalone mode: {str(e)}")
            return {
                "error": str(e),
                "_execution_info": {
                    "execution_mode": "standalone",
                    "timestamp": datetime.now().isoformat(),
                    "plugin": cls.__name__,
                    "status": "error"
                }
            }
    
    @classmethod
    def get_standalone_capabilities(cls) -> Dict[str, Any]:
        """
        Get information about the plugin's standalone capabilities.
        
        Returns:
            Dictionary containing information about the plugin's standalone capabilities
        """
        return {
            "standalone_capable": getattr(cls, "__standalone_capable__", True),
            "execution_modes": ["direct", "standalone"],
            "plugin_id": cls.__plugin_meta__.id,
            "plugin_name": cls.__plugin_meta__.name,
            "plugin_version": cls.__plugin_version__,
            "plugin_author": cls.__plugin_author__,
            "plugin_license": cls.__plugin_license__
        }
