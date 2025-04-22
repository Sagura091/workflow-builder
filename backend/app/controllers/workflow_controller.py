import uuid
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from backend.app.models.workflow import (
    WorkflowRequest,
    WorkflowResponse,
    ExecutionResult,
    WorkflowExecutionRequest,
    ExecutionMode,
    WorkflowExecutionState
)
from backend.app.models.node import Node
from backend.app.models.connection import Edge, Connection, ConnectionPoint
from backend.app.services.workflow_executor import WorkflowExecutor
from backend.app.services.validation import ValidationService
from backend.app.exceptions import WorkflowExecutionError, NodeExecutionError

# Configure logger
logger = logging.getLogger("workflow_builder")

class WorkflowController:
    """Controller for workflow operations."""

    # In-memory storage for workflows (in a real app, this would be a database)
    _workflows: Dict[str, WorkflowResponse] = {}

    # Workflow executor instance
    _executor = WorkflowExecutor()

    @staticmethod
    def create_workflow(workflow: WorkflowRequest) -> WorkflowResponse:
        """Create a new workflow."""
        workflow_id = str(uuid.uuid4())

        # Convert edges to connections
        connections = []
        for edge in workflow.edges:
            connection_id = f"conn-{edge.source}-{edge.target}"
            connections.append(Connection(
                id=connection_id,
                from_point=ConnectionPoint(nodeId=edge.source, port=edge.source_port or "output"),
                to_point=ConnectionPoint(nodeId=edge.target, port=edge.target_port or "input")
            ))

        # Create workflow response
        workflow_response = WorkflowResponse(
            id=workflow_id,
            name=workflow.name or "Untitled Workflow",
            nodes=workflow.nodes,
            connections=connections
        )

        # Save workflow
        WorkflowController._workflows[workflow_id] = workflow_response

        return workflow_response

    @staticmethod
    def get_workflow(workflow_id: str) -> Optional[WorkflowResponse]:
        """Get a workflow by ID."""
        return WorkflowController._workflows.get(workflow_id)

    @staticmethod
    def get_all_workflows() -> List[WorkflowResponse]:
        """Get all workflows."""
        return list(WorkflowController._workflows.values())

    @staticmethod
    def update_workflow(workflow_id: str, workflow: WorkflowRequest) -> Optional[WorkflowResponse]:
        """Update an existing workflow."""
        if workflow_id not in WorkflowController._workflows:
            return None

        # Convert edges to connections
        connections = []
        for edge in workflow.edges:
            connection_id = f"conn-{edge.source}-{edge.target}"
            connections.append(Connection(
                id=connection_id,
                from_point=ConnectionPoint(nodeId=edge.source, port=edge.source_port or "output"),
                to_point=ConnectionPoint(nodeId=edge.target, port=edge.target_port or "input")
            ))

        # Update workflow
        workflow_response = WorkflowResponse(
            id=workflow_id,
            name=workflow.name or WorkflowController._workflows[workflow_id].name,
            nodes=workflow.nodes,
            connections=connections
        )

        WorkflowController._workflows[workflow_id] = workflow_response

        return workflow_response

    @staticmethod
    def delete_workflow(workflow_id: str) -> bool:
        """Delete a workflow."""
        if workflow_id not in WorkflowController._workflows:
            return False

        del WorkflowController._workflows[workflow_id]
        return True

    @staticmethod
    def validate_workflow(workflow: WorkflowRequest) -> List[Dict[str, Any]]:
        """Validate a workflow without executing it."""
        # Create validation service
        validation_service = ValidationService()

        # Validate workflow connections
        # Convert models to dictionaries
        node_dicts = []
        edge_dicts = []

        for node in workflow.nodes:
            try:
                # Try model_dump first (newer Pydantic versions)
                node_dicts.append(node.model_dump())
            except AttributeError:
                # Fall back to dict for older Pydantic versions
                node_dicts.append(node.dict())

        for edge in workflow.edges:
            try:
                # Try model_dump first (newer Pydantic versions)
                edge_dicts.append(edge.model_dump())
            except AttributeError:
                # Fall back to dict for older Pydantic versions
                edge_dicts.append(edge.dict())

        # Validate connections
        errors = validation_service.validate_workflow_connections(node_dicts, edge_dicts)

        # Validate node configurations
        executor = WorkflowExecutor()
        node_validation_errors = executor.validate_workflow(workflow.nodes, workflow.edges)

        # Combine errors
        errors.extend(node_validation_errors)

        return errors

    @staticmethod
    def execute_workflow(workflow_request: Union[WorkflowRequest, WorkflowExecutionRequest]) -> Dict[str, Any]:
        """Execute a workflow synchronously."""
        # Generate execution ID
        execution_id = str(uuid.uuid4())

        # Handle different request types
        if isinstance(workflow_request, WorkflowExecutionRequest):
            # Extract workflow and execution options
            workflow = workflow_request.workflow
            execution_mode = workflow_request.execution_mode
            selected_nodes = workflow_request.selected_nodes
            resume_from_node = workflow_request.resume_from_node
            previous_execution_id = workflow_request.previous_execution_id
            execution_options = workflow_request.execution_options
        else:
            # Default to full execution
            workflow = workflow_request
            execution_mode = ExecutionMode.FULL
            selected_nodes = None
            resume_from_node = None
            previous_execution_id = None
            execution_options = {}

        try:
            # Execute workflow with options
            result = WorkflowController._executor.execute(
                nodes=workflow.nodes,
                edges=workflow.edges,
                execution_id=execution_id,
                execution_mode=execution_mode,
                selected_nodes=selected_nodes,
                resume_from_node=resume_from_node,
                previous_execution_id=previous_execution_id,
                execution_options=execution_options
            )

            return {
                "status": "success",
                "execution_id": execution_id,
                "results": result
            }
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")

            # Get execution result from cache (will contain error details)
            error_result = WorkflowController._executor.get_execution_result(execution_id)

            return {
                "status": "error",
                "execution_id": execution_id,
                "error": str(e),
                "details": error_result
            }

    @staticmethod
    async def execute_workflow_async(workflow_request: Union[WorkflowRequest, WorkflowExecutionRequest]) -> Dict[str, Any]:
        """Execute a workflow asynchronously."""
        # Generate execution ID
        execution_id = str(uuid.uuid4())

        # Handle different request types
        if isinstance(workflow_request, WorkflowExecutionRequest):
            # Extract workflow and execution options
            workflow = workflow_request.workflow
            execution_mode = workflow_request.execution_mode
            selected_nodes = workflow_request.selected_nodes
            resume_from_node = workflow_request.resume_from_node
            previous_execution_id = workflow_request.previous_execution_id
            execution_options = workflow_request.execution_options
        else:
            # Default to full execution
            workflow = workflow_request
            execution_mode = ExecutionMode.FULL
            selected_nodes = None
            resume_from_node = None
            previous_execution_id = None
            execution_options = {}

        try:
            # Execute workflow asynchronously with options
            result = await WorkflowController._executor.execute_async(
                nodes=workflow.nodes,
                edges=workflow.edges,
                execution_id=execution_id,
                execution_mode=execution_mode,
                selected_nodes=selected_nodes,
                resume_from_node=resume_from_node,
                previous_execution_id=previous_execution_id,
                execution_options=execution_options
            )

            return {
                "status": "success",
                "execution_id": execution_id,
                "results": result
            }
        except Exception as e:
            logger.error(f"Error executing workflow asynchronously: {str(e)}")

            # Get execution result from cache (will contain error details)
            error_result = WorkflowController._executor.get_execution_result(execution_id)

            return {
                "status": "error",
                "execution_id": execution_id,
                "error": str(e),
                "details": error_result
            }

    @staticmethod
    def get_execution_status(execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow execution."""
        return WorkflowController._executor.get_execution_result(execution_id)

    @staticmethod
    def get_execution_state(execution_id: str) -> Optional[WorkflowExecutionState]:
        """Get the state of a workflow execution."""
        return WorkflowController._executor.get_execution_state(execution_id)

    @staticmethod
    def is_execution_active(execution_id: str) -> bool:
        """Check if a workflow execution is active."""
        return WorkflowController._executor.is_execution_active(execution_id)

    @staticmethod
    def stop_execution(execution_id: str) -> bool:
        """Stop a workflow execution."""
        # Check if execution exists and is active
        if not WorkflowController._executor.is_execution_active(execution_id):
            return False

        # In a real implementation, this would actually stop the execution
        # For now, we just mark it as stopped in the cache
        execution_result = WorkflowController._executor.get_execution_result(execution_id)
        if execution_result:
            execution_result["status"] = "stopped"
            return True

        return False
