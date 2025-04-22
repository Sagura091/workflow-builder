from typing import Dict, List, Any, Optional
from backend.app.services.type_registry import TypeRegistry

class TypeController:
    def __init__(self, type_registry: TypeRegistry):
        self.type_registry = type_registry
    
    def get_type_system(self) -> Dict[str, Any]:
        """Get the entire type system."""
        return {
            "types": {
                name: self._format_type_definition(type_def)
                for name, type_def in self.type_registry.get_all_types().items()
            },
            "rules": [
                self._format_type_rule(rule)
                for rule in self.type_registry.get_all_rules()
            ]
        }
    
    def get_type(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific type definition."""
        type_def = self.type_registry.get_type(type_name)
        if type_def:
            return self._format_type_definition(type_def)
        return None
    
    def check_compatibility(self, source_type: str, target_type: str) -> Dict[str, Any]:
        """Check if two types are compatible."""
        is_compatible = self.type_registry.is_compatible(source_type, target_type)
        return {
            "compatible": is_compatible,
            "sourceType": source_type,
            "targetType": target_type,
            "message": f"Types are {'compatible' if is_compatible else 'not compatible'}"
        }
    
    def get_compatible_types(self, type_name: str, as_source: bool = True) -> List[str]:
        """Get all types compatible with the given type."""
        return self.type_registry.get_compatible_types(type_name, as_source)
    
    def _format_type_definition(self, type_def) -> Dict[str, Any]:
        """Format type definition for API response."""
        return {
            "name": type_def.name,
            "description": type_def.description,
            "baseType": type_def.base_type,
            "properties": type_def.properties,
            "uiProperties": type_def.ui_properties
        }
    
    def _format_type_rule(self, rule) -> Dict[str, Any]:
        """Format type rule for API response."""
        return {
            "from": rule.source_type,
            "to": rule.target_types,
            "bidirectional": rule.bidirectional,
            "conversionRequired": rule.conversion_required,
            "conversionFunction": rule.conversion_function
        }
