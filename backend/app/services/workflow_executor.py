import networkx as nx
from typing import List, Dict, Any, Optional, Callable, Tuple, Set, Union, Type, IO
import datetime
import uuid
import logging
import asyncio
import traceback
import time
import json
import csv
import os
import io
import concurrent.futures
from enum import Enum
from pathlib import Path

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
from backend.app.versioning.version_manager import version_manager, VersionedFeature

# Configure logger
logger = logging.getLogger("workflow_builder")

class OutputFormat(str, Enum):
    """Output format for workflow execution results."""
    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    PYTHON = "python"
    CUSTOM = "custom"

class OutputDestination(str, Enum):
    """Destination for workflow execution results."""
    MEMORY = "memory"  # Default, just return the result
    FILE = "file"      # Write to a file
    CONSOLE = "console"  # Print to console
    WEBSOCKET = "websocket"  # Send via WebSocket
    CALLBACK = "callback"  # Call a function with the result
    DATABASE = "database"  # Store in a database

class WorkflowExecutor:
    """
    Revolutionary service for executing workflows.

    This executor provides advanced features including:
    - Parallel execution of independent nodes
    - Multiple output formats and destinations
    - Advanced error handling and recovery
    - Execution profiling and optimization
    - Version-aware node execution
    """

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

        # Thread pool for parallel execution
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        # Execution options
        self.use_node_cache = True
        self.cache_ttl = 3600  # 1 hour in seconds
        self.parallel_execution = True
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        self.execution_timeout = 300  # 5 minutes in seconds

        # Output options
        self.default_output_format = OutputFormat.JSON
        self.default_output_destination = OutputDestination.MEMORY
        self.output_directory = "workflow_outputs"

        # Create output directory if it doesn't exist
        os.makedirs(self.output_directory, exist_ok=True)

        # Version management
        self.current_engine_version = version_manager.get_feature_version(
            VersionedFeature.EXECUTION_ENGINE
        )

        logger.info(f"Workflow executor initialized with engine version {self.current_engine_version}")

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
               execution_options: Optional[Dict[str, Any]] = None,
               output_format: Optional[OutputFormat] = None,
               output_destination: Optional[OutputDestination] = None,
               output_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a workflow synchronously with advanced options.

        Args:
            nodes: List of nodes in the workflow
            edges: List of edges in the workflow
            execution_id: Optional execution ID (generated if not provided)
            execution_mode: Mode of execution (full, partial, resume)
            selected_nodes: List of node IDs to execute in partial mode
            resume_from_node: Node ID to resume from in resume mode
            previous_execution_id: ID of previous execution to resume from
            execution_options: Additional execution options
            output_format: Format for the execution result
            output_destination: Destination for the execution result
            output_options: Additional options for output handling

        Returns:
            Execution result in the specified format
        """
        # Generate execution ID if not provided
        if not execution_id:
            execution_id = str(uuid.uuid4())

        # Initialize execution options
        if execution_options is None:
            execution_options = {}

        # Apply execution options
        use_node_cache = execution_options.get("use_cache", self.use_node_cache)
        cache_ttl = execution_options.get("cache_ttl", self.cache_ttl)
        parallel_execution = execution_options.get("parallel_execution", self.parallel_execution)
        max_retries = execution_options.get("max_retries", self.max_retries)
        execution_timeout = execution_options.get("timeout", self.execution_timeout)

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

        # Start execution timer
        overall_start_time = time.time()

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

            # Check if we should use parallel execution
            if parallel_execution:
                # Identify independent nodes that can be executed in parallel
                # For each level in the graph, execute nodes in parallel
                levels = self._get_execution_levels(G, execution_order)

                for level_nodes in levels:
                    # Execute nodes in this level in parallel
                    futures = {}

                    for node_id in level_nodes:
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
                        inputs = self._gather_node_inputs(node_id, edges, node_map, results)

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

                        # Submit node execution to thread pool
                        future = self.thread_pool.submit(
                            self._execute_single_node,
                            node_id=node_id,
                            node=node,
                            plugin=plugin,
                            inputs=inputs,
                            use_cache=use_node_cache,
                            cache_ttl=cache_ttl,
                            max_retries=max_retries
                        )
                        futures[node_id] = (future, start_time)

                    # Wait for all futures to complete
                    for node_id, (future, start_time) in futures.items():
                        try:
                            # Get the result with timeout
                            result, used_cache, execution_time_ms = future.result(timeout=execution_timeout)

                            # Record end time
                            end_time = datetime.datetime.now()

                            # Process successful execution
                            self._process_node_success(
                                node_id=node_id,
                                node=node_map[node_id],
                                result=result,
                                used_cache=used_cache,
                                execution_time_ms=execution_time_ms,
                                start_time=start_time,
                                end_time=end_time,
                                execution_id=execution_id,
                                execution_state=execution_state,
                                node_results=node_results,
                                results=results,
                                logs=logs
                            )

                        except Exception as e:
                            # Process execution failure
                            self._process_node_failure(
                                node_id=node_id,
                                node=node_map[node_id],
                                error=e,
                                start_time=start_time,
                                execution_id=execution_id,
                                execution_state=execution_state,
                                node_results=node_results,
                                logs=logs,
                                inputs=self._gather_node_inputs(node_id, edges, node_map, results)
                            )

                            # Raise the error to stop execution
                            if isinstance(e, concurrent.futures.TimeoutError):
                                raise NodeExecutionError(
                                    detail=f"Node {node_id} execution timed out after {execution_timeout} seconds",
                                    node_id=node_id,
                                    node_type=node_map[node_id].type
                                )
                            else:
                                raise
            else:
                # Sequential execution
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
                    inputs = self._gather_node_inputs(node_id, edges, node_map, results)

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

                        if use_node_cache and self.node_cache.is_node_cacheable(node.type):
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

                        # If not in cache, execute the node with retry
                        if result is None:
                            # Run the plugin with retry
                            result = self.execute_node_with_retry(
                                node_id=node_id,
                                node=node,
                                plugin=plugin,
                                inputs=inputs,
                                max_retries=max_retries
                            )

                            # Cache the result if caching is enabled
                            if use_node_cache and cache_key and self.node_cache.is_node_cacheable(node.type):
                                self.node_cache.set(cache_key, result, cache_ttl)

                        # Record end time
                        end_time = datetime.datetime.now()
                        execution_time_ms = (end_time - start_time).total_seconds() * 1000

                        # Process successful execution
                        self._process_node_success(
                            node_id=node_id,
                            node=node,
                            result=result,
                            used_cache=used_cache,
                            execution_time_ms=execution_time_ms,
                            start_time=start_time,
                            end_time=end_time,
                            execution_id=execution_id,
                            execution_state=execution_state,
                            node_results=node_results,
                            results=results,
                            logs=logs
                        )

                    except Exception as e:
                        # Process execution failure
                        self._process_node_failure(
                            node_id=node_id,
                            node=node,
                            error=e,
                            start_time=start_time,
                            execution_id=execution_id,
                            execution_state=execution_state,
                            node_results=node_results,
                            logs=logs,
                            inputs=inputs
                        )

                        # Re-raise the exception
                        raise

            # Calculate total execution time
            overall_execution_time_ms = (time.time() - overall_start_time) * 1000

            # Update execution state
            execution_state.status = ExecutionStatus.COMPLETED
            execution_state.end_time = datetime.datetime.now().isoformat()
            execution_state.execution_time_ms = overall_execution_time_ms

            # Execution completed successfully
            execution_result = {
                "execution_id": execution_id,
                "status": ExecutionStatus.COMPLETED,
                "node_outputs": results,
                "node_results": node_results,
                "log": logs,
                "start_time": logs[0]["timestamp"] if logs else datetime.datetime.now().isoformat(),
                "end_time": datetime.datetime.now().isoformat(),
                "execution_time_ms": overall_execution_time_ms
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
                    "execution_time_ms": overall_execution_time_ms
                }
            ))

            # Handle output formatting and destination
            return self.handle_output(
                result=execution_result,
                output_format=output_format,
                output_destination=output_destination,
                output_options=output_options
            )

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

            # Handle output formatting and destination for error result
            if output_format or output_destination:
                return self.handle_output(
                    result=error_result,
                    output_format=output_format,
                    output_destination=output_destination,
                    output_options=output_options
                )

            # Re-raise the exception
            raise

        finally:
            # Remove from active executions
            self.active_executions.discard(execution_id)

            # Keep execution state for future reference

    def _gather_node_inputs(self, node_id: str, edges: List[Edge], node_map: Dict[str, Node],
                          results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gather inputs for a node from upstream nodes.

        Args:
            node_id: The ID of the node to gather inputs for
            edges: List of edges in the workflow
            node_map: Map of node IDs to nodes
            results: Map of node IDs to execution results

        Returns:
            Dictionary of input values for the node
        """
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

        return inputs

    def _execute_single_node(self, node_id: str, node: Node, plugin: Any, inputs: Dict[str, Any],
                           use_cache: bool = True, cache_ttl: int = 3600,
                           max_retries: int = 3) -> Tuple[Dict[str, Any], bool, float]:
        """
        Execute a single node with caching and retry support.

        Args:
            node_id: The ID of the node to execute
            node: The node to execute
            plugin: The plugin to use for execution
            inputs: The input values for the node
            use_cache: Whether to use caching
            cache_ttl: Cache time-to-live in seconds
            max_retries: Maximum number of retry attempts

        Returns:
            Tuple of (result, used_cache, execution_time_ms)
        """
        start_time = time.time()

        # Check if result is in cache
        cache_key = None
        result = None
        used_cache = False

        if use_cache and self.node_cache.is_node_cacheable(node.type):
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

        # If not in cache, execute the node with retry
        if result is None:
            # Run the plugin with retry
            result = self.execute_node_with_retry(
                node_id=node_id,
                node=node,
                plugin=plugin,
                inputs=inputs,
                max_retries=max_retries
            )

            # Cache the result if caching is enabled
            if use_cache and cache_key and self.node_cache.is_node_cacheable(node.type):
                self.node_cache.set(cache_key, result, cache_ttl)

        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000

        # Add cache info to result
        if used_cache:
            result["_cache_hit"] = True

        return result, used_cache, execution_time_ms

    def _process_node_success(self, node_id: str, node: Node, result: Dict[str, Any],
                            used_cache: bool, execution_time_ms: float,
                            start_time: datetime.datetime, end_time: datetime.datetime,
                            execution_id: str, execution_state: WorkflowExecutionState,
                            node_results: Dict[str, NodeExecutionResult],
                            results: Dict[str, Dict[str, Any]], logs: List[Dict[str, Any]]):
        """
        Process a successful node execution.

        Args:
            node_id: The ID of the node
            node: The node
            result: The execution result
            used_cache: Whether the result was from cache
            execution_time_ms: Execution time in milliseconds
            start_time: Start time of execution
            end_time: End time of execution
            execution_id: The execution ID
            execution_state: The execution state
            node_results: Map of node IDs to execution results
            results: Map of node IDs to outputs
            logs: List of execution logs
        """
        # Store result
        results[node_id] = result

        # Create node execution result
        node_result = NodeExecutionResult(
            node_id=node_id,
            node_type=node.type,
            status=NodeExecutionStatus.COMPLETED if not used_cache else NodeExecutionStatus.CACHED,
            outputs=result,
            execution_time_ms=execution_time_ms,
            start_time=start_time.isoformat(),
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

    def _process_node_failure(self, node_id: str, node: Node, error: Exception,
                            start_time: datetime.datetime, execution_id: str,
                            execution_state: WorkflowExecutionState,
                            node_results: Dict[str, NodeExecutionResult],
                            logs: List[Dict[str, Any]], inputs: Dict[str, Any]):
        """
        Process a failed node execution.

        Args:
            node_id: The ID of the node
            node: The node
            error: The error that occurred
            start_time: Start time of execution
            execution_id: The execution ID
            execution_state: The execution state
            node_results: Map of node IDs to execution results
            logs: List of execution logs
            inputs: The input values for the node
        """
        # Get error details
        error_time = datetime.datetime.now()
        error_message = str(error)
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
            start_time=start_time.isoformat(),
            end_time=datetime.datetime.now().isoformat(),
            error=error_message
        )
        node_results[node_id] = node_result

        # Update execution state
        execution_state.node_statuses[node_id] = NodeExecutionStatus.FAILED
        execution_state.failed_nodes.append(node_id)

    def _get_execution_levels(self, G: nx.DiGraph, execution_order: List[str]) -> List[List[str]]:
        """
        Group nodes into levels for parallel execution.

        Args:
            G: The workflow graph
            execution_order: The execution order of nodes

        Returns:
            List of lists of node IDs, where each inner list represents a level
        """
        # Create a subgraph with only the nodes in the execution order
        subgraph = G.subgraph(execution_order)

        # Get the longest path length for each node
        path_lengths = {}
        for node in execution_order:
            # Find all paths to this node
            paths = []
            for source in execution_order:
                if source != node:
                    try:
                        # Check if there's a path from source to node
                        path = nx.shortest_path(subgraph, source, node)
                        if path:
                            paths.append(path)
                    except nx.NetworkXNoPath:
                        # No path exists
                        pass

            # Get the longest path length
            if paths:
                path_lengths[node] = max(len(path) - 1 for path in paths)
            else:
                # No incoming paths, this is a root node
                path_lengths[node] = 0

        # Group nodes by level
        levels = {}
        for node, level in path_lengths.items():
            if level not in levels:
                levels[level] = []
            levels[level].append(node)

        # Sort levels by key and return as a list of lists
        return [levels[level] for level in sorted(levels.keys())]

    async def execute_async(self, nodes: List[Node], edges: List[Edge], execution_id: Optional[str] = None,
                      execution_mode: ExecutionMode = ExecutionMode.FULL,
                      selected_nodes: Optional[List[str]] = None,
                      resume_from_node: Optional[str] = None,
                      previous_execution_id: Optional[str] = None,
                      execution_options: Optional[Dict[str, Any]] = None,
                      output_format: Optional[OutputFormat] = None,
                      output_destination: Optional[OutputDestination] = None,
                      output_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a workflow asynchronously with advanced options.

        Args:
            nodes: List of nodes in the workflow
            edges: List of edges in the workflow
            execution_id: Optional execution ID (generated if not provided)
            execution_mode: Mode of execution (full, partial, resume)
            selected_nodes: List of node IDs to execute in partial mode
            resume_from_node: Node ID to resume from in resume mode
            previous_execution_id: ID of previous execution to resume from
            execution_options: Additional execution options
            output_format: Format for the execution result
            output_destination: Destination for the execution result
            output_options: Additional options for output handling

        Returns:
            Execution result in the specified format
        """
        # Generate execution ID if not provided
        if not execution_id:
            execution_id = str(uuid.uuid4())

        # Initialize execution options
        if execution_options is None:
            execution_options = {}

        # Apply execution options
        use_node_cache = execution_options.get("use_cache", self.use_node_cache)
        cache_ttl = execution_options.get("cache_ttl", self.cache_ttl)
        max_retries = execution_options.get("max_retries", self.max_retries)
        execution_timeout = execution_options.get("timeout", self.execution_timeout)

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

        # Start execution timer
        overall_start_time = time.time()

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

            # Sequential execution (async version)
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
                inputs = self._gather_node_inputs(node_id, edges, node_map, results)

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

                    # Send log message for console window
                    await self.websocket_manager.broadcast_execution_update(
                        execution_id=execution_id,
                        update_type="log",
                        data={
                            "node": node_id,
                            "status": "started",
                            "value": f"Starting execution of node {node_id} ({node.type})",
                            "timestamp": start_time_str,
                            "node_type": node.type
                        }
                    )

                    # Check if result is in cache
                    cache_key = None
                    result = None
                    used_cache = False

                    if use_node_cache and self.node_cache.is_node_cacheable(node.type):
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
                        # Run the plugin with retry
                        result = self.execute_node_with_retry(
                            node_id=node_id,
                            node=node,
                            plugin=plugin,
                            inputs=inputs,
                            max_retries=max_retries
                        )

                        # Cache the result if caching is enabled
                        if use_node_cache and cache_key and self.node_cache.is_node_cacheable(node.type):
                            self.node_cache.set(cache_key, result, cache_ttl)

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

                    # Send log message for console window
                    await self.websocket_manager.broadcast_execution_update(
                        execution_id=execution_id,
                        update_type="log",
                        data={
                            "node": node_id,
                            "status": "completed",
                            "value": result.get("logged") or result.get("display") or f"Node {node_id} completed successfully",
                            "timestamp": end_time.isoformat(),
                            "execution_time_ms": execution_time_ms,
                            "cached": used_cache,
                            "node_type": node.type
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

                    # Send log message for console window
                    await self.websocket_manager.broadcast_execution_update(
                        execution_id=execution_id,
                        update_type="log",
                        data={
                            "node": node_id,
                            "status": "error",
                            "value": f"Error: {error_message}",
                            "timestamp": error_time.isoformat(),
                            "traceback": error_traceback,
                            "node_type": node.type
                        }
                    )

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

            # Calculate total execution time
            overall_execution_time_ms = (time.time() - overall_start_time) * 1000

            # Update execution state
            execution_state.status = ExecutionStatus.COMPLETED
            execution_state.end_time = datetime.datetime.now().isoformat()
            execution_state.execution_time_ms = overall_execution_time_ms

            # Execution completed successfully
            execution_result = {
                "execution_id": execution_id,
                "status": ExecutionStatus.COMPLETED,
                "node_outputs": results,
                "node_results": node_results,
                "log": logs,
                "start_time": logs[0]["timestamp"] if logs else datetime.datetime.now().isoformat(),
                "end_time": datetime.datetime.now().isoformat(),
                "execution_time_ms": overall_execution_time_ms
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
                    "execution_time_ms": overall_execution_time_ms
                }
            )

            # Send log message for console window
            await self.websocket_manager.broadcast_execution_update(
                execution_id=execution_id,
                update_type="log",
                data={
                    "node": "workflow",
                    "status": "completed",
                    "value": f"Workflow execution completed successfully in {(overall_execution_time_ms / 1000):.2f} seconds",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "execution_time_ms": overall_execution_time_ms
                }
            )

            # Handle output formatting and destination
            return self.handle_output(
                result=execution_result,
                output_format=output_format,
                output_destination=output_destination,
                output_options=output_options
            )

        except Exception as e:
            # Log the error
            error_time = datetime.datetime.now().isoformat()
            error_message = str(e)
            error_traceback = traceback.format_exc()

            logger.error(f"Workflow execution error: {error_message}\n{error_traceback}")

            # Update execution state
            execution_state.status = ExecutionStatus.FAILED
            execution_state.end_time = datetime.datetime.now().isoformat()
            execution_state.execution_time_ms = (time.time() - overall_start_time) * 1000

            # Create error result
            error_result = {
                "execution_id": execution_id,
                "status": ExecutionStatus.FAILED,
                "node_outputs": results if 'results' in locals() else {},
                "node_results": node_results if 'node_results' in locals() else {},
                "log": logs if 'logs' in locals() else [],
                "error": error_message,
                "traceback": error_traceback,
                "timestamp": error_time,
                "execution_time_ms": execution_state.execution_time_ms
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

            # Send log message for console window
            await self.websocket_manager.broadcast_execution_update(
                execution_id=execution_id,
                update_type="log",
                data={
                    "node": "workflow",
                    "status": "error",
                    "value": f"Workflow execution failed: {error_message}",
                    "timestamp": error_time,
                    "traceback": error_traceback,
                    "execution_time_ms": execution_state.execution_time_ms
                }
            )

            # Handle output formatting and destination for error result
            if output_format or output_destination:
                return self.handle_output(
                    result=error_result,
                    output_format=output_format,
                    output_destination=output_destination,
                    output_options=output_options
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

    def format_output(self, result: Dict[str, Any], output_format: OutputFormat) -> Any:
        """
        Format the execution result according to the specified format.

        Args:
            result: The execution result to format
            output_format: The desired output format

        Returns:
            The formatted result
        """
        if output_format == OutputFormat.JSON:
            return json.dumps(result, indent=2, default=str)

        elif output_format == OutputFormat.CSV:
            # Extract node results for CSV
            csv_data = []
            headers = ["node_id", "node_type", "status", "execution_time_ms"]

            # Add headers row
            csv_data.append(headers)

            # Add data rows
            for node_id, node_result in result.get("node_results", {}).items():
                row = [
                    node_id,
                    node_result.get("node_type", ""),
                    node_result.get("status", ""),
                    node_result.get("execution_time_ms", "")
                ]
                csv_data.append(row)

            # Convert to CSV string
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(csv_data)
            return output.getvalue()

        elif output_format == OutputFormat.TEXT:
            # Create a simple text report
            lines = [
                f"Execution ID: {result.get('execution_id', 'N/A')}",
                f"Status: {result.get('status', 'N/A')}",
                f"Start Time: {result.get('start_time', 'N/A')}",
                f"End Time: {result.get('end_time', 'N/A')}",
                f"Execution Time: {result.get('execution_time_ms', 0)} ms",
                "\nNode Results:"
            ]

            for node_id, node_result in result.get("node_results", {}).items():
                lines.append(f"  - {node_id} ({node_result.get('node_type', '')}): {node_result.get('status', '')}")
                if node_result.get("error"):
                    lines.append(f"    Error: {node_result.get('error')}")

            return "\n".join(lines)

        elif output_format == OutputFormat.MARKDOWN:
            # Create a markdown report
            lines = [
                f"# Workflow Execution Report",
                f"",
                f"**Execution ID:** {result.get('execution_id', 'N/A')}",
                f"**Status:** {result.get('status', 'N/A')}",
                f"**Start Time:** {result.get('start_time', 'N/A')}",
                f"**End Time:** {result.get('end_time', 'N/A')}",
                f"**Execution Time:** {result.get('execution_time_ms', 0)} ms",
                f"",
                f"## Node Results",
                f"",
                f"| Node ID | Type | Status | Time (ms) |",
                f"|---------|------|--------|-----------|"
            ]

            for node_id, node_result in result.get("node_results", {}).items():
                lines.append(
                    f"| {node_id} | {node_result.get('node_type', '')} | "
                    f"{node_result.get('status', '')} | {node_result.get('execution_time_ms', '')} |"
                )

            return "\n".join(lines)

        elif output_format == OutputFormat.HTML:
            # Create an HTML report
            html = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "  <title>Workflow Execution Report</title>",
                "  <style>",
                "    body { font-family: Arial, sans-serif; margin: 20px; }",
                "    table { border-collapse: collapse; width: 100%; }",
                "    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
                "    th { background-color: #f2f2f2; }",
                "    .error { color: red; }",
                "    .success { color: green; }",
                "  </style>",
                "</head>",
                "<body>",
                f"  <h1>Workflow Execution Report</h1>",
                f"  <p><strong>Execution ID:</strong> {result.get('execution_id', 'N/A')}</p>",
                f"  <p><strong>Status:</strong> {result.get('status', 'N/A')}</p>",
                f"  <p><strong>Start Time:</strong> {result.get('start_time', 'N/A')}</p>",
                f"  <p><strong>End Time:</strong> {result.get('end_time', 'N/A')}</p>",
                f"  <p><strong>Execution Time:</strong> {result.get('execution_time_ms', 0)} ms</p>",
                "  <h2>Node Results</h2>",
                "  <table>",
                "    <tr>",
                "      <th>Node ID</th>",
                "      <th>Type</th>",
                "      <th>Status</th>",
                "      <th>Time (ms)</th>",
                "    </tr>"
            ]

            for node_id, node_result in result.get("node_results", {}).items():
                status_class = "error" if node_result.get("status") == "failed" else "success"
                html.append(
                    f"    <tr>",
                    f"      <td>{node_id}</td>",
                    f"      <td>{node_result.get('node_type', '')}</td>",
                    f"      <td class='{status_class}'>{node_result.get('status', '')}</td>",
                    f"      <td>{node_result.get('execution_time_ms', '')}</td>",
                    f"    </tr>"
                )

            html.extend([
                "  </table>",
                "</body>",
                "</html>"
            ])

            return "\n".join(html)

        elif output_format == OutputFormat.PYTHON:
            # Return the raw Python dict
            return result

        else:  # OutputFormat.CUSTOM or unknown
            # Default to JSON
            return json.dumps(result, indent=2, default=str)

    def handle_output(self, result: Dict[str, Any],
                     output_format: OutputFormat = None,
                     output_destination: OutputDestination = None,
                     output_options: Dict[str, Any] = None) -> Any:
        """
        Handle the execution result according to the specified format and destination.

        Args:
            result: The execution result to handle
            output_format: The desired output format (defaults to self.default_output_format)
            output_destination: The desired output destination (defaults to self.default_output_destination)
            output_options: Additional options for output handling

        Returns:
            The handled result, or None if the result was sent to an external destination
        """
        # Use defaults if not specified
        if output_format is None:
            output_format = self.default_output_format

        if output_destination is None:
            output_destination = self.default_output_destination

        if output_options is None:
            output_options = {}

        # Format the output
        formatted_output = self.format_output(result, output_format)

        # Handle the output based on destination
        if output_destination == OutputDestination.MEMORY:
            # Just return the formatted output
            return formatted_output

        elif output_destination == OutputDestination.FILE:
            # Get file path from options or generate one
            file_path = output_options.get("file_path")
            if not file_path:
                # Generate a file name based on execution ID and format
                execution_id = result.get("execution_id", str(uuid.uuid4()))
                extension = output_format.value
                file_path = os.path.join(self.output_directory, f"workflow_{execution_id}.{extension}")

            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

            # Write to file
            with open(file_path, "w", encoding="utf-8") as f:
                if isinstance(formatted_output, str):
                    f.write(formatted_output)
                else:
                    json.dump(formatted_output, f, indent=2, default=str)

            logger.info(f"Workflow result written to {file_path}")
            return file_path

        elif output_destination == OutputDestination.CONSOLE:
            # Print to console
            print(formatted_output)
            return formatted_output

        elif output_destination == OutputDestination.WEBSOCKET:
            # Send via WebSocket
            client_id = output_options.get("client_id")
            asyncio.create_task(self.websocket_manager.send_message(
                client_id=client_id,
                message_type="workflow_result",
                data=formatted_output
            ))
            return formatted_output

        elif output_destination == OutputDestination.CALLBACK:
            # Call a function with the result
            callback = output_options.get("callback")
            if callable(callback):
                return callback(formatted_output)
            else:
                logger.warning("Callback function not provided or not callable")
                return formatted_output

        elif output_destination == OutputDestination.DATABASE:
            # Store in a database (simplified implementation)
            logger.info("Database storage not fully implemented yet")
            # In a real implementation, you would store the result in a database
            return formatted_output

        else:
            # Unknown destination, default to memory
            logger.warning(f"Unknown output destination: {output_destination}")
            return formatted_output

    def execute_node_with_retry(self, node_id: str, node: Node, plugin: Any,
                              inputs: Dict[str, Any], max_retries: int = None) -> Dict[str, Any]:
        """
        Execute a node with automatic retry on failure.

        Args:
            node_id: The ID of the node to execute
            node: The node to execute
            plugin: The plugin to use for execution
            inputs: The input values for the node
            max_retries: Maximum number of retry attempts (defaults to self.max_retries)

        Returns:
            The execution result
        """
        if max_retries is None:
            max_retries = self.max_retries

        retry_count = 0
        last_error = None

        while retry_count <= max_retries:
            try:
                # Execute the node
                result = plugin.run(inputs, node.config)
                return result

            except Exception as e:
                # Record the error
                last_error = e
                retry_count += 1

                if retry_count <= max_retries:
                    # Log retry attempt
                    logger.warning(
                        f"Node {node_id} execution failed, retrying ({retry_count}/{max_retries}): {str(e)}"
                    )

                    # Wait before retrying
                    time.sleep(self.retry_delay * retry_count)  # Exponential backoff
                else:
                    # Max retries reached, re-raise the last error
                    logger.error(f"Node {node_id} execution failed after {max_retries} retries: {str(e)}")
                    raise last_error

        # This should never be reached, but just in case
        raise last_error if last_error else Exception(f"Unknown error executing node {node_id}")
