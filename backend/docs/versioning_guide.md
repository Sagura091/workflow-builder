# Workflow Builder Versioning Guide

This guide provides step-by-step instructions for developers on how to use the versioning system in the Workflow Builder backend.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Creating a New Version](#creating-a-new-version)
4. [Adding New Types](#adding-new-types)
5. [Adding New Core Nodes](#adding-new-core-nodes)
6. [Creating Migration Steps](#creating-migration-steps)
7. [Versioning API Endpoints](#versioning-api-endpoints)
8. [Testing Versioned Components](#testing-versioned-components)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Introduction

The Workflow Builder uses a revolutionary versioning system that enables seamless evolution of the backend while maintaining backward compatibility. This guide will help you understand how to use this system effectively.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- FastAPI
- Pydantic
- Semver

### Installation

The versioning system is included in the Workflow Builder backend. No additional installation is required.

### Basic Concepts

- **Version**: A specific release of the Workflow Builder, identified by a semantic version number (e.g., "0.2.0")
- **Feature**: A specific area of functionality (e.g., type system, core nodes)
- **Component**: A specific piece of functionality (e.g., a type, a core node)
- **Migration**: A process for upgrading workflows from one version to another

## Creating a New Version

### Step 1: Plan Your Version

Before creating a new version, plan what changes you want to make:

- What new features will you add?
- What existing features will you enhance?
- What features will you deprecate or remove?
- Will there be any breaking changes?

### Step 2: Register the New Version

```python
from backend.app.versioning import version_manager, VersionedFeature, VersionMetadata

# Register a new version
version_manager.register_version(
    "0.3.0",
    VersionMetadata(
        version="0.3.0",
        release_date="2023-03-01",
        features={
            VersionedFeature.TYPE_SYSTEM: "0.3.0",
            VersionedFeature.CORE_NODES: "0.3.0",
            VersionedFeature.PLUGIN_SYSTEM: "0.2.0",
            VersionedFeature.WORKFLOW_ENGINE: "0.3.0",
            VersionedFeature.API: "0.3.0",
            VersionedFeature.EXECUTION_ENGINE: "0.3.0",
            VersionedFeature.VALIDATION_SYSTEM: "0.2.0"
        },
        description="Enhanced version with improved workflow engine",
        new_features=["Enhanced workflow engine", "Additional core nodes"],
        deprecated_features=["Legacy validation system"],
        breaking_changes=[]
    )
)
```

### Step 3: Create Directory Structure

Create the appropriate directory structure for your new version:

```
backend/
├── app/
│   ├── types/
│   │   └── v0_3_0/
│   │       ├── __init__.py
│   │       └── type_defs.py
│   └── migrations/
│       └── v0_2_0_to_v0_3_0/
│           ├── __init__.py
│           └── workflow_migration.py
└── core_nodes/
    └── v0_3_0/
        ├── __init__.py
        ├── flow/
        │   ├── __init__.py
        │   └── node_info.py
        └── data/
            ├── __init__.py
            └── node_info.py
```

## Adding New Types

### Step 1: Create Type Definitions

Create a `type_defs.py` file in the appropriate version directory:

```python
# backend/app/types/v0_3_0/type_defs.py

from typing import Any, Dict, List, Optional, Union, Callable

# Define the types
TYPE_DEFS: Dict[str, Dict[str, Any]] = {
    # Include types from previous versions
    "string": {
        "name": "String",
        "introduced_in": "0.1.0",
        "validators": [],
        "converters": {}
    },
    # ... other existing types ...
    
    # Add new types
    "decimal": {
        "name": "Decimal",
        "introduced_in": "0.3.0",
        "base_type": "number",
        "validators": [],
        "converters": {}
    },
    "uuid": {
        "name": "UUID",
        "introduced_in": "0.3.0",
        "validators": [],
        "converters": {}
    }
}
```

### Step 2: Register Types with the Registry

The types will be automatically registered when the versioning system is initialized. You can also register them manually:

```python
from backend.app.versioning import type_registry, VersionedType

# Register a type
type_registry.register_type(
    VersionedType(
        id="decimal",
        name="Decimal",
        version="0.3.0",
        introduced_in="0.3.0",
        base_type="number",
        validators=[],
        converters={}
    )
)
```

## Adding New Core Nodes

### Step 1: Create Node Information

Create a `node_info.py` file in the appropriate version directory:

```python
# backend/core_nodes/v0_3_0/flow/node_info.py

from typing import Any, Dict, Callable

# Define the flow control nodes
NODE_INFO: Dict[str, Dict[str, Any]] = {
    # Include nodes from previous versions
    "flow.begin": {
        "name": "Begin",
        "introduced_in": "0.1.0",
        "category": "Flow Control",
        "description": "Starting point for workflow execution",
        "inputs": {},
        "outputs": {
            "flow": "flow"
        },
        "config_schema": {}
    },
    # ... other existing nodes ...
    
    # Add new nodes
    "flow.state_machine": {
        "name": "State Machine",
        "introduced_in": "0.3.0",
        "category": "Flow Control",
        "description": "Implement a state machine",
        "inputs": {
            "flow": "flow",
            "state": "string",
            "event": "string"
        },
        "outputs": {
            "state1": "flow",
            "state2": "flow",
            "state3": "flow"
        },
        "config_schema": {
            "transitions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "from_state": {
                            "type": "string"
                        },
                        "event": {
                            "type": "string"
                        },
                        "to_state": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    }
}

def get_implementation(node_id: str) -> Callable:
    """
    Get the implementation function for a node.
    
    Args:
        node_id: The ID of the node
        
    Returns:
        The implementation function
    """
    if node_id == "flow.state_machine":
        def state_machine_impl(inputs, config):
            state = inputs.get("state", "")
            event = inputs.get("event", "")
            transitions = config.get("transitions", [])
            
            # Find matching transition
            for transition in transitions:
                if (transition.get("from_state") == state and
                    transition.get("event") == event):
                    to_state = transition.get("to_state", "")
                    return {to_state: None}
            
            # No matching transition
            return {}
        return state_machine_impl
    # ... implementations for other nodes ...
    else:
        # Fall back to previous version
        from backend.core_nodes.v0_2_0.flow.node_info import get_implementation as get_impl_v0_2_0
        try:
            return get_impl_v0_2_0(node_id)
        except ValueError:
            raise ValueError(f"Unknown node ID: {node_id}")
```

### Step 2: Register Nodes with the Registry

The nodes will be automatically registered when the versioning system is initialized. You can also register them manually:

```python
from backend.app.versioning import core_node_registry, VersionedCoreNode

# Register a core node
core_node_registry.register_node(
    VersionedCoreNode(
        id="flow.state_machine",
        name="State Machine",
        version="0.3.0",
        introduced_in="0.3.0",
        category="Flow Control",
        description="Implement a state machine",
        inputs={
            "flow": "flow",
            "state": "string",
            "event": "string"
        },
        outputs={
            "state1": "flow",
            "state2": "flow",
            "state3": "flow"
        },
        config_schema={
            "transitions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "from_state": {
                            "type": "string"
                        },
                        "event": {
                            "type": "string"
                        },
                        "to_state": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    )
)
```

## Creating Migration Steps

### Step 1: Create Migration Module

Create a migration module for upgrading from the previous version:

```python
# backend/app/migrations/v0_2_0_to_v0_3_0/workflow_migration.py

from typing import Any, Dict, List

from backend.app.versioning.migration import WorkflowMigrationStep

class UpdateWorkflowEngineMigration(WorkflowMigrationStep):
    """Migration step to update workflow engine."""
    
    def __init__(self):
        super().__init__(
            source_version="0.2.0",
            target_version="0.3.0",
            description="Update workflow engine",
            breaking=False
        )
    
    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the migration step."""
        result = data.copy()
        
        # Update workflow engine version
        if "metadata" in result:
            metadata = result["metadata"]
            metadata["engine_version"] = "0.3.0"
        
        return result

# List of migration steps
MIGRATION_STEPS = [
    UpdateWorkflowEngineMigration()
]
```

### Step 2: Register Migration Steps

The migration steps will be automatically registered when the versioning system is initialized. You can also register them manually:

```python
from backend.app.versioning.migration import migration_registry

# Register a migration step
migration_registry.register_step(UpdateWorkflowEngineMigration())
```

## Versioning API Endpoints

### Step 1: Create Versioned Endpoint

```python
from fastapi import FastAPI, Request
from backend.app.versioning import VersionedAPIRouter

# Create a versioned route
@app.get(
    "/api/workflow/{workflow_id}",
    route_class=VersionedAPIRouter,
    version_handlers={
        "0.2.0": get_workflow_v0_2_0,
        "0.3.0": get_workflow_v0_3_0
    }
)
async def get_workflow(request: Request, workflow_id: str):
    """Get a workflow by ID."""
    # Default implementation (latest version)
    return await get_workflow_v0_3_0(request, workflow_id)

async def get_workflow_v0_2_0(request: Request, workflow_id: str):
    """v0.2.0 implementation."""
    # Implementation for v0.2.0
    ...

async def get_workflow_v0_3_0(request: Request, workflow_id: str):
    """v0.3.0 implementation."""
    # Implementation for v0.3.0
    ...
```

### Step 2: Use Version-Aware Components

```python
from backend.app.versioning import version_manager, VersionedFeature

async def get_workflow_v0_3_0(request: Request, workflow_id: str):
    """v0.3.0 implementation."""
    # Get the API version from request state
    api_version = getattr(request.state, "api_version", "0.3.0")
    
    # Get the appropriate workflow engine for this version
    workflow_engine = version_manager.get_component(
        VersionedFeature.WORKFLOW_ENGINE,
        "WorkflowEngine",
        api_version
    )
    
    # Use the workflow engine
    workflow = workflow_engine.get_workflow(workflow_id)
    
    return workflow
```

## Testing Versioned Components

### Step 1: Create Test Data

```python
# Test data for v0.2.0
workflow_v0_2_0 = {
    "version": "0.2.0",
    "metadata": {
        "name": "Test Workflow",
        "description": "A test workflow"
    },
    "nodes": [
        {
            "id": "node1",
            "type": "flow.begin",
            "position": {"x": 100, "y": 100}
        },
        {
            "id": "node2",
            "type": "flow.end",
            "position": {"x": 300, "y": 100}
        }
    ],
    "connections": [
        {
            "id": "conn1",
            "from_node": "node1",
            "from_output": "flow",
            "to_node": "node2",
            "to_input": "flow"
        }
    ]
}
```

### Step 2: Test Migration

```python
from backend.app.versioning.migration import migration_registry

# Migrate the workflow
workflow_v0_3_0 = migration_registry.migrate_workflow(
    workflow_v0_2_0,
    "0.2.0",
    "0.3.0"
)

# Verify the migration
assert workflow_v0_3_0["version"] == "0.3.0"
assert "engine_version" in workflow_v0_3_0["metadata"]
assert workflow_v0_3_0["metadata"]["engine_version"] == "0.3.0"
```

### Step 3: Test Compatibility

```python
from backend.app.versioning import version_manager

# Check compatibility
compatibility = version_manager.check_compatibility("0.2.0", "0.3.0")

# Verify compatibility
assert compatibility.compatible
assert len(compatibility.breaking_changes) == 0
assert len(compatibility.upgrade_path) > 0
```

## Best Practices

### 1. Follow Semantic Versioning

- MAJOR version for incompatible API changes
- MINOR version for backward-compatible functionality
- PATCH version for backward-compatible bug fixes

### 2. Document Changes

- Document new features
- Document deprecated features
- Document breaking changes
- Document migration steps

### 3. Provide Fallbacks

- Always provide fallbacks for backward compatibility
- Use graceful degradation for missing features

### 4. Test Thoroughly

- Test migration steps
- Test compatibility
- Test versioned API endpoints
- Test with real workflows

### 5. Use Version-Aware Components

- Always use version-aware components
- Use the version manager to get the appropriate component version

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

By following this guide, you should be able to effectively use the versioning system in the Workflow Builder backend. Remember to always plan your versions carefully, provide migration steps, and test thoroughly.
