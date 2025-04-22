"""
Core Node Controller

This module provides controllers for core nodes.
"""

from typing import Dict, List, Any, Optional
from backend.app.services.core_node_registry import CoreNodeRegistry
from backend.app.exceptions import NotFoundError

class CoreNodeController:
    """Controller for core node operations."""

    def __init__(self, core_node_registry: CoreNodeRegistry):
        self.core_node_registry = core_node_registry

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """
        Get all core nodes.

        Returns:
            List of core nodes
        """
        # Get all nodes
        nodes = []

        for node_id in self.core_node_registry.get_all_nodes():
            metadata = self.core_node_registry.get_node_metadata(node_id)
            if metadata:
                nodes.append(self._format_node_metadata(node_id, metadata))

        return nodes

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """
        Get a core node by ID.

        Args:
            node_id: The ID of the node

        Returns:
            Node metadata

        Raises:
            NotFoundError: If the node is not found
        """
        node_class = self.core_node_registry.get_node(node_id)
        if not node_class:
            raise NotFoundError(f"Core node not found: {node_id}")

        metadata = self.core_node_registry.get_node_metadata(node_id)
        if not metadata:
            raise NotFoundError(f"Core node metadata not found: {node_id}")

        return self._format_node_metadata(node_id, metadata)

    def get_nodes_by_directory(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all core nodes organized by directory.

        Returns:
            Dictionary mapping directory names to lists of core nodes
        """
        result = {}

        # Get all directories
        directories = self.core_node_registry.get_nodes_by_directory()

        # Get nodes for each directory
        for directory, node_ids in directories.items():
            result[directory] = []

            for node_id in node_ids:
                metadata = self.core_node_registry.get_node_metadata(node_id)
                if metadata:
                    result[directory].append(self._format_node_metadata(node_id, metadata))

        return result

    def get_nodes_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all core nodes in a category.

        Args:
            category: The category name

        Returns:
            List of core nodes in the category
        """
        # Get nodes for the category
        nodes = []

        directory_nodes = self.core_node_registry.get_nodes_by_directory(category)
        if category in directory_nodes:
            for node_id in directory_nodes[category]:
                metadata = self.core_node_registry.get_node_metadata(node_id)
                if metadata:
                    nodes.append(self._format_node_metadata(node_id, metadata))

        return nodes

    def _format_node_metadata(self, node_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format node metadata for API response."""
        # If metadata is already in the expected format, return it
        if isinstance(metadata, dict) and "id" in metadata and "name" in metadata:
            return metadata

        # Handle Pydantic models
        if hasattr(metadata, "__dict__") and not isinstance(metadata, dict):
            # Convert Pydantic model to dict
            if hasattr(metadata, "model_dump"):
                # Pydantic v2
                metadata_dict = metadata.model_dump()
            elif hasattr(metadata, "dict"):
                # Pydantic v1
                metadata_dict = metadata.dict()
            else:
                # Fallback to __dict__
                metadata_dict = metadata.__dict__
        else:
            metadata_dict = metadata if isinstance(metadata, dict) else {}

        # Convert inputs and outputs to dictionaries if they are Pydantic models
        inputs = metadata_dict.get("inputs", [])
        outputs = metadata_dict.get("outputs", [])

        # Convert inputs to dictionaries
        formatted_inputs = []
        for input_def in inputs:
            if hasattr(input_def, "dict"):
                formatted_inputs.append(input_def.dict())
            elif hasattr(input_def, "model_dump"):
                formatted_inputs.append(input_def.model_dump())
            elif isinstance(input_def, dict):
                formatted_inputs.append(input_def)
            else:
                # Skip invalid inputs
                continue

        # Convert outputs to dictionaries
        formatted_outputs = []
        for output_def in outputs:
            if hasattr(output_def, "dict"):
                formatted_outputs.append(output_def.dict())
            elif hasattr(output_def, "model_dump"):
                formatted_outputs.append(output_def.model_dump())
            elif isinstance(output_def, dict):
                formatted_outputs.append(output_def)
            else:
                # Skip invalid outputs
                continue

        # Convert config_fields to dictionaries if they are Pydantic models
        config_fields = metadata_dict.get("config_fields", [])

        # Convert config_fields to dictionaries
        formatted_config_fields = []
        for config_field in config_fields:
            if hasattr(config_field, "dict"):
                formatted_config_fields.append(config_field.dict())
            elif hasattr(config_field, "model_dump"):
                formatted_config_fields.append(config_field.model_dump())
            elif isinstance(config_field, dict):
                formatted_config_fields.append(config_field)
            else:
                # Skip invalid config_fields
                continue

        # Create a formatted metadata object
        result = {
            "id": node_id,
            "name": metadata_dict.get("name", node_id.split(".")[-1].title()),
            "category": metadata_dict.get("category", "UNKNOWN").upper(),
            "description": metadata_dict.get("description", ""),
            "inputs": formatted_inputs,
            "outputs": formatted_outputs,
            "config_fields": formatted_config_fields,
            "ui_properties": metadata_dict.get("ui_properties", {})
        }

        return result
