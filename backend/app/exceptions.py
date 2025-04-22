"""
Custom exceptions for the workflow builder.

This module provides custom exception classes for the workflow builder.
"""

from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
import traceback
import datetime

class WorkflowBuilderException(HTTPException):
    """Base exception for workflow builder errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str = "INTERNAL_ERROR",
        field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        include_traceback: bool = False
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code
        self.field = field
        self.context = context or {}
        self.timestamp = datetime.datetime.now().isoformat()

        # Add traceback if requested
        if include_traceback:
            self.context["traceback"] = traceback.format_exc()

class ValidationError(WorkflowBuilderException):
    """Exception for validation errors."""

    def __init__(
        self,
        detail: str,
        code: str = "VALIDATION_ERROR",
        field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        include_traceback: bool = False
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code=code,
            field=field,
            context=context,
            headers=headers,
            include_traceback=include_traceback
        )

class NotFoundError(WorkflowBuilderException):
    """Exception for not found errors."""

    def __init__(
        self,
        detail: str,
        code: str = "NOT_FOUND",
        field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        include_traceback: bool = False
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            code=code,
            field=field,
            context=context,
            headers=headers,
            include_traceback=include_traceback
        )

class PluginError(WorkflowBuilderException):
    """Exception for plugin errors."""

    def __init__(
        self,
        detail: str,
        code: str = "PLUGIN_ERROR",
        field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        include_traceback: bool = True
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            code=code,
            field=field,
            context=context,
            headers=headers,
            include_traceback=include_traceback
        )

class WorkflowExecutionError(WorkflowBuilderException):
    """Exception for workflow execution errors."""

    def __init__(
        self,
        detail: str,
        code: str = "EXECUTION_ERROR",
        field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        include_traceback: bool = True
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            code=code,
            field=field,
            context=context,
            headers=headers,
            include_traceback=include_traceback
        )

class TypeSystemError(WorkflowBuilderException):
    """Exception for type system errors."""

    def __init__(
        self,
        detail: str,
        code: str = "TYPE_SYSTEM_ERROR",
        field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        include_traceback: bool = True
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            code=code,
            field=field,
            context=context,
            headers=headers,
            include_traceback=include_traceback
        )

class NodeConnectionError(WorkflowBuilderException):
    """Exception for node connection errors."""

    def __init__(
        self,
        detail: str,
        source_node: Optional[str] = None,
        target_node: Optional[str] = None,
        source_type: Optional[str] = None,
        target_type: Optional[str] = None,
        code: str = "CONNECTION_ERROR",
        field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        include_traceback: bool = False
    ):
        context = context or {}
        if source_node:
            context["source_node"] = source_node
        if target_node:
            context["target_node"] = target_node
        if source_type:
            context["source_type"] = source_type
        if target_type:
            context["target_type"] = target_type

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code=code,
            field=field,
            context=context,
            headers=headers,
            include_traceback=include_traceback
        )

class NodeExecutionError(WorkflowExecutionError):
    """Exception for node execution errors."""

    def __init__(
        self,
        detail: str,
        node_id: str,
        node_type: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        code: str = "NODE_EXECUTION_ERROR",
        field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        include_traceback: bool = True
    ):
        context = context or {}
        context["node_id"] = node_id
        if node_type:
            context["node_type"] = node_type
        if inputs:
            context["inputs"] = inputs

        super().__init__(
            detail=detail,
            code=code,
            field=field,
            context=context,
            headers=headers,
            include_traceback=include_traceback
        )

class ConfigurationError(WorkflowBuilderException):
    """Exception for configuration errors."""

    def __init__(
        self,
        detail: str,
        config_file: Optional[str] = None,
        code: str = "CONFIGURATION_ERROR",
        field: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        include_traceback: bool = True
    ):
        context = context or {}
        if config_file:
            context["config_file"] = config_file

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            code=code,
            field=field,
            context=context,
            headers=headers,
            include_traceback=include_traceback
        )
