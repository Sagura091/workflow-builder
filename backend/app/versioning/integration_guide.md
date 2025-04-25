# Integrating the Versioning System

This guide provides step-by-step instructions for integrating the revolutionary versioning system into your existing Workflow Builder backend.

## Prerequisites

Before integrating the versioning system, ensure you have:

1. A working Workflow Builder backend
2. Python 3.8 or higher
3. FastAPI installed

## Integration Steps

### 1. Install Required Dependencies

```bash
pip install semver pydantic
```

### 2. Copy the Versioning Package

Copy the entire `backend/app/versioning` directory to your project.

### 3. Create Directory Structure for Versioned Components

Create the following directory structure for your versioned components:

```
backend/
├── app/
│   ├── types/
│   │   └── v0_1_0/  # Initial version of your types
│   │       ├── __init__.py
│   │       └── type_defs.py
│   └── migrations/
│       └── __init__.py
└── core_nodes/
    └── v0_1_0/  # Initial version of your core nodes
        ├── __init__.py
        └── flow/
            ├── __init__.py
            └── node_info.py
```

### 4. Migrate Existing Types

1. Create a `type_defs.py` file in `backend/app/types/v0_1_0/` with your existing types
2. Format your types according to the expected structure:

```python
# backend/app/types/v0_1_0/type_defs.py

TYPE_DEFS = {
    "string": {
        "name": "String",
        "introduced_in": "0.1.0",
        "validators": [],
        "converters": {}
    },
    # Add your other types here
}
```

### 5. Migrate Existing Core Nodes

1. Create a `node_info.py` file in appropriate category directories under `backend/core_nodes/v0_1_0/`
2. Format your nodes according to the expected structure:

```python
# backend/core_nodes/v0_1_0/flow/node_info.py

NODE_INFO = {
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
    # Add your other nodes here
}

def get_implementation(node_id: str):
    # Return the implementation function for each node
    pass
```

### 6. Create a Versioned Main Application

Create a new main application file that uses the versioning system:

```python
# backend/main_versioned.py

from fastapi import FastAPI, Request
from app.versioning import (
    version_manager,
    create_versioned_app,
    initialize_versioning
)

# Initialize the versioning system
initialize_versioning()

# Create the FastAPI application with versioning
app = create_versioned_app(
    title="Workflow Builder API",
    description="API for the Workflow Builder with revolutionary versioning",
    version="0.1.0",
    default_api_version="0.1.0"
)

# Add your routes here
# ...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 7. Convert Existing Routes to Versioned Routes

For each existing route, convert it to a versioned route:

```python
from app.versioning import VersionedAPIRouter

@app.get(
    "/api/nodes",
    route_class=VersionedAPIRouter,
    version_handlers={
        "0.1.0": get_nodes_v0_1_0
    }
)
async def get_nodes(request: Request):
    return get_nodes_v0_1_0(request)

async def get_nodes_v0_1_0(request: Request):
    # Your existing implementation
    pass
```

### 8. Test the Integration

Run your versioned application:

```bash
python backend/main_versioned.py
```

Test the API endpoints with different version headers:

```bash
curl -H "X-API-Version: 0.1.0" http://localhost:8000/api/version
```

## Gradual Migration Strategy

You can gradually migrate your application to use the versioning system:

1. Start by running both the original and versioned applications side by side
2. Migrate one endpoint at a time to the versioned system
3. Test thoroughly after each migration
4. Once all endpoints are migrated, switch to using only the versioned application

## Advanced Integration

### Adding a New Version

When you're ready to add a new version:

1. Create new directories for the new version (e.g., `v0_2_0`)
2. Register the new version with the version manager
3. Create migration steps for upgrading from the previous version
4. Add version handlers for your API endpoints

```python
from app.versioning import version_manager, VersionedFeature, VersionMetadata

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

### Creating Migration Steps

Create migration steps for upgrading workflows between versions:

```python
from typing import Dict, Any
from app.versioning.migration import WorkflowMigrationStep

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
        pass

# Add to a migration module
MIGRATION_STEPS = [
    UpdateNodeConfigMigration()
]
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure your import paths are correct and match your project structure
2. **Version Not Found**: Make sure you've registered all versions with the version manager
3. **Component Not Found**: Check that your component directories follow the expected structure
4. **Migration Failures**: Test your migration steps thoroughly with sample data

### Getting Help

If you encounter issues with the versioning system:

1. Check the logs for detailed error messages
2. Review the versioning system documentation
3. Ensure all required dependencies are installed
4. Verify your directory structure matches the expected format
