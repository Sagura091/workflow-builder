# Workflow Builder Versioning System

This document provides comprehensive documentation for the revolutionary versioning system implemented in the Workflow Builder backend.

## Overview

The versioning system enables seamless evolution of the backend while maintaining backward compatibility. It provides a robust framework for managing different versions of components, migrating workflows between versions, and ensuring compatibility across the system.

## Key Features

### 1. Dynamic Version Resolution

The system implements a dynamic resolution mechanism that can adapt to any number of versions. This allows for:

- Automatic discovery of versioned components
- Runtime resolution of the appropriate component version
- Graceful fallbacks when specific versions are not available

### 2. Semantic Versioning with Feature Flags

The system combines semantic versioning with feature flags to allow granular control over features across versions:

- Each feature area (type system, core nodes, etc.) can evolve independently
- Features can be introduced, deprecated, and removed on different schedules
- The system tracks compatibility between versions

### 3. Automatic Compatibility Analysis

The system provides automatic compatibility detection to determine if workflows can be upgraded:

- Compatibility checking between any two versions
- Identification of breaking changes
- Generation of upgrade paths when direct migration is not possible

### 4. Version-Aware Dependency Injection

The system includes a dependency injection mechanism that automatically provides the correct version of components:

- Components are loaded dynamically based on the requested version
- Version-specific implementations can coexist
- Decorators for marking version information on functions and classes

### 5. Time-Travel Debugging

The system allows developers to debug workflows in the context of any previous version:

- Switch between versions at runtime
- Test workflows against different backend versions
- Identify version-specific issues

### 6. Version Persistence

The system includes mechanisms for persisting version information:

- Save and load version data from disk
- Track version metadata
- Manage version compatibility information

### 7. Sunset Date Tracking

The system includes support for tracking sunset dates for versions:

- Set and retrieve sunset dates for versions
- Automatically include sunset information in API responses
- Notify users of upcoming version removals

## Architecture

### Directory Structure

The versioning system uses a consistent directory structure for versioned components:

```
backend/
├── main.py  # Original main application
├── main_versioned.py  # Main application with versioning
├── app/
│   ├── types/
│   │   ├── v0_1_0/  # Initial type system
│   │   │   ├── type_defs.py
│   │   │   └── ...
│   │   └── v0_2_0/  # Enhanced type system
│   │       ├── type_defs.py
│   │       └── ...
│   ├── migrations/
│   │   ├── v0_1_0_to_v0_2_0/  # Migration steps between versions
│   │   │   ├── workflow_migration.py
│   │   │   └── ...
│   │   └── ...
│   └── versioning/  # The versioning infrastructure
│       ├── version_manager.py
│       ├── middleware.py
│       ├── registry.py
│       ├── migration.py
│       └── ...
└── core_nodes/
    ├── v0_1_0/  # Initial core nodes
    │   ├── flow/
    │   │   ├── node_info.py
    │   │   └── ...
    │   └── ...
    └── v0_2_0/  # Enhanced core nodes
        ├── flow/
        │   ├── node_info.py
        │   └── ...
        └── ...
```

### Component Versioning

Each component in the system can be versioned independently:

- **Types**: Different versions of types can coexist, with automatic conversion between compatible types
- **Core Nodes**: Different versions of core nodes can be used in the same workflow
- **Plugins**: Plugins can specify which versions of the system they are compatible with
- **API Endpoints**: API endpoints can have different implementations for different versions

### Version Manager

The Version Manager is the central component of the versioning system. It:

- Manages version metadata
- Tracks feature versions
- Checks compatibility between versions
- Provides version-aware dependency injection

### Migration System

The Migration System enables upgrading workflows between versions:

- Migration steps define how to transform workflows from one version to another
- Migration plans combine multiple steps to create a complete upgrade path
- Automatic detection of breaking changes

### API Versioning

The API Versioning system ensures that clients can interact with the appropriate version of the API:

- Version detection from headers, URL, or query parameters
- Version negotiation
- Compatibility information in responses

## Version 0.1.0

