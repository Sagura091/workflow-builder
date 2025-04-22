import os
import json
from typing import Dict, Any, List, Tuple, Optional, Set
from backend.app.services.type_registry import TypeRegistry
from backend.app.models.type_system import ConversionType

class ValidationService:
    """Service for validating workflows and connections."""

    def __init__(self, type_system_file: str = None):
        """Initialize the validation service."""
        # Set default path relative to the project root
        if type_system_file is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            type_system_file = os.path.join(project_root, "config", "type_system.json")

        # Initialize type registry
        self.type_registry = TypeRegistry(type_system_file)

        # For backward compatibility
        self.rules = {}
        self.types = {}

        # Load rules and types from registry
        self._load_from_registry()

    def _load_from_registry(self) -> None:
        """Load rules and types from the type registry."""
        # Load rules
        for rule in self.type_registry.get_all_rules():
            if rule.source_type not in self.rules:
                self.rules[rule.source_type] = []
            self.rules[rule.source_type].extend(rule.target_types)

        # Load types
        for type_name, type_def in self.type_registry.get_all_types().items():
            self.types[type_name] = type_def.description

    def _get_port_type(self, node_type: str, port_name: str, port_direction: str) -> str:
        """Get the type of a port based on node type and port name.

        Args:
            node_type: The type of the node
            port_name: The name of the port
            port_direction: Either "input" or "output"

        Returns:
            The type of the port, or "any" if not found
        """
        # Default to "any" if port name is not specified
        if not port_name:
            return "any"

        # Try to get node type definition from a node_types.json file
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            node_types_file = os.path.join(project_root, "node_types.json")

            if os.path.exists(node_types_file):
                with open(node_types_file, "r") as f:
                    node_types = json.load(f)

                # Look for the node type definition
                if node_type in node_types:
                    node_def = node_types[node_type]

                    # Check inputs or outputs based on direction
                    if port_direction == "input" and "inputs" in node_def:
                        for input_def in node_def["inputs"]:
                            if input_def.get("name") == port_name:
                                return input_def.get("type", port_name)

                    elif port_direction == "output" and "outputs" in node_def:
                        for output_def in node_def["outputs"]:
                            if output_def.get("name") == port_name:
                                return output_def.get("type", port_name)
        except Exception as e:
            print(f"Error getting port type: {str(e)}")

        # If we couldn't find a type definition, use the port name as the type
        return port_name

    def validate_connection(self, from_type: str, to_type: str) -> Tuple[bool, Optional[str]]:
        """Validate a connection between two types.

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Use the type registry to check compatibility
        is_compatible, conversion_function, conversion_type = self.type_registry.is_compatible(from_type, to_type)

        if is_compatible:
            # Check if conversion is required
            if conversion_type == ConversionType.EXPLICIT:
                return True, f"Connection requires explicit conversion from '{from_type}' to '{to_type}'"
            return True, None
        else:
            # Get type descriptions for better error messages
            from_def = self.type_registry.get_type(from_type)
            to_def = self.type_registry.get_type(to_type)

            from_desc = from_def.description if from_def else from_type
            to_desc = to_def.description if to_def else to_type

            return False, f"Cannot connect '{from_type}' ({from_desc}) to '{to_type}' ({to_desc})"

    def validate_workflow_connections(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate all connections in a workflow.

        Returns:
            List[Dict[str, Any]]: List of validation errors
        """
        errors = []

        # Build a map of node IDs to node types
        node_map = {node["id"]: node for node in nodes}

        for edge in edges:
            source_id = edge.get("source")
            target_id = edge.get("target")
            source_port = edge.get("source_port")
            target_port = edge.get("target_port")

            # Check if nodes exist
            if source_id not in node_map:
                errors.append({
                    "type": "connection",
                    "id": f"{source_id}-{target_id}",
                    "message": f"Source node '{source_id}' does not exist"
                })
                continue

            if target_id not in node_map:
                errors.append({
                    "type": "connection",
                    "id": f"{source_id}-{target_id}",
                    "message": f"Target node '{target_id}' does not exist"
                })
                continue

            # Get node types
            source_node = node_map[source_id]
            target_node = node_map[target_id]

            # Get port types from node metadata
            # First, try to get from the node type definition
            source_node_type = source_node.get("type", "")
            target_node_type = target_node.get("type", "")

            # Get port types based on node type and port name
            source_type = self._get_port_type(source_node_type, source_port, "output")
            target_type = self._get_port_type(target_node_type, target_port, "input")

            # Validate connection
            is_valid, error_message = self.validate_connection(source_type, target_type)

            if not is_valid:
                errors.append({
                    "type": "connection",
                    "id": f"{source_id}-{target_id}",
                    "message": error_message
                })

        return errors

    def validate_node_config(self, node_type: str, config: Dict[str, Any], plugin_meta: Dict[str, Any]) -> List[str]:
        """Validate a node's configuration."""
        errors = []

        # Get the config fields from the plugin metadata
        config_fields = plugin_meta.get("configFields", [])

        for field in config_fields:
            field_name = field.get("name")
            field_type = field.get("type")

            # Check if required field is missing
            if field.get("required", False) and (field_name not in config or config[field_name] is None):
                errors.append(f"Required field '{field_name}' is missing")
                continue

            # Skip validation if field is not in config
            if field_name not in config:
                continue

            value = config[field_name]

            # Validate field based on type
            if field_type in self.type_registry.get_all_types():
                # Use type registry to validate the value
                is_valid, error_message = self.type_registry.validate_data(value, field_type)
                if not is_valid:
                    errors.append(f"Field '{field_name}': {error_message}")
            elif field_type == "number":
                if not isinstance(value, (int, float)):
                    errors.append(f"Field '{field_name}' must be a number")

                # Check min/max constraints
                if "min" in field and value < field["min"]:
                    errors.append(f"Field '{field_name}' must be at least {field['min']}")

                if "max" in field and value > field["max"]:
                    errors.append(f"Field '{field_name}' must be at most {field['max']}")

            elif field_type == "select" and "options" in field:
                if field.get("multiple", False):
                    if not isinstance(value, list):
                        errors.append(f"Field '{field_name}' must be a list")
                    else:
                        for item in value:
                            if not any(item == opt.get("value", opt) for opt in field["options"]):
                                errors.append(f"Invalid option '{item}' for field '{field_name}'")
                else:
                    if not any(value == opt.get("value", opt) for opt in field["options"]):
                        errors.append(f"Invalid option '{value}' for field '{field_name}'")

        return errors

    def validate_data(self, data: Any, type_name: str) -> Tuple[bool, Optional[str]]:
        """Validate data against a type."""
        return self.type_registry.validate_data(data, type_name)

    def convert_data(self, data: Any, source_type: str, target_type: str) -> Tuple[Any, bool, Optional[str]]:
        """Convert data from one type to another."""
        return self.type_registry.convert_data(data, source_type, target_type)
