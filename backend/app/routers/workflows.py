"""
Workflows Router

This module provides API endpoints for workflows.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, List, Any, Optional

from backend.app.models.responses import StandardResponse
from backend.app.models.workflow import (
    WorkflowRequest,
    WorkflowResponse,
    WorkflowExecutionResponse,
    WorkflowExecutionRequest,
    ExecutionMode,
    WorkflowExecutionState
)
from backend.app.controllers.workflow_controller import WorkflowController
from backend.app.services.auth_service import AuthService
from backend.app.models.user import User
from backend.app.exceptions import NotFoundError, ValidationError

# Create router with API versioning
router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])

@router.post("/", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow: WorkflowRequest,
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """
    Create a new workflow.
    
    Args:
        workflow: The workflow to create
        
    Returns:
        StandardResponse: Response containing the created workflow
    """
    try:
        result = WorkflowController.create_workflow(workflow)
        return StandardResponse.success(
            message="Workflow created successfully",
            data=result
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=StandardResponse)
async def get_all_workflows(
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """
    Get all workflows.
    
    Returns:
        StandardResponse: Response containing all workflows
    """
    try:
        workflows = WorkflowController.get_all_workflows()
        return StandardResponse.success(data=workflows)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{workflow_id}", response_model=StandardResponse)
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """
    Get a specific workflow by ID.
    
    Args:
        workflow_id: The ID of the workflow to get
        
    Returns:
        StandardResponse: Response containing the specified workflow
    """
    try:
        workflow = WorkflowController.get_workflow(workflow_id)
        return StandardResponse.success(data=workflow)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{workflow_id}", response_model=StandardResponse)
async def update_workflow(
    workflow_id: str,
    workflow: WorkflowRequest,
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """
    Update a workflow.
    
    Args:
        workflow_id: The ID of the workflow to update
        workflow: The updated workflow
        
    Returns:
        StandardResponse: Response containing the updated workflow
    """
    try:
        result = WorkflowController.update_workflow(workflow_id, workflow)
        return StandardResponse.success(
            message="Workflow updated successfully",
            data=result
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{workflow_id}", response_model=StandardResponse)
async def delete_workflow(
    workflow_id: str,
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """
    Delete a workflow.
    
    Args:
        workflow_id: The ID of the workflow to delete
        
    Returns:
        StandardResponse: Response indicating success or failure
    """
    try:
        WorkflowController.delete_workflow(workflow_id)
        return StandardResponse.success(message="Workflow deleted successfully")
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
