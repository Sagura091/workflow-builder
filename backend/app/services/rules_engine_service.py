"""
Rules Engine Service

This module provides functionality to validate connections between nodes based on type rules.
"""

import json
import os
from typing import Dict, List, Any, Optional, Set

class RulesEngineService:
    """Service for validating connections based on type rules."""
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        Initialize the rules engine service.
        
        Args:
            rules_path: Path to the type rules JSON file. If None, uses the default.
        """
        if rules_path is None:
            # Get the path to the type rules file
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.rules_path = os.path.join(current_dir, "config", "type_rules.json")
        else:
            self.rules_path = rules_path
        
        # Load the type rules
        self.type_rules = self._load_type_rules()
        self.rule_map = {rule["from"]: rule["to"] for rule in self.type_rules["rules"]}
    
    def _load_type_rules(self) -> Dict[str, Any]:
        """
        Load the type rules from the JSON file.
        
        Returns:
            The type rules
        """
        try:
            with open(self.rules_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading type rules: {e}")
            return {"rules": []}
    
    def validate_connection(self, from_type: str, to_type: str) -> bool:
        """
        Validate a connection between two types.
        
        Args:
            from_type: The source type
            to_type: The target type
            
        Returns:
            True if the connection is valid, False otherwise
        """
        # If either type is 'any', the connection is valid
        if from_type == "any" or to_type == "any":
            return True
        
        # If the types are the same, the connection is valid
        if from_type == to_type:
            return True
        
        # Check the rule map
        if from_type not in self.rule_map:
            return False
        
        return to_type in self.rule_map[from_type]
    
    def get_compatible_types(self, type_name: str, as_source: bool = True) -> List[str]:
        """
        Get all types compatible with the given type.
        
        Args:
            type_name: The type name
            as_source: Whether to check compatibility as source (True) or target (False)
            
        Returns:
            List of compatible types
        """
        compatible_types = set()
        
        # Add the type itself
        compatible_types.add(type_name)
        
        # Add 'any' type
        compatible_types.add("any")
        
        if as_source:
            # If the type is a source, get all target types it can connect to
            if type_name in self.rule_map:
                compatible_types.update(self.rule_map[type_name])
        else:
            # If the type is a target, get all source types that can connect to it
            for source, targets in self.rule_map.items():
                if type_name in targets:
                    compatible_types.add(source)
        
        return list(compatible_types)

# For backwards compatibility
def validate_connection(from_type: str, to_type: str) -> bool:
    """
    Validate a connection between two types.
    
    Args:
        from_type: The source type
        to_type: The target type
        
    Returns:
        True if the connection is valid, False otherwise
    """
    engine = RulesEngineService()
    return engine.validate_connection(from_type, to_type)
