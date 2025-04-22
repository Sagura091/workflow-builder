from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from backend.app.models.node import ConfigField

class PluginMeta(BaseModel):
    """Metadata for a plugin."""
    name: str
    category: str
    description: str
    editable: bool = True
    generated: bool = False
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    configFields: List[ConfigField]

class Plugin(BaseModel):
    """A plugin definition."""
    id: str
    meta: PluginMeta
    
    class Config:
        arbitrary_types_allowed = True
