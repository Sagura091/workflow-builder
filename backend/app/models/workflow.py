from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Set, Union
from datetime import datetime
from enum import Enum
from backend.app.models.node import Node
from backend.app.models.connection import Edge, Connection

class ExecutionMode(str, Enum):
    """Execution mode for workflows."""
    FULL = "full"  # Execute the entire workflow
    PARTIAL = "partial"  # Execute only selected nodes
    RESUME = "resume"  # Resume from a specific node

class WorkflowRequest(BaseModel):
    """Request model for workflow operations."""
    id: Optional[str] = None
    name: Optional[str] = "Untitled Workflow"
    nodes: List[Node]
    edges: List[Edge]

class WorkflowExecutionRequest(BaseModel):
    """Request model for workflow execution."""
    workflow: WorkflowRequest
    execution_mode: ExecutionMode = ExecutionMode.FULL
    selected_nodes: Optional[List[str]] = None  # Node IDs to execute in partial mode
    resume_from_node: Optional[str] = None  # Node ID to resume from
    previous_execution_id: Optional[str] = None  # ID of previous execution to resume from
    execution_options: Dict[str, Any] = Field(default_factory=dict)  # Additional execution options

class ExecutionStatus(str, Enum):
    """Status of a workflow execution."""
    PENDING = "pending"  # Execution is pending
    RUNNING = "running"  # Execution is in progress
    COMPLETED = "completed"  # Execution completed successfully
    FAILED = "failed"  # Execution failed
    STOPPED = "stopped"  # Execution was stopped by the user
    PAUSED = "paused"  # Execution is paused

class NodeExecutionStatus(str, Enum):
    """Status of a node execution."""
    PENDING = "pending"  # Node execution is pending
    RUNNING = "running"  # Node is currently executing
    COMPLETED = "completed"  # Node executed successfully
    FAILED = "failed"  # Node execution failed
    SKIPPED = "skipped"  # Node was skipped
    CACHED = "cached"  # Node result was retrieved from cache

class ExecutionLog(BaseModel):
    """Log entry for workflow execution."""
    node: str
    status: str
    value: Any
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    execution_time_ms: Optional[float] = None
    cached: bool = False
    traceback: Optional[str] = None

class NodeExecutionResult(BaseModel):
    """Result of a node execution."""
    node_id: str
    node_type: str
    status: NodeExecutionStatus
    outputs: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error: Optional[str] = None
    cached: bool = False

class ExecutionResult(BaseModel):
    """Result of a workflow execution."""
    execution_id: str
    status: ExecutionStatus
    node_outputs: Dict[str, Any] = Field(default_factory=dict)
    node_results: Dict[str, NodeExecutionResult] = Field(default_factory=dict)
    log: List[ExecutionLog] = Field(default_factory=list)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None
    traceback: Optional[str] = None

class WorkflowResponse(BaseModel):
    """Response model for workflow operations."""
    id: str
    name: str
    nodes: List[Node]
    connections: List[Connection]

class WorkflowExecutionResponse(BaseModel):
    """Response model for workflow execution."""
    status: str = "success"
    execution_id: str
    results: Optional[ExecutionResult] = None
    message: Optional[str] = None
    error: Optional[str] = None

class WorkflowExecutionState(BaseModel):
    """State of a workflow execution."""
    execution_id: str
    workflow_id: str
    status: ExecutionStatus
    node_statuses: Dict[str, NodeExecutionStatus] = Field(default_factory=dict)
    current_node: Optional[str] = None
    completed_nodes: List[str] = Field(default_factory=list)
    failed_nodes: List[str] = Field(default_factory=list)
    skipped_nodes: List[str] = Field(default_factory=list)
    start_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    execution_time_ms: Optional[float] = None
    execution_mode: ExecutionMode = ExecutionMode.FULL
    selected_nodes: List[str] = Field(default_factory=list)
    resume_from_node: Optional[str] = None
    previous_execution_id: Optional[str] = None
