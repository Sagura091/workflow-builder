"""
Executions Router

This module provides API endpoints for workflow executions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, List, Any, Optional

from backend.app.models.responses import StandardResponse
from backend.app.models.workflow import (
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    ExecutionMode,
    WorkflowExecutionState
)
from backend.app.controllers.execution_controller import ExecutionController
from backend.app.dependencies import get_execution_controller
from backend.app.services.auth_service import AuthService
from backend.app.models.user import User
from backend.app.exceptions import NotFoundError, ValidationError, ExecutionError

# Create router with API versioning
router = APIRouter(prefix="/api/v1/executions", tags=["Executions"])

@router.post("/", response_model=StandardResponse)
async def execute_workflow(
    execution_request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    controller: ExecutionController = Depends(get_execution_controller),
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """
    Execute a workflow.
    
    Args:
        execution_request: The execution request
        background_tasks: FastAPI background tasks
        
    Returns:
        StandardResponse: Response containing the execution result or ID
    """
    try:
        # Check execution mode
        if execution_request.mode == ExecutionMode.SYNC:
            # Synchronous execution
            result = await controller.execute_workflow(execution_request.workflow, execution_request.inputs)
            return StandardResponse.success(
                message="Workflow executed successfully",
                data=result
            )
        else:
            # Asynchronous execution
            execution_id = controller.start_execution(execution_request.workflow, execution_request.inputs)
            background_tasks.add_task(controller.execute_workflow_async, execution_id)
            return StandardResponse.success(
                message="Workflow execution started",
                data={"execution_id": execution_id}
            )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ExecutionError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=StandardResponse)
async def get_all_executions(
    controller: ExecutionController = Depends(get_execution_controller),
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """
    Get all workflow executions.
    
    Returns:
        StandardResponse: Response containing all executions
    """
    try:
        executions = controller.get_all_executions()
        return StandardResponse.success(data=executions)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{execution_id}", response_model=StandardResponse)
async def get_execution(
    execution_id: str,
    controller: ExecutionController = Depends(get_execution_controller),
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """
    Get a specific execution by ID.
    
    Args:
        execution_id: The ID of the execution to get
        
    Returns:
        StandardResponse: Response containing the specified execution
    """
    try:
        execution = controller.get_execution(execution_id)
        return StandardResponse.success(data=execution)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{execution_id}", response_model=StandardResponse)
async def cancel_execution(
    execution_id: str,
    controller: ExecutionController = Depends(get_execution_controller),
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """
    Cancel a workflow execution.
    
    Args:
        execution_id: The ID of the execution to cancel
        
    Returns:
        StandardResponse: Response indicating success or failure
    """
    try:
        controller.cancel_execution(execution_id)
        return StandardResponse.success(message="Execution cancelled successfully")
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{execution_id}/status", response_model=StandardResponse)
async def get_execution_status(
    execution_id: str,
    controller: ExecutionController = Depends(get_execution_controller),
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """
    Get the status of a workflow execution.
    
    Args:
        execution_id: The ID of the execution to get the status for
        
    Returns:
        StandardResponse: Response containing the execution status
    """
    try:
        status = controller.get_execution_status(execution_id)
        return StandardResponse.success(data=status)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{execution_id}/results", response_model=StandardResponse)
async def get_execution_results(
    execution_id: str,
    controller: ExecutionController = Depends(get_execution_controller),
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """
    Get the results of a workflow execution.
    
    Args:
        execution_id: The ID of the execution to get the results for
        
    Returns:
        StandardResponse: Response containing the execution results
    """
    try:
        results = controller.get_execution_results(execution_id)
        return StandardResponse.success(data=results)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
