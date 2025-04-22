from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from backend.app.services.auth_service import AuthService
from backend.app.models.user import User
from backend.app.models.workflow import (
    WorkflowRequest,
    WorkflowResponse,
    WorkflowExecutionResponse,
    WorkflowExecutionRequest,
    ExecutionMode,
    WorkflowExecutionState
)
from backend.app.controllers.workflow_controller import WorkflowController
from backend.app.models.responses import StandardResponse

router = APIRouter()

@router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(workflow: WorkflowRequest, current_user: User = Depends(AuthService().get_current_active_user)):
    """Create a new workflow."""
    result = WorkflowController.create_workflow(workflow)
    return result

@router.get("/workflows", response_model=List[WorkflowResponse])
async def get_all_workflows(current_user: User = Depends(AuthService().get_current_active_user)):
    """Get all workflows."""
    return WorkflowController.get_all_workflows()

@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, current_user: User = Depends(AuthService().get_current_active_user)):
    """Get a workflow by ID."""
    workflow = WorkflowController.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: str, workflow: WorkflowRequest, current_user: User = Depends(AuthService().get_current_active_user)):
    """Update a workflow."""
    result = WorkflowController.update_workflow(workflow_id, workflow)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return result

@router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(workflow_id: str, current_user: User = Depends(AuthService().get_current_active_user)):
    """Delete a workflow."""
    success = WorkflowController.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return None

@router.post("/workflows/validate")
async def validate_workflow(workflow: WorkflowRequest, current_user: User = Depends(AuthService().get_current_active_user)):
    """Validate a workflow without executing it."""
    try:
        validation_errors = WorkflowController.validate_workflow(workflow)
        return {
            "status": "success" if not validation_errors else "error",
            "errors": validation_errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflows/execute")
async def execute_workflow(workflow: WorkflowRequest, background_tasks: BackgroundTasks, current_user: User = Depends(AuthService().get_current_active_user)):
    """Execute a workflow."""
    try:
        # Execute workflow synchronously
        result = WorkflowController.execute_workflow(workflow)
        return StandardResponse.success(data=result)
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.post("/workflows/execute-advanced")
async def execute_workflow_advanced(execution_request: WorkflowExecutionRequest, background_tasks: BackgroundTasks, current_user: User = Depends(AuthService().get_current_active_user)):
    """Execute a workflow with advanced options."""
    try:
        # Execute workflow with advanced options
        result = WorkflowController.execute_workflow(execution_request)
        return StandardResponse.success(data=result)
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.post("/workflows/execute-async")
async def execute_workflow_async(workflow: WorkflowRequest, current_user: User = Depends(AuthService().get_current_active_user)):
    """Execute a workflow asynchronously."""
    try:
        # Execute workflow asynchronously
        result = await WorkflowController.execute_workflow_async(workflow)
        return StandardResponse.success(data=result)
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.post("/workflows/execute-async-advanced")
async def execute_workflow_async_advanced(execution_request: WorkflowExecutionRequest, current_user: User = Depends(AuthService().get_current_active_user)):
    """Execute a workflow asynchronously with advanced options."""
    try:
        # Execute workflow asynchronously with advanced options
        result = await WorkflowController.execute_workflow_async(execution_request)
        return StandardResponse.success(data=result)
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.get("/workflows/execution/{execution_id}")
async def get_execution_status(execution_id: str, current_user: User = Depends(AuthService().get_current_active_user)):
    """Get the status of a workflow execution."""
    execution_status = WorkflowController.get_execution_status(execution_id)
    if not execution_status:
        return StandardResponse.error(message="Execution not found", errors=[{
            "code": "NOT_FOUND",
            "message": f"Execution with ID {execution_id} not found"
        }])
    return StandardResponse.success(data=execution_status)

@router.get("/workflows/execution/{execution_id}/state")
async def get_execution_state(execution_id: str, current_user: User = Depends(AuthService().get_current_active_user)):
    """Get the state of a workflow execution."""
    execution_state = WorkflowController.get_execution_state(execution_id)
    if not execution_state:
        return StandardResponse.error(message="Execution state not found", errors=[{
            "code": "NOT_FOUND",
            "message": f"Execution state with ID {execution_id} not found"
        }])
    # Convert to dict using model_dump if available, otherwise fall back to dict
    try:
        state_dict = execution_state.model_dump()
    except AttributeError:
        state_dict = execution_state.dict()
    return StandardResponse.success(data=state_dict)

@router.post("/workflows/execution/{execution_id}/stop")
async def stop_execution(execution_id: str, current_user: User = Depends(AuthService().get_current_active_user)):
    """Stop a workflow execution."""
    # Check if execution is active
    is_active = WorkflowController.is_execution_active(execution_id)
    if not is_active:
        execution_status = WorkflowController.get_execution_status(execution_id)
        if not execution_status:
            return StandardResponse.error(message="Execution not found", errors=[{
                "code": "NOT_FOUND",
                "message": f"Execution with ID {execution_id} not found"
            }])
        else:
            return StandardResponse.error(message="Execution is not active", errors=[{
                "code": "EXECUTION_INACTIVE",
                "message": f"Execution with ID {execution_id} is not active"
            }])

    # Stop execution
    success = WorkflowController.stop_execution(execution_id)
    if not success:
        return StandardResponse.error(message="Failed to stop execution")

    return StandardResponse.success(message="Execution stopped")

@router.post("/workflows/execution/{execution_id}/resume")
async def resume_execution(execution_id: str, resume_from_node: Optional[str] = None, current_user: User = Depends(AuthService().get_current_active_user)):
    """Resume a workflow execution from a specific node."""
    # Check if execution exists
    execution_status = WorkflowController.get_execution_status(execution_id)
    if not execution_status:
        return StandardResponse.error(message="Execution not found", errors=[{
            "code": "NOT_FOUND",
            "message": f"Execution with ID {execution_id} not found"
        }])

    # Check if execution is active
    is_active = WorkflowController.is_execution_active(execution_id)
    if is_active:
        return StandardResponse.error(message="Execution is already active", errors=[{
            "code": "EXECUTION_ACTIVE",
            "message": f"Execution with ID {execution_id} is already active"
        }])

    # Get the workflow from the execution result
    workflow_data = execution_status.get("workflow", {})
    if not workflow_data:
        return StandardResponse.error(message="Workflow data not found in execution result", errors=[{
            "code": "WORKFLOW_NOT_FOUND",
            "message": f"Workflow data not found in execution with ID {execution_id}"
        }])

    # Create execution request
    execution_request = WorkflowExecutionRequest(
        workflow=WorkflowRequest(**workflow_data),
        execution_mode=ExecutionMode.RESUME,
        resume_from_node=resume_from_node,
        previous_execution_id=execution_id
    )

    try:
        # Execute workflow with resume options
        result = WorkflowController.execute_workflow(execution_request)
        return StandardResponse.success(data=result)
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.get("/workflows/execution/{execution_id}/active")
async def is_execution_active(execution_id: str, current_user: User = Depends(AuthService().get_current_active_user)):
    """Check if a workflow execution is active."""
    is_active = WorkflowController.is_execution_active(execution_id)
    return StandardResponse.success(data={"active": is_active})
