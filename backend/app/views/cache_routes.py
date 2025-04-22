"""
Cache Routes

This module provides routes for managing the node cache.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List

from backend.app.services.node_cache_service import NodeCacheService
from backend.app.models.responses import StandardResponse

router = APIRouter(prefix="/api/cache", tags=["cache"])

@router.get("/stats")
async def get_cache_stats() -> StandardResponse:
    """Get cache statistics."""
    cache_service = NodeCacheService()
    stats = cache_service.get_stats()
    return StandardResponse.success(data=stats)

@router.post("/configure")
async def configure_cache(config: Dict[str, Any]) -> StandardResponse:
    """Configure the cache service."""
    cache_service = NodeCacheService()
    cache_service.configure(config)
    return StandardResponse.success(message="Cache configured successfully")

@router.post("/clear")
async def clear_cache() -> StandardResponse:
    """Clear the cache."""
    cache_service = NodeCacheService()
    cache_service.clear()
    return StandardResponse.success(message="Cache cleared successfully")

@router.post("/cleanup")
async def cleanup_cache() -> StandardResponse:
    """Clean up expired cache entries."""
    cache_service = NodeCacheService()
    removed_count = cache_service.cleanup_expired()
    return StandardResponse.success(
        message=f"Removed {removed_count} expired cache entries",
        data={"removed_count": removed_count}
    )

@router.post("/cacheable-node-types")
async def set_cacheable_node_types(node_types: List[str]) -> StandardResponse:
    """Set the node types that can be cached."""
    cache_service = NodeCacheService()
    cache_service.cacheable_node_types = set(node_types)
    return StandardResponse.success(
        message=f"Set {len(node_types)} cacheable node types",
        data={"cacheable_node_types": node_types}
    )

@router.get("/cacheable-node-types")
async def get_cacheable_node_types() -> StandardResponse:
    """Get the node types that can be cached."""
    cache_service = NodeCacheService()
    return StandardResponse.success(
        data={"cacheable_node_types": list(cache_service.cacheable_node_types)}
    )
