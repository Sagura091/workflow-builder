"""
Exception handlers for the workflow builder.

This module provides exception handlers for the workflow builder.
"""

import traceback
import logging
from typing import Any, Dict, List, Optional, Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from backend.app.exceptions import WorkflowBuilderException
from backend.app.models.responses import StandardResponse, ErrorDetail

# Configure logger
logger = logging.getLogger("workflow_builder")

async def workflow_builder_exception_handler(
    request: Request, exc: WorkflowBuilderException
) -> JSONResponse:
    """Handle WorkflowBuilderException."""
    # Prepare logging extras
    log_extras = {
        "status_code": exc.status_code,
        "code": exc.code,
        "path": request.url.path,
        "method": request.method,
        "timestamp": getattr(exc, "timestamp", None),
    }

    # Add context to log extras if available
    if hasattr(exc, "context") and exc.context:
        log_extras["context"] = exc.context

    # Log the exception
    logger.error(
        f"WorkflowBuilderException: {exc.detail}",
        extra=log_extras,
    )

    # Create error detail
    error_detail = ErrorDetail(
        field=exc.field,
        code=exc.code,
        message=exc.detail,
        context=getattr(exc, "context", None)
    )

    # Create response
    return JSONResponse(
        status_code=exc.status_code,
        content=StandardResponse(
            status="error",
            message=exc.detail,
            errors=[error_detail]
        ).model_dump(exclude_none=True),
        headers=exc.headers
    )

async def validation_exception_handler(
    request: Request, exc: Union[RequestValidationError, PydanticValidationError]
) -> JSONResponse:
    """Handle validation errors."""
    logger.error(
        f"ValidationError: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    errors = []

    if isinstance(exc, RequestValidationError):
        for error in exc.errors():
            field = ".".join([str(loc) for loc in error["loc"] if loc != "body"])
            errors.append(
                ErrorDetail(
                    field=field if field else None,
                    code=error["type"],
                    message=error["msg"]
                )
            )
    else:
        # Handle PydanticValidationError
        for error in exc.errors():
            field = ".".join([str(loc) for loc in error["loc"]])
            errors.append(
                ErrorDetail(
                    field=field if field else None,
                    code=error["type"],
                    message=error["msg"]
                )
            )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=StandardResponse(
            status="error",
            message="Validation error",
            errors=errors
        ).model_dump(exclude_none=True)
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    # Get traceback
    tb = traceback.format_exc()

    # Create context with traceback
    context = {
        "traceback": tb,
        "exception_type": exc.__class__.__name__
    }

    # Log the exception
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": tb,
            "exception_type": exc.__class__.__name__
        },
    )

    # Create error detail
    error_detail = ErrorDetail(
        code="INTERNAL_ERROR",
        message=str(exc),
        context=context
    )

    # Create response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=StandardResponse(
            status="error",
            message="An unexpected error occurred",
            errors=[error_detail]
        ).model_dump(exclude_none=True)
    )
