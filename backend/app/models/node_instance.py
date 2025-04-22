"""
Node Instance Models

This module defines the models for node instances, which are specific instances of node types
with their own configurations and positions in a workflow.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4

class Position(BaseModel):
    """Position of a node in the workflow canvas."""
    x: float = 0
    y: float = 0

class NodeInstanceBase(BaseModel):
    """Base model for node instances."""
    node_type_id: str
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = {}
    position: Optional[Position] = None
    workflow_id: Optional[str] = None

class NodeInstanceCreate(NodeInstanceBase):
    """Model for creating a new node instance."""
    pass

class NodeInstanceUpdate(BaseModel):
    """Model for updating an existing node instance."""
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    position: Optional[Position] = None
    workflow_id: Optional[str] = None

class NodeInstance(NodeInstanceBase):
    """Model for a node instance."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True
