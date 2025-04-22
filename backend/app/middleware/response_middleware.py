"""
Response standardization middleware.

This middleware ensures all responses follow the standard response format.
"""

import time
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.app.models.responses import StandardResponse, ResponseMetadata


class ResponseStandardizationMiddleware(BaseHTTPMiddleware):
    """Middleware to standardize API responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and standardize the response."""
        # Skip non-API routes
        if not request.url.path.startswith("/api"):
            return await call_next(request)
        
        # Record start time for performance tracking
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate execution time
        execution_time_ms = round((time.time() - start_time) * 1000, 2)
        
        # Skip if response is not JSON
        if not response.headers.get("content-type", "").startswith("application/json"):
            return response
        
        # Get response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # Parse response body
        try:
            import json
            body = json.loads(response_body)
            
            # Skip if already in standard format
            if isinstance(body, dict) and "status" in body and body.get("status") in ["success", "error"]:
                # Just add execution time if not present
                if "metadata" in body:
                    if "execution_time_ms" not in body["metadata"]:
                        body["metadata"]["execution_time_ms"] = execution_time_ms
                else:
                    body["metadata"] = {"execution_time_ms": execution_time_ms}
                
                return JSONResponse(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            
            # Create standard response
            standard_response = StandardResponse(
                status="success",
                data=body,
                metadata=ResponseMetadata(execution_time_ms=execution_time_ms)
            )
            
            return JSONResponse(
                content=standard_response.dict(exclude_none=True),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except Exception as e:
            # If we can't parse the response, return it as is
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
