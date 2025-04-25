"""
Version Management API

This module provides API endpoints for managing versions.
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from .version_manager import (
    version_manager,
    VersionedFeature,
    VersionMetadata,
    VersionCompatibility
)

logger = logging.getLogger(__name__)

# Request and response models
class VersionResponse(BaseModel):
    """Response model for version information."""
    version: str
    latest_version: str
    available_versions: List[str]

class FeatureVersionsResponse(BaseModel):
    """Response model for feature versions."""
    version: str
    features: Dict[str, str]

class VersionMetadataResponse(BaseModel):
    """Response model for version metadata."""
    version: str
    release_date: str
    description: str
    features: Dict[str, str]
    breaking_changes: List[str]
    deprecated_features: List[str]
    new_features: List[str]
    sunset_date: Optional[str] = None

class CompatibilityResponse(BaseModel):
    """Response model for compatibility information."""
    source_version: str
    target_version: str
    compatible: bool
    upgrade_path: List[str]
    breaking_changes: List[str]
    requires_migration: bool

class VersionRegistrationRequest(BaseModel):
    """Request model for registering a new version."""
    version: str
    release_date: str
    description: str
    features: Dict[str, str]
    breaking_changes: List[str] = []
    deprecated_features: List[str] = []
    new_features: List[str] = []
    sunset_date: Optional[str] = None

class SunsetDateRequest(BaseModel):
    """Request model for setting a sunset date."""
    sunset_date: str

# Create router
router = APIRouter(prefix="/api/versions", tags=["Versions"])

@router.get("/current", response_model=VersionResponse)
async def get_current_version():
    """Get the current API version."""
    return {
        "version": version_manager.current_version,
        "latest_version": version_manager.get_latest_version(),
        "available_versions": version_manager.list_available_versions()
    }

@router.get("/features", response_model=FeatureVersionsResponse)
async def get_features(version: Optional[str] = None):
    """
    Get the features available in a specific version.
    
    Args:
        version: The version to get features for (defaults to current)
    """
    version = version or version_manager.current_version
    
    features = {}
    for feature in VersionedFeature:
        try:
            features[feature.value] = version_manager.get_feature_version(feature, version)
        except ValueError:
            features[feature.value] = "not_available"
    
    return {
        "version": version,
        "features": features
    }

@router.get("/metadata/{version}", response_model=VersionMetadataResponse)
async def get_version_metadata(version: str):
    """
    Get metadata for a specific version.
    
    Args:
        version: The version to get metadata for
    """
    try:
        metadata = version_manager.get_version_metadata(version)
        
        # Convert features enum keys to strings
        features = {}
        for feature, feature_version in metadata.features.items():
            features[feature.value] = feature_version
        
        return {
            "version": metadata.version,
            "release_date": metadata.release_date,
            "description": metadata.description,
            "features": features,
            "breaking_changes": metadata.breaking_changes,
            "deprecated_features": metadata.deprecated_features,
            "new_features": metadata.new_features,
            "sunset_date": metadata.sunset_date
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/compatibility", response_model=CompatibilityResponse)
async def check_compatibility(
    source_version: str,
    target_version: Optional[str] = None
):
    """
    Check compatibility between versions.
    
    Args:
        source_version: The source version
        target_version: The target version (defaults to current)
    """
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

@router.post("/register", response_model=VersionMetadataResponse, status_code=201)
async def register_version(request: VersionRegistrationRequest):
    """
    Register a new version.
    
    This endpoint is typically used by administrators to register
    new versions of the system.
    """
    try:
        # Convert string feature keys to enum
        features = {}
        for feature_str, feature_version in request.features.items():
            try:
                feature = VersionedFeature(feature_str)
                features[feature] = feature_version
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid feature: {feature_str}"
                )
        
        # Create metadata
        metadata = VersionMetadata(
            version=request.version,
            release_date=request.release_date,
            features=features,
            description=request.description,
            breaking_changes=request.breaking_changes,
            deprecated_features=request.deprecated_features,
            new_features=request.new_features,
            sunset_date=request.sunset_date
        )
        
        # Register the version
        version_manager.register_version(request.version, metadata)
        
        # Return the registered metadata
        return await get_version_metadata(request.version)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/current/{version}")
async def set_current_version(version: str):
    """
    Set the current system version.
    
    This endpoint is typically used by administrators to change
    the current version of the system.
    """
    try:
        version_manager.set_current_version(version)
        return {"message": f"Current version set to {version}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/sunset/{version}")
async def set_sunset_date(version: str, request: SunsetDateRequest):
    """
    Set the sunset date for a specific version.
    
    This endpoint is typically used by administrators to set
    when a version will be removed.
    """
    try:
        version_manager.set_sunset_date(version, request.sunset_date)
        return {"message": f"Sunset date for version {version} set to {request.sunset_date}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def include_router(app):
    """Include the version management router in the app."""
    app.include_router(router)
