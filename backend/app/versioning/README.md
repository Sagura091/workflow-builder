# Revolutionary Version Infrastructure for Workflow Builder

This package provides a sophisticated version management system for the Workflow Builder backend. It enables seamless evolution of the backend while maintaining backward compatibility.

## Core Features

### 1. Dynamic Version Resolution

Instead of hard-coded version paths, the system implements a dynamic resolution system that can adapt to any number of versions. This allows for:

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

## Directory Structure

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

## Usage Examples

### Registering a New Version

```python
from backend.app.versioning import version_manager, VersionedFeature, VersionMetadata

# Register a new system version
version_manager.register_version(
    "0.2.0",
    VersionMetadata(
        version="0.2.0",
        release_date="2023-02-01",
        features={
            VersionedFeature.TYPE_SYSTEM: "0.2.0",
            VersionedFeature.CORE_NODES: "0.2.0",
            VersionedFeature.PLUGIN_SYSTEM: "0.1.0",  # Still using v0.1.0
            VersionedFeature.WORKFLOW_ENGINE: "0.2.0",
            VersionedFeature.API: "0.2.0",
            VersionedFeature.EXECUTION_ENGINE: "0.2.0",
            VersionedFeature.VALIDATION_SYSTEM: "0.1.0"  # Still using v0.1.0
        },
        description="Enhanced version with improved type system and core nodes",
        new_features=["Enhanced type system", "Additional core nodes"],
        deprecated_features=["Legacy validation system"]
    )
)
```

### Creating a Versioned API Endpoint

```python
from fastapi import FastAPI, Request
from backend.app.versioning import VersionedAPIRouter

app = FastAPI()

@app.get(
    "/api/workflow/{workflow_id}",
    route_class=VersionedAPIRouter,
    version_handlers={
        "0.1.0": get_workflow_v0_1_0,
        "0.2.0": get_workflow_v0_2_0
    }
)
async def get_workflow(request: Request, workflow_id: str):
    """Get a workflow by ID."""
    # Default implementation (latest version)
    return await get_workflow_v0_2_0(request, workflow_id)

async def get_workflow_v0_1_0(request: Request, workflow_id: str):
    """v0.1.0 implementation."""
    # Implementation for v0.1.0
    ...

async def get_workflow_v0_2_0(request: Request, workflow_id: str):
    """v0.2.0 implementation."""
    # Implementation for v0.2.0
    ...
```

### Using Version-Aware Dependency Injection

```python
from backend.app.versioning import version_manager, VersionedFeature

# Get the appropriate type validator for the current version
type_validator = version_manager.get_component(
    VersionedFeature.TYPE_SYSTEM,
    "TypeValidator"
)

# Create an instance
validator = type_validator()

# Validate a value
result = validator.validate("string", "Hello, World!")
```

### Creating a Migration Step

```python
from typing import Dict, Any
from backend.app.versioning.migration import WorkflowMigrationStep

class UpdateNodeConfigMigration(WorkflowMigrationStep):
    """Migration step to update node configuration format."""

    def __init__(self):
        super().__init__(
            source_version="0.1.0",
            target_version="0.2.0",
            description="Update node configuration format",
            breaking=False
        )

    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the migration step."""
        result = data.copy()

        # Update node configurations
        if "nodes" in result:
            for node in result["nodes"]:
                if "config" in node:
                    # Transform the config from v0.1.0 to v0.2.0 format
                    node["config"] = self._transform_config(node["config"])

        return result

    def _transform_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a node configuration from v0.1.0 to v0.2.0 format."""
        # Implementation of the transformation
        ...
```

## Best Practices

1. **Always register new versions** before adding new components
2. **Use semantic versioning** for all version numbers
3. **Document breaking changes** in version metadata
4. **Provide migration steps** for all version transitions
5. **Test compatibility** between versions
6. **Use version decorators** to mark version information on functions and classes
7. **Implement fallbacks** for backward compatibility

## Conclusion

This revolutionary version infrastructure provides a solid foundation for evolving the Workflow Builder backend while maintaining backward compatibility. It enables seamless upgrades, feature experimentation, and robust version management.
