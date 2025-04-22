"""
Execution Routes

This module provides API routes for workflow execution.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.app.models.responses import StandardResponse
from backend.app.controllers.execution_controller import ExecutionController
from backend.app.dependencies import get_execution_controller

# Create models
class WorkflowExecutionRequest(BaseModel):
    """Request model for workflow execution."""
    workflow: Dict[str, Any]
    inputs: Dict[str, Any] = {}

# Create router
router = APIRouter(prefix="/api/workflows", tags=["execution"])

@router.post("/execute", response_model=StandardResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    controller: ExecutionController = Depends(get_execution_controller)
) -> StandardResponse:
    """
    Execute a workflow.
    
    Args:
        request: The workflow execution request
        
    Returns:
        Execution result or execution ID for async execution
    """
    result = await controller.execute_workflow(request.workflow, request.inputs, background_tasks)
    return StandardResponse.success(
        data=result,
        message="Workflow execution started"
    )

@router.get("/executions/{execution_id}", response_model=StandardResponse)
async def get_execution_status(
    execution_id: str,
    controller: ExecutionController = Depends(get_execution_controller)
) -> StandardResponse:
    """
    Get the status of a workflow execution.
    
    Args:
        execution_id: The ID of the execution
        
    Returns:
        Execution status
    """
    status = await controller.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found")
    
    return StandardResponse.success(
        data=status,
        message=f"Execution status for '{execution_id}' retrieved successfully"
    )

@router.get("/executions", response_model=StandardResponse)
async def get_executions(
    workflow_id: str = None,
    status: str = None,
    limit: int = 100,
    offset: int = 0,
    controller: ExecutionController = Depends(get_execution_controller)
) -> StandardResponse:
    """
    Get workflow executions.
    
    Args:
        workflow_id: Optional workflow ID to filter by
        status: Optional status to filter by
        limit: Maximum number of executions to return
        offset: Offset for pagination
        
    Returns:
        List of executions
    """
    executions = await controller.get_executions(workflow_id, status, limit, offset)
    return StandardResponse.success(
        data=executions,
        message="Executions retrieved successfully"
    )
