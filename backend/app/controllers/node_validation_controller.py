"""
Node Validation Controller

This module provides controllers for validating node definitions.
"""

from typing import Dict, Any

class NodeValidationController:
    """Controller for node validation operations."""

    def validate_node_definition(self, node_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a node definition.

        Args:
            node_def (dict): The node definition to validate

        Returns:
            dict: Validation result
        """
        try:
            # Check required fields
            if not node_def.get('id'):
                return {
                    "valid": False,
                    "message": "Node definition missing required field: id"
                }

            # For backward compatibility, use title as name if name is not provided
            if not node_def.get('name') and node_def.get('title'):
                node_def['name'] = node_def['title']

            if not node_def.get('name'):
                return {
                    "valid": False,
                    "message": "Node definition missing required field: name"
                }

            # Category is optional, default to 'Uncategorized'
            if not node_def.get('category'):
                node_def['category'] = 'Uncategorized'

            # Validate inputs
            inputs = node_def.get('inputs', [])
            if not isinstance(inputs, list):
                return {
                    "valid": False,
                    "message": "Inputs must be an array"
                }

            # Validate input ports
            for i, input_port in enumerate(inputs):
                # For backward compatibility, use name as id if id is not provided
                if not input_port.get('id') and input_port.get('name'):
                    input_port['id'] = input_port['name']

                # If still no id, generate one
                if not input_port.get('id'):
                    input_port['id'] = f"input_{i}"

                # If no name, use id
                if not input_port.get('name'):
                    input_port['name'] = input_port.get('id')

                # If no type, default to 'any'
                if not input_port.get('type'):
                    input_port['type'] = 'any'

            # Validate outputs
            outputs = node_def.get('outputs', [])
            if not isinstance(outputs, list):
                return {
                    "valid": False,
                    "message": "Outputs must be an array"
                }

            # Validate output ports
            for i, output_port in enumerate(outputs):
                # For backward compatibility, use name as id if id is not provided
                if not output_port.get('id') and output_port.get('name'):
                    output_port['id'] = output_port['name']

                # If still no id, generate one
                if not output_port.get('id'):
                    output_port['id'] = f"output_{i}"

                # If no name, use id
                if not output_port.get('name'):
                    output_port['name'] = output_port.get('id')

                # If no type, default to 'any'
                if not output_port.get('type'):
                    output_port['type'] = 'any'

            # Set status to available if not provided
            if not node_def.get('status'):
                node_def['status'] = 'available'

            return {
                "valid": True,
                "node_def": node_def  # Return the updated node definition
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"Validation error: {str(e)}"
            }
