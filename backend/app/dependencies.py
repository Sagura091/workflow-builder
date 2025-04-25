from fastapi import Depends
from backend.app.services.plugin_manager import PluginManager
from backend.app.services.plugin_loader import PluginLoader
from backend.app.services.type_registry import TypeRegistry
from backend.app.services.template_service import TemplateService
from backend.app.services.core_node_registry import CoreNodeRegistry
from backend.app.services.node_registry import NodeRegistry
from backend.app.controllers.plugin_controller import PluginController
from backend.app.controllers.standalone_plugin_controller import StandalonePluginController
from backend.app.controllers.plugin_testing_controller import PluginTestingController
from backend.app.controllers.type_controller import TypeController
from backend.app.controllers.node_controller import NodeController
from backend.app.controllers.connection_controller import ConnectionController
from backend.app.controllers.template_controller import TemplateController
from backend.app.controllers.node_types_controller import NodeTypesController
from backend.app.controllers.type_system_controller import TypeSystemController
from backend.app.controllers.node_validation_controller import NodeValidationController
from backend.app.controllers.execution_controller import ExecutionController
import os

# Singleton instances
_plugin_manager = None
_plugin_loader = None
_type_registry = None
_template_service = None
_node_registry = None
_core_node_registry = None

def get_plugin_manager():
    global _plugin_manager
    if _plugin_manager is None:
        # Get the path to the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Set the plugin directory to backend/plugins
        plugin_dir = os.environ.get("PLUGIN_DIR", os.path.join(backend_dir, "plugins"))
        _plugin_manager = PluginManager(plugin_dir)
        _plugin_manager.load_all_plugins()
    return _plugin_manager

def get_plugin_loader():
    global _plugin_loader
    if _plugin_loader is None:
        # Get the path to the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Set the plugin directory to backend/plugins
        plugin_dir = os.environ.get("PLUGIN_DIR", os.path.join(backend_dir, "plugins"))
        # Set the core nodes directory to backend/core_nodes
        core_nodes_dir = os.environ.get("CORE_NODES_DIR", os.path.join(backend_dir, "core_nodes"))
        _plugin_loader = PluginLoader(plugin_dir, core_nodes_dir)
        _plugin_loader.load_all_plugins()
    return _plugin_loader

def get_type_registry():
    global _type_registry
    if _type_registry is None:
        # Get the path to the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Set the type system file to backend/config/type_system.json
        type_system_file = os.environ.get("TYPE_SYSTEM_FILE", os.path.join(backend_dir, "config", "type_system.json"))
        _type_registry = TypeRegistry(type_system_file)
    return _type_registry

def get_plugin_controller(
    plugin_manager: PluginManager = Depends(get_plugin_manager)
) -> PluginController:
    return PluginController(plugin_manager)

def get_type_controller(
    type_registry: TypeRegistry = Depends(get_type_registry)
) -> TypeController:
    return TypeController(type_registry)

def get_node_controller(
    plugin_manager: PluginManager = Depends(get_plugin_manager),
    type_registry: TypeRegistry = Depends(get_type_registry)
) -> NodeController:
    return NodeController(plugin_manager, type_registry)

def get_connection_controller(
    plugin_manager: PluginManager = Depends(get_plugin_manager),
    type_registry: TypeRegistry = Depends(get_type_registry)
) -> ConnectionController:
    return ConnectionController(plugin_manager, type_registry)

def get_template_service():
    global _template_service
    if _template_service is None:
        # Get the path to the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Set the templates directory to backend/templates
        templates_dir = os.environ.get("TEMPLATES_DIR", os.path.join(backend_dir, "templates"))
        _template_service = TemplateService(templates_dir)
    return _template_service

def get_template_controller(
    template_service: TemplateService = Depends(get_template_service)
) -> TemplateController:
    return TemplateController(template_service)

def get_core_node_registry():
    global _core_node_registry
    if _core_node_registry is None:
        _core_node_registry = CoreNodeRegistry()
        _core_node_registry.initialize()
    return _core_node_registry

def get_node_registry():
    global _node_registry
    if _node_registry is None:
        _node_registry = NodeRegistry()
    return _node_registry

def get_node_types_controller(
    node_registry: NodeRegistry = Depends(get_node_registry)
) -> NodeTypesController:
    return NodeTypesController(node_registry)

def get_type_system_controller(
    type_registry: TypeRegistry = Depends(get_type_registry)
) -> TypeSystemController:
    return TypeSystemController()

def get_node_validation_controller(
    node_registry: NodeRegistry = Depends(get_node_registry),
    type_registry: TypeRegistry = Depends(get_type_registry)
) -> NodeValidationController:
    return NodeValidationController()

def get_execution_controller() -> ExecutionController:
    return ExecutionController()

def get_standalone_plugin_controller(
    plugin_loader: PluginLoader = Depends(get_plugin_loader)
) -> StandalonePluginController:
    return StandalonePluginController(plugin_loader)

def get_plugin_testing_controller(
    plugin_loader: PluginLoader = Depends(get_plugin_loader)
) -> PluginTestingController:
    return PluginTestingController(plugin_loader)
