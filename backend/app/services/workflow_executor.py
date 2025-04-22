import networkx as nx
from typing import List, Dict, Any, Optional, Callable, Tuple, Set
import datetime
import uuid
import logging
import asyncio
import traceback
import time

from backend.app.models.node import Node
from backend.app.models.connection import Edge
from backend.app.models.workflow import (
    ExecutionMode,
    ExecutionStatus,
    NodeExecutionStatus,
    NodeExecutionResult,
    WorkflowExecutionState
)
from backend.app.services.plugin_loader import PluginLoader
from backend.app.services.validation import ValidationService
from backend.app.services.websocket_manager import WebSocketManager
from backend.app.services.node_cache_service import NodeCacheService
from backend.app.exceptions import (
    WorkflowExecutionError,
    NodeExecutionError,
    NodeConnectionError,
    TypeSystemError
)

# Configure logger
logger = logging.getLogger("workflow_builder")

class WorkflowExecutor:
    """Service for executing workflows."""

    def __init__(self):
        """Initialize the workflow executor."""
        self.plugin_loader = PluginLoader()
        self.validation_service = ValidationService()
        self.websocket_manager = WebSocketManager()
        self.node_cache = NodeCacheService()

        # Execution cache
        self.execution_cache: Dict[str, Dict[str, Any]] = {}

        # Execution state tracking
        self.execution_states: Dict[str, WorkflowExecutionState] = {}

        # Active executions
        self.active_executions: Set[str] = set()

        # Execution options
        self.use_node_cache = True
        self.cache_ttl = 3600  # 1 hour in seconds

    def build_graph(self, nodes: List[Node], edges: List[Edge]) -> nx.DiGraph:
        """Build a directed graph from nodes and edges."""
        G = nx.DiGraph()

        # Add nodes
        for node in nodes:
            G.add_node(node.id, type=node.type, config=node.config)

        # Add edges
        for edge in edges:
            G.add_edge(edge.source, edge.target)

        return G

    def topological_sort(self, G: nx.DiGraph) -> List[str]:
        """Perform a topological sort on the graph."""
        try:
            return list(nx.topological_sort(G))
        except nx.NetworkXUnfeasible:
            raise ValueError("Workflow contains cycles and cannot be executed")

    def validate_workflow(self, nodes: List[Node], edges: List[Edge]) -> List[Dict[str, Any]]:
        """Validate the workflow before execution.

        Returns:
            List[Dict[str, Any]]: List of validation errors
        """
        errors = []

        # Build node map for quick lookup
        node_map = {node.id: node for node in nodes}

        # Check that all nodes exist
        for edge in edges:
            if edge.source not in node_map:
                errors.append({
                    "type": "connection",
                    "id": f"{edge.source}-{edge.target}",
                    "message": f"Node {edge.source} referenced in edge does not exist"
                })
                continue

            if edge.target not in node_map:
                errors.append({
                    "type": "connection",
                    "id": f"{edge.source}-{edge.target}",
                    "message": f"Node {edge.target} referenced in edge does not exist"
                })
                continue

        # Validate connections between nodes
        for edge in edges:
            # Skip if nodes don't exist
            if edge.source not in node_map or edge.target not in node_map:
                continue

            source_node = node_map[edge.source]
            target_node = node_map[edge.target]

            # Load plugins
            source_plugin = self.plugin_loader.load_plugin(source_node.type)
            target_plugin = self.plugin_loader.load_plugin(target_node.type)

            if not source_plugin or not hasattr(source_plugin, "__plugin_meta__"):
                errors.append({
                    "type": "node",
                    "id": source_node.id,
                    "message": f"Invalid source plugin: {source_node.type}"
                })
                continue

            if not target_plugin or not hasattr(target_plugin, "__plugin_meta__"):
                errors.append({
                    "type": "node",
                    "id": target_node.id,
                    "message": f"Invalid target plugin: {target_node.type}"
                })
                continue

            # Get plugin metadata
            source_meta = source_plugin.__plugin_meta__
            target_meta = target_plugin.__plugin_meta__

            # Validate connection types
            source_outputs = source_meta.get("outputs", {})
            target_inputs = target_meta.get("inputs", {})

            # Check if plugins have inputs/outputs
            if not source_outputs:
                errors.append({
                    "type": "node",
                    "id": source_node.id,
                    "message": f"Node {source_node.id} has no outputs"
                })
                continue

            if not target_inputs:
                errors.append({
                    "type": "node",
                    "id": target_node.id,
                    "message": f"Node {target_node.id} has no inputs"
                })
                continue

            # Get port types (in a real implementation, you would use the specific ports from the edge)
            # For now, we'll use the first output and input
            source_port = edge.source_port or list(source_outputs.keys())[0]
            target_port = edge.target_port or list(target_inputs.keys())[0]

            source_type = source_outputs.get(source_port, "any")
            target_type = target_inputs.get(target_port, "any")

            # Validate connection using type rules
            is_valid, error_message = self.validation_service.validate_connection(source_type, target_type)

            if not is_valid:
                errors.append({
                    "type": "connection",
                    "id": f"{edge.source}-{edge.target}",
                    "message": error_message
                })

        return errors

    def execute(self, nodes: List[Node], edges: List[Edge], execution_id: Optional[str] = None,
               execution_mode: ExecutionMode = ExecutionMode.FULL,
               selected_nodes: Optional[List[str]] = None,
               resume_from_node: Optional[str] = None,
               previous_execution_id: Optional[str] = None,
               execution_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a workflow synchronously.

        Args:
            nodes: List of nodes in the workflow
            edges: List of edges in the workflow
            execution_id: Optional execution ID (generated if not provided)
            execution_mode: Mode of execution (full, partial, resume)
            selected_nodes: List of node IDs to execute in partial mode
            resume_from_node: Node ID to resume from in resume mode
            previous_execution_id: ID of previous execution to resume from
            execution_options: Additional execution options

        Returns:
            Execution result
        """
        # Generate execution ID if not provided
        if not execution_id:
            execution_id = str(uuid.uuid4())

        # Initialize execution options
        if execution_options is None:
            execution_options = {}

        # Apply execution options
        use_cache = execution_options.get("use_cache", self.use_node_cache)
        cache_ttl = execution_options.get("cache_ttl", self.cache_ttl)

        # Add to active executions
        self.active_executions.add(execution_id)

        # Create execution state
        workflow_id = execution_options.get("workflow_id", str(uuid.uuid4()))
        execution_state = WorkflowExecutionState(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=ExecutionStatus.RUNNING,
            execution_mode=execution_mode,
            selected_nodes=selected_nodes or [],
            resume_from_node=resume_from_node,
            previous_execution_id=previous_execution_id
        )
        self.execution_states[execution_id] = execution_state

        try:
            # Validate workflow
            validation_errors = self.validate_workflow(nodes, edges)

            # If there are validation errors, raise an exception
            if validation_errors:
                error_messages = [error["message"] for error in validation_errors]
                error_message = f"Workflow validation failed: {'; '.join(error_messages)}"
                raise WorkflowExecutionError(detail=error_message, context={"errors": validation_errors})

            # Build graph and get execution order
            G = self.build_graph(nodes, edges)
            full_execution_order = self.topological_sort(G)

            # Determine which nodes to execute based on execution mode
            execution_order = self._get_execution_order(
                full_execution_order=full_execution_order,
                execution_mode=execution_mode,
                selected_nodes=selected_nodes,
                resume_from_node=resume_from_node,
                previous_execution_id=previous_execution_id,
                G=G
            )

            # Update execution state with node statuses
            for node_id in full_execution_order:
                if node_id in execution_order:
                    execution_state.node_statuses[node_id] = NodeExecutionStatus.PENDING
                else:
                    execution_state.node_statuses[node_id] = NodeExecutionStatus.SKIPPED
                    execution_state.skipped_nodes.append(node_id)

            # Build node map for quick lookup
            node_map = {node.id: node for node in nodes}

            # Initialize node results
            node_results: Dict[str, NodeExecutionResult] = {}

            # Execute nodes in order
            results = {}
            logs = []

            for node_id in execution_order:
                # Skip nodes that are not in the execution order
                if node_id not in execution_order:
                    continue

                # Update execution state
                execution_state.current_node = node_id
                execution_state.node_statuses[node_id] = NodeExecutionStatus.RUNNING

                # Get the node
                node = node_map[node_id]

                # Load plugin
                plugin = self.plugin_loader.load_plugin(node.type)

                if not plugin or not hasattr(plugin, "run"):
                    raise NodeExecutionError(
                        detail=f"Plugin {node.type} does not have a run method",
                        node_id=node_id,
                        node_type=node.type
                    )

                # Gather inputs from upstream nodes
                inputs = {}
                for edge in edges:
                    if edge.target == node_id:
                        source_node = node_map[edge.source]
                        source_plugin = self.plugin_loader.load_plugin(source_node.type)

                        # Get source plugin metadata
                        source_meta = source_plugin.__plugin_meta__
                        source_outputs = source_meta.get("outputs", {})

                        # Get port names
                        source_port = edge.source_port or list(source_outputs.keys())[0]
                        target_port = edge.target_port or list(source_outputs.keys())[0]

                        # Get the output from the source node
                        source_result = results.get(edge.source, {})

                        # Map the output to the input port
                        if source_port in source_result:
                            inputs[target_port] = source_result[source_port]
                        else:
                            # If the specific port isn't found, use the entire result
                            inputs.update(source_result)

                # Execute plugin
                try:
                    # Record start time
                    start_time = datetime.datetime.now()
                    start_time_str = start_time.isoformat()

                    # Log node execution start
                    node_start_log = {
                        "node": node_id,
                        "status": "started",
                        "timestamp": start_time_str,
                        "node_type": node.type
                    }
                    logs.append(node_start_log)

                    # Send real-time update
                    asyncio.create_task(self.websocket_manager.broadcast_execution_update(
                        execution_id=execution_id,
                        update_type="node_started",
                        data={
                            "node_id": node_id,
                            "node_type": node.type,
                            "timestamp": start_time_str
                        }
                    ))

                    # Check if result is in cache
                    cache_key = None
                    result = None
                    used_cache = False

                    if self.use_node_cache and self.node_cache.is_node_cacheable(node.type):
                        # Generate cache key
                        cache_key = self.node_cache.generate_cache_key(
                            node_type=node.type,
                            node_id=node_id,
                            inputs=inputs,
                            config=node.config
                        )

                        # Try to get from cache
                        result = self.node_cache.get(cache_key)
                        used_cache = result is not None

                    # If not in cache, execute the node
                    if result is None:
                        # Run the plugin
                        result = plugin.run(inputs, node.config)

                        # Cache the result if caching is enabled
                        if self.use_node_cache and cache_key and self.node_cache.is_node_cacheable(node.type):
                            self.node_cache.set(cache_key, result, self.cache_ttl)

                    # Record end time
                    end_time = datetime.datetime.now()
                    execution_time_ms = (end_time - start_time).total_seconds() * 1000

                    # Add cache info to result
                    if used_cache:
                        result["_cache_hit"] = True

                    # Store result
                    results[node_id] = result

                    # Create node execution result
                    node_result = NodeExecutionResult(
                        node_id=node_id,
                        node_type=node.type,
                        status=NodeExecutionStatus.COMPLETED if not used_cache else NodeExecutionStatus.CACHED,
                        outputs=result,
                        execution_time_ms=execution_time_ms,
                        start_time=start_time_str,
                        end_time=end_time.isoformat(),
                        cached=used_cache
                    )
                    node_results[node_id] = node_result

                    # Update execution state
                    execution_state.node_statuses[node_id] = NodeExecutionStatus.COMPLETED if not used_cache else NodeExecutionStatus.CACHED
                    execution_state.completed_nodes.append(node_id)

                    # Add to logs
                    node_complete_log = {
                        "node": node_id,
                        "status": "completed",
                        "value": result.get("logged") or result.get("display") or "Execution completed",
                        "timestamp": end_time.isoformat(),
                        "execution_time_ms": execution_time_ms,
                        "cached": used_cache
                    }
                    logs.append(node_complete_log)

                    # Send real-time update
                    asyncio.create_task(self.websocket_manager.broadcast_execution_update(
                        execution_id=execution_id,
                        update_type="node_completed",
                        data={
                            "node_id": node_id,
                            "node_type": node.type,
                            "timestamp": end_time.isoformat(),
                            "execution_time_ms": execution_time_ms,
                            "result": result.get("logged") or result.get("display"),
                            "cached": used_cache
                        }
                    ))

                except Exception as e:
                    # Get error details
                    error_time = datetime.datetime.now()
                    error_message = str(e)
                    error_traceback = traceback.format_exc()

                    # Log error
                    node_error_log = {
                        "node": node_id,
                        "status": "error",
                        "value": f"Error: {error_message}",
                        "timestamp": error_time.isoformat(),
                        "traceback": error_traceback
                    }
                    logs.append(node_error_log)

                    # Send real-time update
                    asyncio.create_task(self.websocket_manager.broadcast_execution_update(
                        execution_id=execution_id,
                        update_type="node_error",
                        data={
                            "node_id": node_id,
                            "node_type": node.type,
                            "timestamp": error_time.isoformat(),
                            "error": error_message,
                            "traceback": error_traceback
                        }
                    ))

                    # Create node execution result for failed node
                    node_result = NodeExecutionResult(
                        node_id=node_id,
                        node_type=node.type,
                        status=NodeExecutionStatus.FAILED,
                        outputs={},
                        execution_time_ms=(datetime.datetime.now() - start_time).total_seconds() * 1000,
                        start_time=start_time_str,
                        end_time=datetime.datetime.now().isoformat(),
                        error=error_message
                    )
                    node_results[node_id] = node_result

                    # Update execution state
                    execution_state.node_statuses[node_id] = NodeExecutionStatus.FAILED
                    execution_state.failed_nodes.append(node_id)

                    # Raise a more detailed error
                    raise NodeExecutionError(
                        detail=f"Error executing node {node_id}: {error_message}",
                        node_id=node_id,
                        node_type=node.type,
                        inputs=inputs
                    )

            # Update execution state
            execution_state.status = ExecutionStatus.COMPLETED
            execution_state.end_time = datetime.datetime.now().isoformat()
            execution_state.execution_time_ms = self._calculate_total_execution_time(logs)

            # Execution completed successfully
            execution_result = {
                "execution_id": execution_id,
                "status": ExecutionStatus.COMPLETED,
                "node_outputs": results,
                "node_results": node_results,
                "log": logs,
                "start_time": logs[0]["timestamp"] if logs else datetime.datetime.now().isoformat(),
                "end_time": datetime.datetime.now().isoformat(),
                "execution_time_ms": execution_state.execution_time_ms
            }

            # Cache the result
            self.execution_cache[execution_id] = execution_result

            # Send completion update
            asyncio.create_task(self.websocket_manager.broadcast_execution_update(
                execution_id=execution_id,
                update_type="execution_completed",
                data={
                    "execution_id": execution_id,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "node_count": len(nodes),
                    "execution_time_ms": self._calculate_total_execution_time(logs)
                }
            ))

            return execution_result

        except Exception as e:
            # Log the error
            error_time = datetime.datetime.now().isoformat()
            error_message = str(e)
            error_traceback = traceback.format_exc()

            logger.error(f"Workflow execution error: {error_message}\n{error_traceback}")

            # Update execution state
            execution_state.status = ExecutionStatus.FAILED
            execution_state.end_time = datetime.datetime.now().isoformat()
            execution_state.execution_time_ms = self._calculate_total_execution_time(logs)

            # Create error result
            error_result = {
                "execution_id": execution_id,
                "status": ExecutionStatus.FAILED,
                "node_outputs": results,
                "node_results": node_results,
                "log": logs,
                "error": error_message,
                "traceback": error_traceback,
                "timestamp": error_time,
                "execution_time_ms": execution_state.execution_time_ms
            }

            # Cache the error result
            self.execution_cache[execution_id] = error_result

            # Send error update
            asyncio.create_task(self.websocket_manager.broadcast_execution_update(
                execution_id=execution_id,
                update_type="execution_error",
                data={
                    "execution_id": execution_id,
                    "timestamp": error_time,
                    "error": error_message,
                    "traceback": error_traceback
                }
            ))

            # Re-raise the exception
            raise

        finally:
            # Remove from active executions
            self.active_executions.discard(execution_id)

            # Keep execution state for future reference

    async def execute_async(self, nodes: List[Node], edges: List[Edge], execution_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a workflow asynchronously."""
        # Generate execution ID if not provided
        if not execution_id:
            execution_id = str(uuid.uuid4())

        # Add to active executions
        self.active_executions.add(execution_id)

        try:
            # Validate workflow
            validation_errors = self.validate_workflow(nodes, edges)

            # If there are validation errors, raise an exception
            if validation_errors:
                error_messages = [error["message"] for error in validation_errors]
                error_message = f"Workflow validation failed: {'; '.join(error_messages)}"
                raise WorkflowExecutionError(detail=error_message, context={"errors": validation_errors})

            # Build graph and get execution order
            G = self.build_graph(nodes, edges)
            execution_order = self.topological_sort(G)

            # Build node map for quick lookup
            node_map = {node.id: node for node in nodes}

            # Execute nodes in order
            results = {}
            logs = []

            for node_id in execution_order:
                node = node_map[node_id]

                # Load plugin
                plugin = self.plugin_loader.load_plugin(node.type)

                if not plugin or not hasattr(plugin, "run"):
                    raise NodeExecutionError(
                        detail=f"Plugin {node.type} does not have a run method",
                        node_id=node_id,
                        node_type=node.type
                    )

                # Gather inputs from upstream nodes
                inputs = {}
                for edge in edges:
                    if edge.target == node_id:
                        source_node = node_map[edge.source]
                        source_plugin = self.plugin_loader.load_plugin(source_node.type)

                        # Get source plugin metadata
                        source_meta = source_plugin.__plugin_meta__
                        source_outputs = source_meta.get("outputs", {})

                        # Get port names
                        source_port = edge.source_port or list(source_outputs.keys())[0]
                        target_port = edge.target_port or list(source_outputs.keys())[0]

                        # Get the output from the source node
                        source_result = results.get(edge.source, {})

                        # Map the output to the input port
                        if source_port in source_result:
                            inputs[target_port] = source_result[source_port]
                        else:
                            # If the specific port isn't found, use the entire result
                            inputs.update(source_result)

                # Execute plugin
                try:
                    # Record start time
                    start_time = datetime.datetime.now()
                    start_time_str = start_time.isoformat()

                    # Log node execution start
                    node_start_log = {
                        "node": node_id,
                        "status": "started",
                        "timestamp": start_time_str,
                        "node_type": node.type
                    }
                    logs.append(node_start_log)

                    # Send real-time update
                    await self.websocket_manager.broadcast_execution_update(
                        execution_id=execution_id,
                        update_type="node_started",
                        data={
                            "node_id": node_id,
                            "node_type": node.type,
                            "timestamp": start_time_str
                        }
                    )

                    # Check if result is in cache
                    cache_key = None
                    result = None
                    used_cache = False

                    if self.use_node_cache and self.node_cache.is_node_cacheable(node.type):
                        # Generate cache key
                        cache_key = self.node_cache.generate_cache_key(
                            node_type=node.type,
                            node_id=node_id,
                            inputs=inputs,
                            config=node.config
                        )

                        # Try to get from cache
                        result = self.node_cache.get(cache_key)
                        used_cache = result is not None

                    # If not in cache, execute the node
                    if result is None:
                        # Run the plugin
                        result = plugin.run(inputs, node.config)

                        # Cache the result if caching is enabled
                        if self.use_node_cache and cache_key and self.node_cache.is_node_cacheable(node.type):
                            self.node_cache.set(cache_key, result, self.cache_ttl)

                    # Record end time
                    end_time = datetime.datetime.now()
                    execution_time_ms = (end_time - start_time).total_seconds() * 1000

                    # Add cache info to result
                    if used_cache:
                        result["_cache_hit"] = True

                    # Store result
                    results[node_id] = result

                    # Add to logs
                    node_complete_log = {
                        "node": node_id,
                        "status": "completed",
                        "value": result.get("logged") or result.get("display") or "Execution completed",
                        "timestamp": end_time.isoformat(),
                        "execution_time_ms": execution_time_ms,
                        "cached": used_cache
                    }
                    logs.append(node_complete_log)

                    # Send real-time update
                    await self.websocket_manager.broadcast_execution_update(
                        execution_id=execution_id,
                        update_type="node_completed",
                        data={
                            "node_id": node_id,
                            "node_type": node.type,
                            "timestamp": end_time.isoformat(),
                            "execution_time_ms": execution_time_ms,
                            "result": result.get("logged") or result.get("display"),
                            "cached": used_cache
                        }
                    )

                except Exception as e:
                    # Get error details
                    error_time = datetime.datetime.now()
                    error_message = str(e)
                    error_traceback = traceback.format_exc()

                    # Log error
                    node_error_log = {
                        "node": node_id,
                        "status": "error",
                        "value": f"Error: {error_message}",
                        "timestamp": error_time.isoformat(),
                        "traceback": error_traceback
                    }
                    logs.append(node_error_log)

                    # Send real-time update
                    await self.websocket_manager.broadcast_execution_update(
                        execution_id=execution_id,
                        update_type="node_error",
                        data={
                            "node_id": node_id,
                            "node_type": node.type,
                            "timestamp": error_time.isoformat(),
                            "error": error_message,
                            "traceback": error_traceback
                        }
                    )

                    # Raise a more detailed error
                    raise NodeExecutionError(
                        detail=f"Error executing node {node_id}: {error_message}",
                        node_id=node_id,
                        node_type=node.type,
                        inputs=inputs
                    )

            # Execution completed successfully
            execution_result = {
                "execution_id": execution_id,
                "status": "completed",
                "node_outputs": results,
                "log": logs,
                "start_time": logs[0]["timestamp"] if logs else datetime.datetime.now().isoformat(),
                "end_time": datetime.datetime.now().isoformat()
            }

            # Cache the result
            self.execution_cache[execution_id] = execution_result

            # Send completion update
            await self.websocket_manager.broadcast_execution_update(
                execution_id=execution_id,
                update_type="execution_completed",
                data={
                    "execution_id": execution_id,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "node_count": len(nodes),
                    "execution_time_ms": self._calculate_total_execution_time(logs)
                }
            )

            return execution_result

        except Exception as e:
            # Log the error
            error_time = datetime.datetime.now().isoformat()
            error_message = str(e)
            error_traceback = traceback.format_exc()

            logger.error(f"Workflow execution error: {error_message}\n{error_traceback}")

            # Create error result
            error_result = {
                "execution_id": execution_id,
                "status": "error",
                "error": error_message,
                "traceback": error_traceback,
                "timestamp": error_time
            }

            # Cache the error result
            self.execution_cache[execution_id] = error_result

            # Send error update
            await self.websocket_manager.broadcast_execution_update(
                execution_id=execution_id,
                update_type="execution_error",
                data={
                    "execution_id": execution_id,
                    "timestamp": error_time,
                    "error": error_message,
                    "traceback": error_traceback
                }
            )

            # Re-raise the exception
            raise

        finally:
            # Remove from active executions
            self.active_executions.discard(execution_id)

    def _get_execution_order(self, full_execution_order: List[str], execution_mode: ExecutionMode,
                           selected_nodes: Optional[List[str]] = None, resume_from_node: Optional[str] = None,
                           previous_execution_id: Optional[str] = None, G: Optional[nx.DiGraph] = None) -> List[str]:
        """Get the execution order based on the execution mode.

        Args:
            full_execution_order: Full topological sort of the workflow graph
            execution_mode: Mode of execution (full, partial, resume)
            selected_nodes: List of node IDs to execute in partial mode
            resume_from_node: Node ID to resume from in resume mode
            previous_execution_id: ID of previous execution to resume from
            G: The workflow graph

        Returns:
            List of node IDs to execute
        """
        if execution_mode == ExecutionMode.FULL:
            # Execute all nodes
            return full_execution_order

        elif execution_mode == ExecutionMode.PARTIAL and selected_nodes:
            # Execute only selected nodes and their dependencies
            if not G:
                raise ValueError("Graph is required for partial execution")

            # Find all dependencies of selected nodes
            dependencies = set()
            for node_id in selected_nodes:
                # Add the node itself
                dependencies.add(node_id)

                # Add all ancestors (dependencies)
                ancestors = nx.ancestors(G, node_id)
                dependencies.update(ancestors)

            # Filter execution order to include only dependencies
            return [node_id for node_id in full_execution_order if node_id in dependencies]

        elif execution_mode == ExecutionMode.RESUME and resume_from_node:
            # Resume execution from a specific node
            if not G:
                raise ValueError("Graph is required for resume execution")

            # Find the index of the resume node
            try:
                resume_index = full_execution_order.index(resume_from_node)
            except ValueError:
                raise ValueError(f"Resume node {resume_from_node} not found in execution order")

            # Get all nodes from the resume node onwards
            resume_nodes = full_execution_order[resume_index:]

            # If we have a previous execution, we can reuse results
            if previous_execution_id and previous_execution_id in self.execution_cache:
                previous_results = self.execution_cache[previous_execution_id]

                # Get completed nodes from previous execution
                completed_nodes = set()
                if "node_outputs" in previous_results:
                    completed_nodes = set(previous_results["node_outputs"].keys())

                # Add dependencies of resume node that were not completed in previous execution
                dependencies = nx.ancestors(G, resume_from_node)
                missing_dependencies = dependencies - completed_nodes

                # Add missing dependencies to resume nodes
                for node_id in full_execution_order:
                    if node_id in missing_dependencies:
                        resume_nodes.append(node_id)

                # Sort resume nodes according to original execution order
                resume_nodes = [node_id for node_id in full_execution_order if node_id in resume_nodes]

            return resume_nodes

        # Default to full execution
        return full_execution_order

    def get_execution_result(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a workflow execution."""
        return self.execution_cache.get(execution_id)

    def get_execution_state(self, execution_id: str) -> Optional[WorkflowExecutionState]:
        """Get the state of a workflow execution."""
        return self.execution_states.get(execution_id)

    def is_execution_active(self, execution_id: str) -> bool:
        """Check if a workflow execution is active."""
        return execution_id in self.active_executions

    def _calculate_total_execution_time(self, logs: List[Dict[str, Any]]) -> float:
        """Calculate the total execution time from logs."""
        total_time = 0.0

        for log in logs:
            if "execution_time_ms" in log:
                total_time += log["execution_time_ms"]

        return total_time
