"""
Type System Controller

This module provides controllers for the type system.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

class TypeSystemController:
    """Controller for type system operations."""

    def get_type_system(self) -> Dict[str, Any]:
        """
        Get the type system.

        Returns:
            dict: The type system
        """
        try:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'type_system.json'
            with open(config_path, 'r') as f:
                type_system = json.load(f)
            return type_system
        except Exception as e:
            raise ValueError(f"Error loading type system: {str(e)}")

    def check_type_compatibility(self, source_type: str, target_type: str) -> Dict[str, Any]:
        """
        Check if two types are compatible.

        Args:
            source_type (str): The source type
            target_type (str): The target type

        Returns:
            dict: Compatibility result
        """
        try:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'type_system.json'
            with open(config_path, 'r') as f:
                type_system = json.load(f)

            # If types are the same, they are compatible
            if source_type == target_type:
                return {"compatible": True}

            # If either type is 'any', they are compatible
            if source_type == 'any' or target_type == 'any':
                return {"compatible": True}

            # Check rules
            for rule in type_system.get('rules', []):
                # Check from -> to
                if rule.get('from') == source_type and target_type in rule.get('to', []):
                    return {"compatible": True}

                # Check bidirectional rules
                if rule.get('bidirectional') and rule.get('from') == target_type and source_type in rule.get('to', []):
                    return {"compatible": True}

            return {"compatible": False}
        except Exception as e:
            raise ValueError(f"Error checking type compatibility: {str(e)}")
