from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Callable, Set
from enum import Enum

class TypeCategory(str, Enum):
    """Categories for organizing types."""
    PRIMITIVE = "primitive"  # Basic types like string, number, boolean
    CONTAINER = "container"  # Container types like object, array
    FILE = "file"  # File-related types
    DATA = "data"  # Data-related types like dataset, features
    ML = "ml"  # Machine learning types like model, predictions
    CUSTOM = "custom"  # Custom types defined by plugins
    SYSTEM = "system"  # System types like any, trigger

class TypeProperty(BaseModel):
    """Definition of a property for a type."""
    name: str
    description: str
    type: str
    required: bool = False
    default_value: Optional[Any] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)

class TypeDefinition(BaseModel):
    """Definition of a data type in the type system."""
    name: str
    description: str
    category: TypeCategory = TypeCategory.CUSTOM
    base_type: Optional[str] = None
    properties: Dict[str, TypeProperty] = Field(default_factory=dict)
    ui_properties: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    validation_function: Optional[str] = None

class ConversionType(str, Enum):
    """Types of conversions between types."""
    NONE = "none"  # No conversion needed
    IMPLICIT = "implicit"  # Automatic conversion (e.g., number to string)
    EXPLICIT = "explicit"  # Requires explicit conversion node
    CUSTOM = "custom"  # Custom conversion function

class TypeRule(BaseModel):
    """Rule defining compatibility between types."""
    source_type: str
    target_types: List[str]
    bidirectional: bool = False
    conversion_type: ConversionType = ConversionType.NONE
    conversion_function: Optional[str] = None
    priority: int = 0  # Higher priority rules take precedence
    constraints: Dict[str, Any] = Field(default_factory=dict)  # Additional constraints for the rule

class TypeConverter(BaseModel):
    """Converter for transforming data between types."""
    name: str
    description: str
    source_type: str
    target_type: str
    conversion_function: str
    bidirectional: bool = False
    reverse_conversion_function: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TypeValidator(BaseModel):
    """Validator for checking if data conforms to a type."""
    name: str
    description: str
    type_name: str
    validation_function: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TypeSystem(BaseModel):
    """Complete type system with types, rules, converters, and validators."""
    types: Dict[str, TypeDefinition] = Field(default_factory=dict)
    rules: List[TypeRule] = Field(default_factory=list)
    converters: Dict[str, TypeConverter] = Field(default_factory=dict)
    validators: Dict[str, TypeValidator] = Field(default_factory=dict)
    type_hierarchy: Dict[str, List[str]] = Field(default_factory=dict)  # Map of type to its subtypes
