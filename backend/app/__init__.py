import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from backend.app.config.logging_config import configure_logging
from backend.app.middleware.logging_middleware import LoggingMiddleware
from backend.app.middleware.response_middleware import ResponseStandardizationMiddleware
from backend.app.middleware.exception_handlers import (
    workflow_builder_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from backend.app.exceptions import WorkflowBuilderException
from backend.app.views import (
    workflow_routes,
    node_views,
    connection_views,
    template_views,
    node_validation_routes,
    websocket_routes,
    cache_routes,
    schedule_routes,
    auth_routes,
    node_config_routes,
    api_routes
)

# Import consolidated routes
from backend.app.views import (
    core_node_routes,
    plugin_routes,
    type_system_routes,
    node_types_routes,
    workflow_routes,
    execution_routes
)

# Import routers
from backend.app.routers.standalone_plugins import router as standalone_plugins_router
from backend.app.routers.plugin_testing import router as plugin_testing_router
from backend.app.services.core_node_registry import CoreNodeRegistry

def create_app():
    """Create and configure the FastAPI application."""
    # Configure logging
    configure_logging()
    logger = logging.getLogger("workflow_builder")
    logger.info("Initializing Workflow Builder API")

    # Initialize core node registry
    core_registry = CoreNodeRegistry()
    core_registry.initialize()
    logger.info(f"Core node registry initialized with {len(core_registry.get_all_nodes())} nodes")

    # Initialize plugin manager
    from backend.app.dependencies import get_plugin_manager
    plugin_manager = get_plugin_manager()
    logger.info(f"Plugin manager initialized with {len(plugin_manager.get_all_plugin_metadata())} plugins")

    # Initialize type registry
    from backend.app.dependencies import get_type_registry
    type_registry = get_type_registry()
    logger.info("Type registry initialized")

    # Initialize and start scheduler
    from backend.app.services.schedule_service import ScheduleService
    schedule_service = ScheduleService()
    schedule_service.start_scheduler()
    logger.info("Scheduler started")

    # Create FastAPI app
    app = FastAPI(
        title="Workflow Builder API",
        description="API for building and executing workflows with dynamic plugins",
        version="1.0.0",
    )

    # Add exception handlers
    app.add_exception_handler(WorkflowBuilderException, workflow_builder_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Add middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(ResponseStandardizationMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(workflow_routes.router, prefix="/api", tags=["workflows"])
    app.include_router(node_views.router)
    app.include_router(connection_views.router)
    app.include_router(template_views.router)
    app.include_router(node_validation_routes.router)
    app.include_router(websocket_routes.router)
    app.include_router(cache_routes.router)
    app.include_router(schedule_routes.router)
    app.include_router(auth_routes.router)
    app.include_router(node_config_routes.router)
    app.include_router(api_routes.router)

    # Register consolidated routes
    app.include_router(core_node_routes)
    app.include_router(plugin_routes)
    app.include_router(type_system_routes)
    app.include_router(node_types_routes)
    app.include_router(workflow_routes.router)
    app.include_router(execution_routes.router)

    # Register standalone plugins router
    app.include_router(standalone_plugins_router, prefix="/api")

    # Register plugin testing router
    app.include_router(plugin_testing_router, prefix="/api")

    @app.get("/", tags=["root"])
    async def root():
        return {"message": "Welcome to the Workflow Builder API"}

    @app.get("/api/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok"}

    logger.info("Workflow Builder API initialized successfully")
    return app
