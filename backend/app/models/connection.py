from pydantic import BaseModel
from typing import Optional

class ConnectionPoint(BaseModel):
    """A connection point on a node."""
    nodeId: str
    port: str

class Connection(BaseModel):
    """A connection between two nodes."""
    id: Optional[str] = None
    from_point: ConnectionPoint
    to_point: ConnectionPoint

class Edge(BaseModel):
    """A simplified edge representation for API requests."""
    source: str
    target: str
    source_port: Optional[str] = None
    target_port: Optional[str] = None
