"""
Version Detection Middleware for API

This module provides middleware for FastAPI that handles version detection
and negotiation for API requests.
"""

import logging
from typing import Callable, Dict, Optional
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .version_manager import version_manager, VersionedFeature

logger = logging.getLogger(__name__)

class VersionHeaderMiddleware(BaseHTTPMiddleware):
    """
    Middleware that handles API version detection and negotiation.

    This middleware:
    1. Detects requested API version from headers or URL
    2. Validates the requested version
    3. Sets the appropriate version for the request context
    4. Adds version information to the response headers
    """

    def __init__(
        self,
        app: ASGIApp,
        default_version: str = "0.1.0",
        header_name: str = "X-API-Version",
        query_param: str = "api_version",
        path_pattern: str = r"/api/v(\d+\.\d+\.\d+)/"
    ):
        super().__init__(app)
        self.default_version = default_version
        self.header_name = header_name
        self.query_param = query_param
        self.path_pattern = path_pattern

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and add version information."""
        # Extract version from request
        version = self._extract_version(request)

        # Validate the version
        if version not in version_manager.list_available_versions():
            # If invalid, fall back to default
            logger.warning(f"Requested API version {version} not available, using {self.default_version}")
            version = self.default_version

        # Store the version in request state
        request.state.api_version = version

        # Process the request
        response = await call_next(request)

        # Add version information to response headers
        response.headers[self.header_name] = version
        response.headers["X-API-Latest-Version"] = version_manager.get_latest_version()

        # Add all available versions
        response.headers["X-API-Available-Versions"] = ",".join(version_manager.list_available_versions())

        # Add feature versions
        api_feature_version = version_manager.get_feature_version(VersionedFeature.API, version)
        response.headers["X-API-Feature-Version"] = api_feature_version

        # Add compatibility information
        latest_version = version_manager.get_latest_version()
        if version != latest_version:
            compatibility = version_manager.check_compatibility(version, latest_version)
            response.headers["X-API-Compatible-With-Latest"] = str(compatibility.compatible).lower()
            if compatibility.upgrade_path:
                response.headers["X-API-Upgrade-Path"] = ",".join(compatibility.upgrade_path)

        # Add deprecation warning if needed
        for feature, feature_version in version_manager.get_deprecated_features(version):
            if feature == VersionedFeature.API and feature_version == api_feature_version:
                response.headers["X-API-Deprecated"] = "true"
                response.headers["X-API-Deprecation-Info"] = (
                    f"This API version is deprecated. Please upgrade to version "
                    f"{version_manager.get_latest_version()}"
                )

                # Add sunset information if available
                if hasattr(version_manager, "get_sunset_date"):
                    sunset_date = version_manager.get_sunset_date(version)
                    if sunset_date:
                        response.headers["X-API-Sunset-Date"] = sunset_date
                break

        return response

    def _extract_version(self, request: Request) -> str:
        """Extract the requested version from the request."""
        # Check header first
        version = request.headers.get(self.header_name)
        if version:
            return version

        # Check query parameter
        version = request.query_params.get(self.query_param)
        if version:
            return version

        # Check URL path
        import re
        path = request.url.path
        match = re.search(self.path_pattern, path)
        if match:
            return match.group(1)

        # Default to the latest version
        return self.default_version


class VersionedAPIRouter(APIRoute):
    """
    Custom API route that handles version-specific routing.

    This allows defining different handlers for different API versions
    within the same endpoint.
    """

    def __init__(
        self,
        *args,
        version_handlers: Dict[str, Callable] = None,
        min_version: Optional[str] = None,
        max_version: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the versioned route.

        Args:
            version_handlers: Dict mapping version strings to handler functions
            min_version: Minimum supported version (inclusive)
            max_version: Maximum supported version (inclusive)
            *args, **kwargs: Arguments passed to the parent APIRoute
        """
        self.version_handlers = version_handlers or {}
        self.min_version = min_version
        self.max_version = max_version

        # Use the latest handler as the default
        if self.version_handlers:
            latest_version = max(self.version_handlers.keys(), key=lambda v: v)
            default_handler = self.version_handlers[latest_version]
            kwargs["endpoint"] = default_handler

        super().__init__(*args, **kwargs)

    async def handle(self, request: Request) -> Response:
        """Handle the request with the appropriate version handler."""
        # Get the API version from request state (set by middleware)
        version = getattr(request.state, "api_version", version_manager.current_version)

        # Check version constraints
        if self.min_version and version_manager.check_compatibility(
            version, self.min_version
        ).breaking_changes:
            return Response(
                content=f"API version {version} is too old. Minimum supported version is {self.min_version}",
                status_code=400
            )

        if self.max_version and version_manager.check_compatibility(
            self.max_version, version
        ).breaking_changes:
            return Response(
                content=f"API version {version} is too new. Maximum supported version is {self.max_version}",
                status_code=400
            )

        # Find the appropriate handler for this version
        handler = self._get_handler_for_version(version)

        # If no handler found, use the default
        if not handler:
            return await super().handle(request)

        # Create a new scope with the selected endpoint
        scope = request.scope.copy()
        scope["endpoint"] = handler

        # Create a new request with the updated scope
        versioned_request = Request(scope, request.receive, request.send)

        # Handle the request with the selected handler
        return await super().handle(versioned_request)

    def _get_handler_for_version(self, version: str) -> Optional[Callable]:
        """Get the appropriate handler for the requested version."""
        if not self.version_handlers:
            return None

        # If exact version match exists, use it
        if version in self.version_handlers:
            return self.version_handlers[version]

        # Find the latest compatible version
        compatible_versions = []
        for handler_version in self.version_handlers:
            compatibility = version_manager.check_compatibility(handler_version, version)
            if compatibility.compatible:
                compatible_versions.append(handler_version)

        if not compatible_versions:
            # No compatible version found, use the default
            return None

        # Use the latest compatible version
        latest_compatible = max(compatible_versions, key=lambda v: v)
        return self.version_handlers[latest_compatible]


def create_versioned_app(
    title: str = "Workflow Builder API",
    description: str = "API for the Workflow Builder",
    version: str = "0.1.0",
    default_api_version: str = "0.1.0"
) -> FastAPI:
    """
    Create a FastAPI application with version middleware.

    Args:
        title: API title
        description: API description
        version: API version
        default_api_version: Default API version to use

    Returns:
        FastAPI application with version middleware
    """
    app = FastAPI(title=title, description=description, version=version)

    # Add version middleware
    app.add_middleware(
        VersionHeaderMiddleware,
        default_version=default_api_version
    )

    # Set the current version
    version_manager.set_current_version(version)

    return app