The initial version of the Workflow Builder includes:

### Types

- string
- number
- boolean
- array
- object
- any

### Core Nodes

- flow.begin
- flow.end
- flow.branch

## Version 0.2.0

Version 0.2.0 enhances the Workflow Builder with:

### Types

All types from v0.1.0, plus:

- integer
- float
- date
- time
- datetime
- email
- url
- file
- image
- audio
- video
- color
- regex
- json
- xml
- html
- markdown
- css
- javascript
- python

### Core Nodes

All nodes from v0.1.0, plus:

#### Flow Control

- flow.switch
- flow.for_each
- flow.while
- flow.delay
- flow.parallel
- flow.join
- flow.try_catch

#### Data Handling

- data.variable
- data.get_property
- data.set_property
- data.array_item
- data.array_length
- data.array_push
- data.array_pop
- data.array_filter
- data.array_map
- data.object_keys
- data.object_values
- data.object_entries
- data.json_parse
- data.json_stringify

### Migration Steps

- UpdateWorkflowMetadataMigration
- UpdateNodeTypesMigration
- UpdateConnectionsMigration

## API Reference

### Version Manager

```python
from backend.app.versioning import version_manager

# Register a new version
version_manager.register_version(
    "0.2.0",
    VersionMetadata(
        version="0.2.0",
        release_date="2023-02-01",
        features={
            VersionedFeature.TYPE_SYSTEM: "0.2.0",
            VersionedFeature.CORE_NODES: "0.2.0",
            VersionedFeature.PLUGIN_SYSTEM: "0.1.0",
            VersionedFeature.WORKFLOW_ENGINE: "0.2.0",
            VersionedFeature.API: "0.2.0",
            VersionedFeature.EXECUTION_ENGINE: "0.2.0",
            VersionedFeature.VALIDATION_SYSTEM: "0.1.0"
        },
        description="Enhanced version with improved type system and core nodes",
        new_features=["Enhanced type system", "Additional core nodes"],
        deprecated_features=["Legacy validation system"],
        sunset_date="2024-02-01"
    )
)

# Get the current version
current_version = version_manager.current_version

# Get the latest version
latest_version = version_manager.get_latest_version()

# List available versions
versions = version_manager.list_available_versions()

# Check compatibility between versions
compatibility = version_manager.check_compatibility("0.1.0", "0.2.0")

# Get a feature version
type_system_version = version_manager.get_feature_version(
    VersionedFeature.TYPE_SYSTEM,
    "0.2.0"
)

# Get a component
type_validator = version_manager.get_component(
    VersionedFeature.TYPE_SYSTEM,
    "TypeValidator",
    "0.2.0"
)

# Set the current version
version_manager.set_current_version("0.2.0")

# Get sunset date
sunset_date = version_manager.get_sunset_date("0.1.0")

# Set sunset date
version_manager.set_sunset_date("0.1.0", "2024-01-01")
```

### Core Node Registry

```python
from backend.app.versioning import core_node_registry, VersionedCoreNode

# Register a core node
core_node_registry.register_node(
    VersionedCoreNode(
        id="flow.switch",
        name="Switch",
        version="0.2.0",
        introduced_in="0.2.0",
        category="Flow Control",
        description="Branch execution based on a value",
        inputs={
            "flow": "flow",
            "value": "any"
        },
        outputs={
            "case1": "flow",
            "case2": "flow",
            "case3": "flow",
            "default": "flow"
        },
        config_schema={}
    )
)

# Get a core node
node = core_node_registry.get_node("flow.switch", "0.2.0")

# List core nodes
nodes = core_node_registry.list_nodes(category="Flow Control", system_version="0.2.0")

# List categories
categories = core_node_registry.list_categories(system_version="0.2.0")
```

### Type Registry

```python
from backend.app.versioning import type_registry, VersionedType

# Register a type
type_registry.register_type(
    VersionedType(
        id="integer",
        name="Integer",
        version="0.2.0",
        introduced_in="0.2.0",
        base_type="number",
        validators=[],
        converters={}
    )
)

# Get a type
type_def = type_registry.get_type("integer", "0.2.0")

# List types
types = type_registry.list_types(system_version="0.2.0")
```

