from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class PortType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    FILE = "file"
    IMAGE = "image"
    DATASET = "dataset"
    MODEL = "model"
    FEATURES = "features"
    PREDICTIONS = "predictions"
    ANY = "any"

class PortDirection(str, Enum):
    INPUT = "input"
    OUTPUT = "output"

class NodeCategory(str, Enum):
    DATA = "Data"
    PROCESSING = "Processing"
    VISUALIZATION = "Visualization"
    MACHINE_LEARNING = "Machine Learning"
    DEPLOYMENT = "Deployment"
    UTILITIES = "Utilities"
    CUSTOM = "Custom"
    CONTROL_FLOW = "Control Flow"
    CONVERTERS = "Converters"
    TEXT = "Text"
    MATH = "Math"
    FILE_STORAGE = "File Storage"
    WEB_API = "Web API"
    LOGIC = "Logic"
    AI_ML = "AI & ML"
    VARIABLES = "Variables"

class PortDefinition(BaseModel):
    id: str
    name: str
    type: str
    description: str
    required: bool = True
    default_value: Optional[Any] = None
    accepts_multiple: bool = False
    ui_properties: Dict[str, Any] = Field(default_factory=dict)

class ConfigField(BaseModel):
    id: str
    name: str
    type: str  # text, number, select, checkbox, code, color, etc.
    description: str
    required: bool = False
    default_value: Optional[Any] = None
    options: Optional[List[Dict[str, Any]]] = None  # For select fields
    validation: Dict[str, Any] = Field(default_factory=dict)
    ui_properties: Dict[str, Any] = Field(default_factory=dict)

class PluginMetadata(BaseModel):
    id: str
    name: str
    version: str
    description: str
    author: str
    category: NodeCategory
    tags: List[str] = []
    inputs: List[PortDefinition] = []
    outputs: List[PortDefinition] = []
    config_fields: List[ConfigField] = []
    ui_properties: Dict[str, Any] = Field(default_factory=dict)
    examples: List[Dict[str, Any]] = []
    documentation_url: Optional[str] = None
