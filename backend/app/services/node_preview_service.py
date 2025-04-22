import time
import traceback
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
import signal

class TimeoutException(Exception):
    """Exception raised when execution times out."""
    pass

@contextmanager
def timeout(seconds):
    """Context manager for timeout."""
    def signal_handler(signum, frame):
        raise TimeoutException("Execution timed out")
    
    # Set the timeout handler
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        # Disable the alarm
        signal.alarm(0)

class NodePreviewService:
    def __init__(self, plugin_manager, type_registry):
        self.plugin_manager = plugin_manager
        self.type_registry = type_registry
    
    def preview_node(self, plugin_id: str, config: Dict[str, Any], 
                    sample_inputs: Optional[Dict[str, Any]] = None,
                    timeout_seconds: int = 5) -> Dict[str, Any]:
        """
        Execute a node with sample inputs for preview.
        
        Args:
            plugin_id: The ID of the plugin to execute
            config: The node configuration
            sample_inputs: Optional sample inputs, will be generated if not provided
            timeout_seconds: Maximum execution time in seconds
            
        Returns:
            Preview results including inputs, outputs, and execution time
        """
        # Get the plugin
        plugin = self.plugin_manager.get_plugin(plugin_id)
        if not plugin:
            return {
                "status": "error",
                "message": f"Plugin '{plugin_id}' not found"
            }
        
        # Get plugin metadata
        metadata = self.plugin_manager.get_plugin_metadata(plugin_id)
        
        # Generate sample inputs if not provided
        if not sample_inputs:
            sample_inputs = self._generate_sample_inputs(metadata)
        
        # Execute plugin with timeout protection
        try:
            start_time = time.time()
            
            with timeout(timeout_seconds):
                result = plugin.execute(config, sample_inputs)
            
            execution_time = time.time() - start_time
            
            # Format result for preview with type information
            return {
                "status": "success",
                "inputs": self._format_inputs_with_types(metadata, sample_inputs),
                "outputs": self._format_outputs_with_types(metadata, result),
                "execution_time_ms": int(execution_time * 1000)
            }
        except TimeoutException:
            return {
                "status": "error",
                "message": f"Execution timed out after {timeout_seconds} seconds"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _generate_sample_inputs(self, metadata) -> Dict[str, Any]:
        """Generate sample inputs based on plugin metadata."""
        sample_inputs = {}
        
        for input_port in metadata.inputs:
            if input_port.required:
                sample_inputs[input_port.id] = self._generate_sample_value(input_port.type)
        
        return sample_inputs
    
    def _generate_sample_value(self, type_name: str) -> Any:
        """Generate a sample value for a given type."""
        if type_name == "string":
            return "Sample text"
        elif type_name == "number":
            return 42
        elif type_name == "boolean":
            return True
        elif type_name == "object":
            return {"key": "value", "number": 123}
        elif type_name == "array":
            return ["item1", "item2", "item3"]
        elif type_name == "file":
            return "sample_file.txt"
        elif type_name == "image":
            return "sample_image.jpg"
        elif type_name == "dataset":
            return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        elif type_name == "features":
            return [[1, 2, 3], [4, 5, 6]]
        elif type_name == "model":
            return {"model_type": "sample", "parameters": {}}
        elif type_name == "predictions":
            return [0.1, 0.2, 0.7]
        else:
            return "Sample data"
    
    def _format_inputs_with_types(self, metadata, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format inputs with type information."""
        formatted_inputs = []
        
        for input_port in metadata.inputs:
            if input_port.id in inputs:
                formatted_inputs.append({
                    "id": input_port.id,
                    "name": input_port.name,
                    "type": input_port.type,
                    "value": inputs[input_port.id],
                    "preview": self._generate_preview(inputs[input_port.id], input_port.type)
                })
        
        return formatted_inputs
    
    def _format_outputs_with_types(self, metadata, outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format outputs with type information."""
        formatted_outputs = []
        
        for output_port in metadata.outputs:
            if output_port.id in outputs:
                formatted_outputs.append({
                    "id": output_port.id,
                    "name": output_port.name,
                    "type": output_port.type,
                    "value": outputs[output_port.id],
                    "preview": self._generate_preview(outputs[output_port.id], output_port.type)
                })
        
        return formatted_outputs
    
    def _generate_preview(self, value: Any, type_name: str) -> str:
        """Generate a preview string for a value."""
        if value is None:
            return "null"
        
        if isinstance(value, (str, bool, int, float)):
            return str(value)
        
        if isinstance(value, list):
            if not value:
                return "[]"
            if len(value) <= 3:
                return str(value)
            return f"[{value[0]}, {value[1]}, ... +{len(value)-2} more]"
        
        if isinstance(value, dict):
            if not value:
                return "{}"
            keys = list(value.keys())
            if len(keys) <= 3:
                return str(value)
            preview = "{"
            for i, key in enumerate(keys[:2]):
                preview += f"{key}: {value[key]}, "
            preview += f"... +{len(keys)-2} more}}"
            return preview
        
        return str(value)
