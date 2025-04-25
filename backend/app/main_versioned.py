"""
Main Application Module with Versioning

This module initializes the FastAPI application with the revolutionary versioning system.
"""

import logging
from fastapi import FastAPI, Depends, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any

from .versioning import (
    version_manager,
    VersionedFeature,
    create_versioned_app,
    VersionedAPIRouter,
    core_node_registry,
    type_registry,
    initialize_versioning
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the versioning system
initialize_versioning()

# Create the FastAPI application with versioning
app = create_versioned_app(
    title="Workflow Builder API",
    description="API for the Workflow Builder with revolutionary versioning",
    version="0.1.0",
    default_api_version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define API routes
@app.get("/api/version")
async def get_version():
    """Get the current API version."""
    return {
        "version": version_manager.current_version,
        "latest_version": version_manager.get_latest_version(),
        "available_versions": version_manager.list_available_versions()
    }

@app.get("/api/features")
async def get_features():
    """Get the features available in the current version."""
    features = {}
    for feature in VersionedFeature:
        features[feature.value] = version_manager.get_feature_version(feature)
    
    return {
        "version": version_manager.current_version,
        "features": features
    }

# Example of a versioned route
@app.get(
    "/api/nodes",
    response_model=List[Dict[str, Any]],
    route_class=VersionedAPIRouter,
    version_handlers={
        "0.1.0": lambda request: get_nodes_v0_1_0(request),
        "0.2.0": lambda request: get_nodes_v0_2_0(request)
    }
)
async def get_nodes(request: Request):
    """
    Get all available nodes.
    
    This is a versioned endpoint that returns different results
    based on the requested API version.
    """
    # Default implementation (latest version)
    return get_nodes_v0_1_0(request)

async def get_nodes_v0_1_0(request: Request):
    """Get nodes implementation for v0.1.0."""
    # Get the API version from request state
    api_version = getattr(request.state, "api_version", "0.1.0")
    
    # Get all nodes available in this version
    nodes = core_node_registry.list_nodes(system_version=api_version)
    
    # Convert to dict for response
    result = []
    for node in nodes:
        result.append({
            "id": node.id,
            "name": node.name,
            "category": node.category,
            "description": node.description,
            "inputs": node.inputs,
            "outputs": node.outputs,
            "config_schema": node.config_schema,
            "version": node.version
        })
    
    return result

async def get_nodes_v0_2_0(request: Request):
    """Get nodes implementation for v0.2.0."""
    # This would be a more advanced implementation for v0.2.0
    # For now, just add an extra field to the v0.1.0 response
    nodes = await get_nodes_v0_1_0(request)
    
    # Add extra information for v0.2.0
    for node in nodes:
        node["api_version"] = "0.2.0"
        node["deprecated"] = False
    
    return nodes

@app.get("/api/types")
async def get_types(request: Request):
    """Get all available types."""
    # Get the API version from request state
    api_version = getattr(request.state, "api_version", "0.1.0")
    
    # Get all types available in this version
    types = type_registry.list_types(system_version=api_version)
    
    # Convert to dict for response
    result = []
    for type_def in types:
        result.append({
            "id": type_def.id,
            "name": type_def.name,
            "version": type_def.version,
            "base_type": type_def.base_type
        })
    
    return result

@app.get("/api/compatibility")
async def check_compatibility(
    source_version: str,
    target_version: Optional[str] = None
):
    """Check compatibility between versions."""
    target_version = target_version or version_manager.current_version
    
    try:
        compatibility = version_manager.check_compatibility(source_version, target_version)
        
        return {
            "source_version": compatibility.source_version,
            "target_version": compatibility.target_version,
            "compatible": compatibility.compatible,
            "upgrade_path": compatibility.upgrade_path,
            "breaking_changes": compatibility.breaking_changes,
            "requires_migration": compatibility.requires_migration
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Add more routes as needed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
