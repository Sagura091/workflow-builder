"""
Error handling middleware for the workflow builder.

This module provides error handling middleware for the workflow builder.
"""

import traceback
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from backend.app.models.responses import StandardResponse, ErrorDetail

# Configure logger
logger = logging.getLogger("workflow_builder")

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and handle errors."""
        try:
            return await call_next(request)
        except Exception as exc:
            # Get traceback
            tb = traceback.format_exc()
            
            # Log the exception
            logger.error(
                f"Unhandled exception in middleware: {str(exc)}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "traceback": tb,
                    "exception_type": exc.__class__.__name__
                },
                exc_info=True
            )
            
            # Create error response
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content=StandardResponse(
                    status="error",
                    message="Internal server error",
                    errors=[
                        ErrorDetail(
                            code="internal_server_error",
                            message=str(exc)
                        )
                    ]
                ).model_dump(exclude_none=True)
            )
