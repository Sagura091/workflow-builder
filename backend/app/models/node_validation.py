from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from backend.app.models.node import Node

class NodeValidationRequest(BaseModel):
    """Request model for node validation."""
    node: Node
    connections: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    workflow_context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ValidationError(BaseModel):
    """Error details for node validation."""
    field: str
    message: str
    code: str

class NodeValidationResponse(BaseModel):
    """Response model for node validation."""
    valid: bool
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[ValidationError] = Field(default_factory=list)
    message: Optional[str] = None
