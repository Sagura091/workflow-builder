"""
Execution Controller

This module provides a controller for workflow execution.
"""

from typing import Dict, List, Any, Optional
from fastapi import BackgroundTasks
import uuid
import datetime
import asyncio

class ExecutionController:
    """Controller for workflow execution."""
    
    def __init__(self):
        """Initialize the execution controller."""
        # In a real implementation, this would use a database
        self.executions = {}
    
    async def execute_workflow(self, workflow: Dict[str, Any], inputs: Dict[str, Any], 
                              background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow: The workflow to execute
            inputs: The inputs for the workflow
            background_tasks: FastAPI background tasks
            
        Returns:
            Execution result or execution ID for async execution
        """
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Create execution record
        execution = {
            "id": execution_id,
            "workflow_id": workflow.get("id", "unknown"),
            "status": "pending",
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": None,
            "inputs": inputs,
            "results": {},
            "logs": []
        }
        
        # Store execution
        self.executions[execution_id] = execution
        
        # Add execution to background tasks
        background_tasks.add_task(self._execute_workflow_async, execution_id, workflow, inputs)
        
        return {
            "execution_id": execution_id,
            "status": "pending"
        }
    
    async def _execute_workflow_async(self, execution_id: str, workflow: Dict[str, Any], 
                                     inputs: Dict[str, Any]) -> None:
        """
        Execute a workflow asynchronously.
        
        Args:
            execution_id: The ID of the execution
            workflow: The workflow to execute
            inputs: The inputs for the workflow
        """
        try:
            # Update status to running
            self.executions[execution_id]["status"] = "running"
            
            # Simulate workflow execution
            await asyncio.sleep(2)
            
            # Update execution record
            self.executions[execution_id].update({
                "status": "completed",
                "end_time": datetime.datetime.now().isoformat(),
                "results": {"message": "Workflow executed successfully"},
                "logs": ["Workflow execution started", "Workflow execution completed"]
            })
        except Exception as e:
            # Update execution record with error
            self.executions[execution_id].update({
                "status": "failed",
                "end_time": datetime.datetime.now().isoformat(),
                "error": str(e),
                "logs": ["Workflow execution started", f"Workflow execution failed: {str(e)}"]
            })
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow execution.
        
        Args:
            execution_id: The ID of the execution
            
        Returns:
            Execution status
        """
        return self.executions.get(execution_id)
    
    async def get_executions(self, workflow_id: Optional[str] = None, 
                           status: Optional[str] = None, 
                           limit: int = 100, 
                           offset: int = 0) -> List[Dict[str, Any]]:
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
        # Filter executions
        filtered_executions = self.executions.values()
        
        if workflow_id:
            filtered_executions = [e for e in filtered_executions if e.get("workflow_id") == workflow_id]
        
        if status:
            filtered_executions = [e for e in filtered_executions if e.get("status") == status]
        
        # Sort by start time (newest first)
        sorted_executions = sorted(
            filtered_executions, 
            key=lambda e: e.get("start_time", ""), 
            reverse=True
        )
        
        # Apply pagination
        paginated_executions = sorted_executions[offset:offset + limit]
        
        return paginated_executions
