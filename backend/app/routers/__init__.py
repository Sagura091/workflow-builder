"""
API Routers

This module exports all API routers for the application.
"""

__all__ = [
    'core_nodes_router',
    'plugins_router',
    'type_system_router',
    'workflows_router',
    'executions_router',
    'node_validation_router',
    'node_config_router',
    'websockets_router',
    'standalone_plugins_router'
]

from backend.app.routers.core_nodes import router as core_nodes_router
from backend.app.routers.plugins import router as plugins_router
from backend.app.routers.type_system import router as type_system_router
from backend.app.routers.workflows import router as workflows_router
from backend.app.routers.executions import router as executions_router
from backend.app.routers.node_validation import router as node_validation_router
from backend.app.routers.node_config import router as node_config_router
from backend.app.routers.websockets import router as websockets_router
from backend.app.routers.standalone_plugins import router as standalone_plugins_router
