import os
import json
import importlib
import inspect
from typing import List, Dict, Any, Optional, Callable, Set, Tuple, Union
from backend.app.models.type_system import (
    TypeDefinition,
    TypeRule,
    TypeSystem,
    TypeCategory,
    TypeProperty,
    ConversionType,
    TypeConverter,
    TypeValidator
)

class TypeRegistry:
    """Registry for managing the type system."""
    _instance = None

    def __new__(cls, type_system_file: str = None):
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super(TypeRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, type_system_file: str = None):
        """Initialize the type registry."""
        if self._initialized:
            return

        self.type_system = TypeSystem()
        self.conversion_functions: Dict[str, Callable] = {}
        self.validation_functions: Dict[str, Callable] = {}

        # Load type system from file if provided
        if type_system_file and os.path.exists(type_system_file):
            self.load_from_file(type_system_file)

        self._initialized = True

    def load_from_file(self, file_path: str) -> None:
        """Load type definitions and rules from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Load type definitions
            if 'types' in data:
                for type_name, type_info in data['types'].items():
                    # Convert properties to TypeProperty objects
                    properties = {}
                    if 'properties' in type_info:
                        for prop_name, prop_info in type_info['properties'].items():
                            if isinstance(prop_info, dict):
                                properties[prop_name] = TypeProperty(
                                    name=prop_name,
                                    description=prop_info.get('description', ''),
                                    type=prop_info.get('type', 'string'),
                                    required=prop_info.get('required', False),
                                    default_value=prop_info.get('default_value'),
                                    constraints=prop_info.get('constraints', {})
                                )

                    # Determine category
                    category = TypeCategory.CUSTOM
                    if 'category' in type_info:
                        try:
                            category = TypeCategory(type_info['category'])
                        except ValueError:
                            pass

                    self.register_type(
                        TypeDefinition(
                            name=type_name,
                            description=type_info.get('description', ''),
                            category=category,
                            base_type=type_info.get('base_type'),
                            properties=properties,
                            ui_properties=type_info.get('ui_properties', {}),
                            metadata=type_info.get('metadata', {}),
                            validation_function=type_info.get('validation_function')
                        )
                    )

            # Load type rules
            if 'rules' in data:
                for rule in data['rules']:
                    # Determine conversion type
                    conversion_type = ConversionType.NONE
                    if 'conversion_type' in rule:
                        try:
                            conversion_type = ConversionType(rule['conversion_type'])
                        except ValueError:
                            # Fall back to legacy conversion_required
                            if rule.get('conversion_required', False):
                                conversion_type = ConversionType.EXPLICIT

                    self.register_rule(
                        TypeRule(
                            source_type=rule['from'],
                            target_types=rule['to'],
                            bidirectional=rule.get('bidirectional', False),
                            conversion_type=conversion_type,
                            conversion_function=rule.get('conversion_function'),
                            priority=rule.get('priority', 0),
                            constraints=rule.get('constraints', {})
                        )
                    )

            # Load type converters
            if 'converters' in data:
                for converter_name, converter_info in data['converters'].items():
                    self.register_converter(
                        TypeConverter(
                            name=converter_name,
                            description=converter_info.get('description', ''),
                            source_type=converter_info['source_type'],
                            target_type=converter_info['target_type'],
                            conversion_function=converter_info['conversion_function'],
                            bidirectional=converter_info.get('bidirectional', False),
                            reverse_conversion_function=converter_info.get('reverse_conversion_function'),
                            metadata=converter_info.get('metadata', {})
                        )
                    )

            # Load type validators
            if 'validators' in data:
                for validator_name, validator_info in data['validators'].items():
                    self.register_validator(
                        TypeValidator(
                            name=validator_name,
                            description=validator_info.get('description', ''),
                            type_name=validator_info['type_name'],
                            validation_function=validator_info['validation_function'],
                            metadata=validator_info.get('metadata', {})
                        )
                    )

            # Build type hierarchy
            self._build_type_hierarchy()

        except Exception as e:
            print(f"Error loading type system from {file_path}: {str(e)}")

    def register_type(self, type_def: TypeDefinition) -> None:
        """Register a new type definition."""
        self.type_system.types[type_def.name] = type_def

        # Update type hierarchy if base type is specified
        if type_def.base_type:
            if type_def.base_type not in self.type_system.type_hierarchy:
                self.type_system.type_hierarchy[type_def.base_type] = []
            if type_def.name not in self.type_system.type_hierarchy[type_def.base_type]:
                self.type_system.type_hierarchy[type_def.base_type].append(type_def.name)

    def register_rule(self, rule: TypeRule) -> None:
        """Register a new type compatibility rule."""
        self.type_system.rules.append(rule)

        # Sort rules by priority (higher priority first)
        self.type_system.rules.sort(key=lambda r: r.priority, reverse=True)

    def register_converter(self, converter: TypeConverter) -> None:
        """Register a new type converter."""
        self.type_system.converters[converter.name] = converter

        # Load the conversion function if specified
        if converter.conversion_function:
            self._load_function(converter.conversion_function, self.conversion_functions)

        # Load the reverse conversion function if specified
        if converter.bidirectional and converter.reverse_conversion_function:
            self._load_function(converter.reverse_conversion_function, self.conversion_functions)

    def register_validator(self, validator: TypeValidator) -> None:
        """Register a new type validator."""
        self.type_system.validators[validator.name] = validator

        # Load the validation function if specified
        if validator.validation_function:
            self._load_function(validator.validation_function, self.validation_functions)

    def get_type(self, type_name: str) -> Optional[TypeDefinition]:
        """Get a type definition by name."""
        return self.type_system.types.get(type_name)

    def get_all_types(self) -> Dict[str, TypeDefinition]:
        """Get all registered types."""
        return self.type_system.types

    def get_all_rules(self) -> List[TypeRule]:
        """Get all registered compatibility rules."""
        return self.type_system.rules

    def _load_function(self, function_path: str, function_dict: Dict[str, Callable]) -> None:
        """Load a function from a module path."""
        try:
            module_path, function_name = function_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            function = getattr(module, function_name)
            function_dict[function_path] = function
        except (ImportError, AttributeError) as e:
            print(f"Error loading function {function_path}: {str(e)}")

    def _build_type_hierarchy(self) -> None:
        """Build the type hierarchy based on base_type relationships."""
        # Clear existing hierarchy
        self.type_system.type_hierarchy = {}

        # Build hierarchy from type definitions
        for type_name, type_def in self.type_system.types.items():
            if type_def.base_type:
                if type_def.base_type not in self.type_system.type_hierarchy:
                    self.type_system.type_hierarchy[type_def.base_type] = []
                if type_name not in self.type_system.type_hierarchy[type_def.base_type]:
                    self.type_system.type_hierarchy[type_def.base_type].append(type_name)

    def is_compatible(self, source_type: str, target_type: str) -> Tuple[bool, Optional[str], Optional[ConversionType]]:
        """Check if source_type is compatible with target_type.

        Returns:
            Tuple containing:
            - bool: Whether the types are compatible
            - Optional[str]: Conversion function path if needed
            - Optional[ConversionType]: Type of conversion required
        """
        # Same types are always compatible
        if source_type == target_type:
            return True, None, ConversionType.NONE

        # 'any' type is compatible with everything
        if source_type == 'any' or target_type == 'any':
            return True, None, ConversionType.NONE

        # Check direct rules
        for rule in self.type_system.rules:
            if rule.source_type == source_type and target_type in rule.target_types:
                return True, rule.conversion_function, rule.conversion_type
            if rule.bidirectional and rule.source_type == target_type and source_type in rule.target_types:
                return True, rule.conversion_function, rule.conversion_type

        # Check converters
        for converter_name, converter in self.type_system.converters.items():
            if converter.source_type == source_type and converter.target_type == target_type:
                return True, converter.conversion_function, ConversionType.CUSTOM
            if converter.bidirectional and converter.source_type == target_type and converter.target_type == source_type:
                return True, converter.reverse_conversion_function, ConversionType.CUSTOM

        # Check inheritance (base types)
        source_def = self.get_type(source_type)
        if source_def and source_def.base_type:
            return self.is_compatible(source_def.base_type, target_type)

        # Check if target type is a base type of source type
        if target_type in self.type_system.type_hierarchy and source_type in self.type_system.type_hierarchy[target_type]:
            return True, None, ConversionType.NONE

        # Check if there's a common base type
        source_ancestors = self.get_ancestors(source_type)
        target_ancestors = self.get_ancestors(target_type)
        common_ancestors = source_ancestors.intersection(target_ancestors)
        if common_ancestors:
            return True, None, ConversionType.NONE

        return False, None, None

    def get_ancestors(self, type_name: str) -> Set[str]:
        """Get all ancestor types (base types) of a given type."""
        ancestors = set()
        current_type = type_name

        while current_type:
            type_def = self.get_type(current_type)
            if not type_def or not type_def.base_type:
                break

            ancestors.add(type_def.base_type)
            current_type = type_def.base_type

        return ancestors

    def get_descendants(self, type_name: str) -> Set[str]:
        """Get all descendant types (derived types) of a given type."""
        descendants = set()

        # Direct descendants
        if type_name in self.type_system.type_hierarchy:
            direct_descendants = set(self.type_system.type_hierarchy[type_name])
            descendants.update(direct_descendants)

            # Recursive descendants
            for descendant in direct_descendants:
                descendants.update(self.get_descendants(descendant))

        return descendants

    def get_compatible_types(self, type_name: str, as_source: bool = True) -> List[str]:
        """Get all types compatible with the given type."""
        compatible_types = set([type_name])  # A type is always compatible with itself

        # Add base types and descendants
        compatible_types.update(self.get_ancestors(type_name))
        compatible_types.update(self.get_descendants(type_name))

        if as_source:
            # Find all types that this type can connect to
            for rule in self.type_system.rules:
                if rule.source_type == type_name:
                    compatible_types.update(rule.target_types)
                elif rule.bidirectional and type_name in rule.target_types:
                    compatible_types.add(rule.source_type)

            # Add types from converters
            for converter in self.type_system.converters.values():
                if converter.source_type == type_name:
                    compatible_types.add(converter.target_type)
                elif converter.bidirectional and converter.target_type == type_name:
                    compatible_types.add(converter.source_type)
        else:
            # Find all types that can connect to this type
            for rule in self.type_system.rules:
                if type_name in rule.target_types:
                    compatible_types.add(rule.source_type)
                elif rule.bidirectional and rule.source_type == type_name:
                    compatible_types.update(rule.target_types)

            # Add types from converters
            for converter in self.type_system.converters.values():
                if converter.target_type == type_name:
                    compatible_types.add(converter.source_type)
                elif converter.bidirectional and converter.source_type == type_name:
                    compatible_types.add(converter.target_type)

        # Add 'any' type
        if type_name != 'any':
            compatible_types.add('any')

        return list(compatible_types)

    def validate_data(self, data: Any, type_name: str) -> Tuple[bool, Optional[str]]:
        """Validate data against a type.

        Args:
            data: The data to validate
            type_name: The type to validate against

        Returns:
            Tuple containing:
            - bool: Whether the data is valid
            - Optional[str]: Error message if invalid
        """
        # Get type definition
        type_def = self.get_type(type_name)
        if not type_def:
            return False, f"Unknown type: {type_name}"

        # Check if type has a validation function
        if type_def.validation_function:
            if type_def.validation_function in self.validation_functions:
                validation_func = self.validation_functions[type_def.validation_function]
                try:
                    result = validation_func(data)
                    if isinstance(result, tuple) and len(result) == 2:
                        return result
                    elif isinstance(result, bool):
                        return result, None if result else "Validation failed"
                    else:
                        return False, "Invalid validation function result"
                except Exception as e:
                    return False, f"Validation error: {str(e)}"

        # Check if type has a validator
        for validator in self.type_system.validators.values():
            if validator.type_name == type_name:
                if validator.validation_function in self.validation_functions:
                    validation_func = self.validation_functions[validator.validation_function]
                    try:
                        result = validation_func(data)
                        if isinstance(result, tuple) and len(result) == 2:
                            return result
                        elif isinstance(result, bool):
                            return result, None if result else "Validation failed"
                        else:
                            return False, "Invalid validation function result"
                    except Exception as e:
                        return False, f"Validation error: {str(e)}"

        # Basic type validation
        if type_name == 'string':
            return isinstance(data, str), None if isinstance(data, str) else "Expected a string"
        elif type_name == 'number':
            return isinstance(data, (int, float)), None if isinstance(data, (int, float)) else "Expected a number"
        elif type_name == 'boolean':
            return isinstance(data, bool), None if isinstance(data, bool) else "Expected a boolean"
        elif type_name == 'object':
            return isinstance(data, dict), None if isinstance(data, dict) else "Expected an object"
        elif type_name == 'array':
            return isinstance(data, list), None if isinstance(data, list) else "Expected an array"

        # Check base type
        if type_def.base_type:
            return self.validate_data(data, type_def.base_type)

        # Default to valid if no validation is defined
        return True, None

    def convert_data(self, data: Any, source_type: str, target_type: str) -> Tuple[Any, bool, Optional[str]]:
        """Convert data from source_type to target_type.

        Args:
            data: The data to convert
            source_type: The source type
            target_type: The target type

        Returns:
            Tuple containing:
            - Any: The converted data
            - bool: Whether the conversion was successful
            - Optional[str]: Error message if unsuccessful
        """
        # If types are the same, no conversion needed
        if source_type == target_type:
            return data, True, None

        # Check if conversion is needed
        is_compatible, conversion_function, conversion_type = self.is_compatible(source_type, target_type)

        if not is_compatible:
            return None, False, f"Cannot convert from {source_type} to {target_type}"

        # If no conversion needed, return data as is
        if conversion_type == ConversionType.NONE or not conversion_function:
            return data, True, None

        # If conversion function is specified, use it
        if conversion_function in self.conversion_functions:
            conversion_func = self.conversion_functions[conversion_function]
            try:
                result = conversion_func(data)
                return result, True, None
            except Exception as e:
                return None, False, f"Conversion error: {str(e)}"

        # Check converters
        for converter in self.type_system.converters.values():
            if converter.source_type == source_type and converter.target_type == target_type:
                if converter.conversion_function in self.conversion_functions:
                    conversion_func = self.conversion_functions[converter.conversion_function]
                    try:
                        result = conversion_func(data)
                        return result, True, None
                    except Exception as e:
                        return None, False, f"Conversion error: {str(e)}"
            elif converter.bidirectional and converter.source_type == target_type and converter.target_type == source_type:
                if converter.reverse_conversion_function in self.conversion_functions:
                    conversion_func = self.conversion_functions[converter.reverse_conversion_function]
                    try:
                        result = conversion_func(data)
                        return result, True, None
                    except Exception as e:
                        return None, False, f"Conversion error: {str(e)}"

        # Basic conversions
        if target_type == 'string':
            try:
                return str(data), True, None
            except Exception as e:
                return None, False, f"Cannot convert to string: {str(e)}"
        elif target_type == 'number':
            try:
                if isinstance(data, str):
                    return float(data), True, None
                elif isinstance(data, bool):
                    return 1 if data else 0, True, None
                else:
                    return float(data), True, None
            except Exception as e:
                return None, False, f"Cannot convert to number: {str(e)}"
        elif target_type == 'boolean':
            try:
                if isinstance(data, str):
                    return data.lower() in ('true', 'yes', '1', 'y'), True, None
                elif isinstance(data, (int, float)):
                    return bool(data), True, None
                else:
                    return bool(data), True, None
            except Exception as e:
                return None, False, f"Cannot convert to boolean: {str(e)}"

        # If we get here, conversion failed
        return None, False, f"No conversion available from {source_type} to {target_type}"
