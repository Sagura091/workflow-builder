from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any

class ConfigField(BaseModel):
    """Configuration field definition for a node."""
    name: str
    label: str
    type: str
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None
    multiple: Optional[bool] = False
    min: Optional[float] = None
    step: Optional[float] = None

class NodeType(BaseModel):
    """Definition of a node type."""
    title: str
    icon: str
    color: str
    inputs: List[str]
    outputs: List[str]
    configFields: List[ConfigField]

class Node(BaseModel):
    """A node in a workflow."""
    id: str
    type: str
    config: Dict[str, Any] = Field(default_factory=dict)
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
