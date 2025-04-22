# Import routes for easier access
from backend.app.views import (
    workflow_routes,
    node_views,
    connection_views,
    template_views,
    node_validation_routes,
    node_config_routes
)

# Import consolidated routes
from backend.app.views.consolidated_core_node_routes import router as core_node_routes_router
from backend.app.views.consolidated_plugin_routes import router as plugin_routes_router
from backend.app.views.consolidated_type_system_routes import router as type_system_routes_router
from backend.app.views.consolidated_node_types_routes import router as node_types_routes_router

# Export consolidated routes
core_node_routes = core_node_routes_router
plugin_routes = plugin_routes_router
type_system_routes = type_system_routes_router
node_types_routes = node_types_routes_router
