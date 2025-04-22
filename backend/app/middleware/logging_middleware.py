"""
Logging middleware for the workflow builder.

This module provides logging middleware for the workflow builder.
"""

import time
import uuid
import json
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Configure logger
logger = logging.getLogger("workflow_builder")

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log information."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        await self._log_request(request, request_id)
        
        # Process request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log response
            process_time = time.time() - start_time
            self._log_response(request, response, request_id, process_time)
            
            return response
        except Exception as exc:
            # Log exception
            process_time = time.time() - start_time
            self._log_exception(request, exc, request_id, process_time)
            raise
    
    async def _log_request(self, request: Request, request_id: str) -> None:
        """Log request information."""
        # Get request body for logging
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
                # Redact sensitive information
                if isinstance(body, dict) and "password" in body:
                    body["password"] = "********"
            except:
                body = None
        
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "type": "request",
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent", ""),
                "body": body
            }
        )
    
    def _log_response(self, request: Request, response: Response, request_id: str, process_time: float) -> None:
        """Log response information."""
        logger.info(
            f"Response: {response.status_code} {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "type": "response",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2)
            }
        )
    
    def _log_exception(self, request: Request, exc: Exception, request_id: str, process_time: float) -> None:
        """Log exception information."""
        logger.error(
            f"Exception: {str(exc)} {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "type": "error",
                "method": request.method,
                "path": request.url.path,
                "exception": str(exc),
                "process_time_ms": round(process_time * 1000, 2)
            },
            exc_info=True
        )