### Migration Registry

```python
from backend.app.versioning.migration import (
    migration_registry,
    WorkflowMigrationStep
)

# Create a migration step
class MyMigrationStep(WorkflowMigrationStep):
    def __init__(self):
        super().__init__(
            source_version="0.1.0",
            target_version="0.2.0",
            description="My migration step",
            breaking=False
        )
    
    def apply(self, data):
        # Apply migration
        return data

# Register a migration step
migration_registry.register_step(MyMigrationStep())

# Create a migration plan
plan = migration_registry.create_migration_plan("0.1.0", "0.2.0")

# Migrate a workflow
migrated_workflow = migration_registry.migrate_workflow(
    workflow,
    "0.1.0",
    "0.2.0"
)
```

### API Versioning

```python
from fastapi import FastAPI
from backend.app.versioning import (
    create_versioned_app,
    VersionedAPIRouter
)

# Create a versioned app
app = create_versioned_app(
    title="Workflow Builder API",
    description="API for the Workflow Builder",
    version="0.2.0",
    default_api_version="0.2.0"
)

# Create a versioned route
@app.get(
    "/api/workflow/{workflow_id}",
    route_class=VersionedAPIRouter,
    version_handlers={
        "0.1.0": get_workflow_v0_1_0,
        "0.2.0": get_workflow_v0_2_0
    }
)
async def get_workflow(request, workflow_id):
    # Default implementation
    return await get_workflow_v0_2_0(request, workflow_id)
```

## Best Practices

### 1. Always Use Semantic Versioning

Follow the [Semantic Versioning](https://semver.org/) specification:

- MAJOR version for incompatible API changes
- MINOR version for backward-compatible functionality
- PATCH version for backward-compatible bug fixes

### 2. Document Breaking Changes

Always document breaking changes in version metadata:

```python
version_manager.register_version(
    "1.0.0",
    VersionMetadata(
        version="1.0.0",
        release_date="2023-03-01",
        features={...},
        description="First major release",
        breaking_changes=[
            "Removed deprecated API endpoints",
            "Changed workflow format"
        ]
    )
)
```

### 3. Provide Migration Steps

Always provide migration steps for upgrading between versions:

```python
class UpdateWorkflowFormatMigration(WorkflowMigrationStep):
    def __init__(self):
        super().__init__(
            source_version="0.2.0",
            target_version="1.0.0",
            description="Update workflow format",
            breaking=True
        )
    
    def apply(self, data):
        # Apply migration
        return data
```

### 4. Use Version-Aware Components

Always use version-aware components:

```python
# Get the appropriate component for the current version
validator = version_manager.get_component(
    VersionedFeature.TYPE_SYSTEM,
    "TypeValidator"
)
```

### 5. Test Compatibility

Always test compatibility between versions:

```python
compatibility = version_manager.check_compatibility("0.1.0", "0.2.0")
if not compatibility.compatible:
    print(f"Incompatible: {compatibility.breaking_changes}")
```

### 6. Set Sunset Dates

Always set sunset dates for deprecated versions:

```python
version_manager.set_sunset_date("0.1.0", "2024-01-01")
```

## Troubleshooting

### Common Issues

1. **Version Not Found**: Ensure the version is registered with the version manager
2. **Component Not Found**: Check that the component is registered with the appropriate registry
3. **Incompatible Versions**: Check the compatibility matrix and migration steps
4. **Missing Migration Steps**: Ensure migration steps are registered for all version transitions

### Debugging

1. **Check Version Information**: Use the version manager to check version information
2. **Inspect Component Registries**: Check the core node and type registries
3. **Test Migration Steps**: Test migration steps with sample workflows
4. **Check API Versioning**: Verify that API endpoints are properly versioned

## Conclusion

The revolutionary versioning system provides a solid foundation for evolving the Workflow Builder backend while maintaining backward compatibility. It enables seamless upgrades, feature experimentation, and robust version management.
