#!/usr/bin/env python
"""
Script to test node connections to ensure that the type system is working correctly.
This script will:
1. Load the type system from the config directory
2. Test various node connections to ensure they are valid
3. Report any issues with the type system
"""

import os
import json
import sys
from typing import Dict, List, Any, Tuple, Set

# Define the root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the config directory
CONFIG_DIR = os.path.join(ROOT_DIR, "config")

# Define the paths to the type system files
TYPE_SYSTEM_PATH = os.path.join(CONFIG_DIR, "type_system.json")
TYPE_RULES_PATH = os.path.join(CONFIG_DIR, "type_rules.json")

def load_type_system() -> Dict[str, Any]:
    """Load the type system from the config directory."""
    try:
        with open(TYPE_SYSTEM_PATH, "r", encoding="utf-8") as f:
            type_system = json.load(f)
        
        with open(TYPE_RULES_PATH, "r", encoding="utf-8") as f:
            type_rules = json.load(f)
        
        # Combine the type system and rules
        return {
            "types": type_system.get("types", {}),
            "rules": type_rules.get("rules", []) + type_system.get("rules", [])
        }
    except Exception as e:
        print(f"Error loading type system: {e}")
        return {"types": {}, "rules": []}

def is_type_compatible(source_type: str, target_type: str, type_system: Dict[str, Any]) -> bool:
    """Check if two types are compatible."""
    # Same type is always compatible
    if source_type == target_type:
        return True
    
    # Any type is compatible with anything
    if source_type == "any" or target_type == "any":
        return True
    
    # Check the rules
    for rule in type_system["rules"]:
        if rule["from"] == source_type and target_type in rule["to"]:
            return True
        
        # Check for bidirectional rules
        if rule.get("bidirectional") and rule["from"] == target_type and source_type in rule["to"]:
            return True
    
    return False

def test_connection(source_type: str, target_type: str, type_system: Dict[str, Any]) -> Tuple[bool, str]:
    """Test a connection between two types."""
    compatible = is_type_compatible(source_type, target_type, type_system)
    
    if compatible:
        return True, f"Connection from {source_type} to {target_type} is valid"
    else:
        return False, f"Connection from {source_type} to {target_type} is invalid"

def test_all_connections(type_system: Dict[str, Any]) -> List[Tuple[bool, str]]:
    """Test all possible connections between types."""
    results = []
    types = list(type_system["types"].keys())
    
    for source_type in types:
        for target_type in types:
            results.append(test_connection(source_type, target_type, type_system))
    
    return results

def find_missing_rules(type_system: Dict[str, Any]) -> List[str]:
    """Find missing rules in the type system."""
    missing_rules = []
    types = list(type_system["types"].keys())
    
    # Check if each type has at least one rule
    for type_name in types:
        has_rule = False
        
        for rule in type_system["rules"]:
            if rule["from"] == type_name:
                has_rule = True
                break
        
        if not has_rule:
            missing_rules.append(f"No rule found for type: {type_name}")
    
    return missing_rules

def main():
    """Main function."""
    print("Testing node connections...")
    
    # Load the type system
    type_system = load_type_system()
    
    if not type_system["types"]:
        print("Error: No types found in the type system")
        sys.exit(1)
    
    # Test all connections
    results = test_all_connections(type_system)
    
    # Count valid and invalid connections
    valid_count = sum(1 for result in results if result[0])
    invalid_count = sum(1 for result in results if not result[0])
    
    print(f"Tested {len(results)} connections:")
    print(f"  - {valid_count} valid connections")
    print(f"  - {invalid_count} invalid connections")
    
    # Print invalid connections
    if invalid_count > 0:
        print("\nInvalid connections:")
        for result in results:
            if not result[0]:
                print(f"  - {result[1]}")
    
    # Find missing rules
    missing_rules = find_missing_rules(type_system)
    
    if missing_rules:
        print("\nMissing rules:")
        for rule in missing_rules:
            print(f"  - {rule}")
    
    print("\nConnection testing complete!")

if __name__ == "__main__":
    main()
