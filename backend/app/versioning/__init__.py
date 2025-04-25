"""
Versioning Package

This package provides a revolutionary version management system for the
Workflow Builder backend.

Features:
1. Dynamic version resolution
2. Semantic versioning with feature flags
3. Automatic compatibility detection
4. Version-aware dependency injection
5. Time-travel debugging capabilities
6. Version persistence and management
7. Sunset date tracking
"""

import logging

logger = logging.getLogger(__name__)

from .version_manager import (
    version_manager,
    VersionedFeature,
    FeatureVersion,
    VersionCompatibility,
    VersionMetadata
)

from .middleware import (
    VersionHeaderMiddleware,
    VersionedAPIRouter,
    create_versioned_app
)

from .registry import (
    VersionedComponent,
    VersionedCoreNode,
    VersionedType,
    VersionedCoreNodeRegistry,
    VersionedTypeRegistry,
    core_node_registry,
    type_registry
)

from .migration import (
    MigrationStep,
    WorkflowMigrationStep,
    NodeMigrationStep,
    TypeMigrationStep,
    MigrationPlan,
    MigrationRegistry,
    migration_registry
)

from .api import (
    router as version_api_router,
    include_router as include_version_api
)

from .integration import (
    integrate_with_existing_app,
    get_versioned_component,
    register_existing_components
)

__all__ = [
    # Version Manager
    'version_manager',
    'VersionedFeature',
    'FeatureVersion',
    'VersionCompatibility',
    'VersionMetadata',

    # Middleware
    'VersionHeaderMiddleware',
    'VersionedAPIRouter',
    'create_versioned_app',

    # Registry
    'VersionedComponent',
    'VersionedCoreNode',
    'VersionedType',
    'VersionedCoreNodeRegistry',
    'VersionedTypeRegistry',
    'core_node_registry',
    'type_registry',

    # Migration
    'MigrationStep',
    'WorkflowMigrationStep',
    'NodeMigrationStep',
    'TypeMigrationStep',
    'MigrationPlan',
    'MigrationRegistry',
    'migration_registry',

    # API
    'version_api_router',
    'include_version_api',

    # Integration
    'integrate_with_existing_app',
    'get_versioned_component',
    'register_existing_components'
]

# Initialize the versioning system
def initialize_versioning(app=None, integrate_existing=False):
    """
    Initialize the versioning system.

    Args:
        app: Optional FastAPI application to include the version API
        integrate_existing: Whether to integrate with existing backend components
    """
    # Load existing version data or register initial version if none exists
    try:
        version_manager._load_version_data()
        logger.info("Loaded existing version data")
    except Exception:
        # Register initial version
        version_manager.register_version(
            "0.1.0",
            VersionMetadata(
                version="0.1.0",
                release_date="2023-01-01",
                features={
                    VersionedFeature.TYPE_SYSTEM: "0.1.0",
                    VersionedFeature.CORE_NODES: "0.1.0",
                    VersionedFeature.PLUGIN_SYSTEM: "0.1.0",
                    VersionedFeature.WORKFLOW_ENGINE: "0.1.0",
                    VersionedFeature.API: "0.1.0",
                    VersionedFeature.EXECUTION_ENGINE: "0.1.0",
                    VersionedFeature.VALIDATION_SYSTEM: "0.1.0"
                },
                description="Initial version of the Workflow Builder"
            )
        )
        logger.info("Registered initial version 0.1.0")

    # Discover core nodes
    core_node_registry.discover_nodes()

    # Discover types
    type_registry.discover_types()

    # Discover migrations
    migration_registry.discover_migrations()

    # Integrate with existing backend if requested
    if integrate_existing:
        try:
            register_existing_components()
        except Exception as e:
            logger.warning(f"Failed to register existing components: {e}")

    # Include version API if app is provided
    if app:
        if integrate_existing:
            # Use the integration module to integrate with existing app
            integrate_with_existing_app(app)
        else:
            # Just include the version API
            include_version_api(app)
        logger.info("Included version API in the application")
