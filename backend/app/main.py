"""
Main Application Module

This module initializes the FastAPI application and includes all routers.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.controllers.core_node_router import router as core_node_router
from backend.app.controllers.node_instance_controller import router as node_instance_router
from backend.app.services.core_node_registry import CoreNodeRegistry
from backend.app.views.api_routes import router as api_router
from backend.app.views.consolidated_plugin_routes import router as plugin_routes
from backend.app.views.consolidated_node_types_routes import router as node_types_routes, legacy_router as legacy_node_types_routes
from backend.app.views.consolidated_type_system_routes import router as type_system_routes, legacy_router as legacy_type_system_routes
from backend.app.views.node_validation_routes import router as node_validation_routes, legacy_router as legacy_node_validation_routes
from backend.app.views.node_config_routes import router as node_config_routes, legacy_router as legacy_node_config_routes
from backend.app.views.execution_routes import router as execution_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("workflow_builder")

# Initialize the core node registry
node_registry = CoreNodeRegistry()
node_registry.initialize()

# Create the FastAPI application
app = FastAPI(
    title="Workflow Builder API",
    description="API for the Workflow Builder application",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(core_node_router, prefix="/api")
app.include_router(node_instance_router, prefix="/api")

# Include new API routes
app.include_router(api_router)
app.include_router(plugin_routes)
app.include_router(node_types_routes)
app.include_router(legacy_node_types_routes)
app.include_router(type_system_routes)
app.include_router(legacy_type_system_routes)
app.include_router(node_validation_routes)
app.include_router(legacy_node_validation_routes)
app.include_router(node_config_routes)
app.include_router(legacy_node_config_routes)
app.include_router(execution_routes)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "status": "success",
        "message": "Workflow Builder API is running",
        "version": "1.0.0",
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "success",
        "message": "API is healthy",
        "core_nodes_count": len(node_registry.get_all_nodes()),
    }
