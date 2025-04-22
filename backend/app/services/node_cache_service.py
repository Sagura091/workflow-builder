"""
Node Cache Service

This module provides caching for node execution results to improve performance.
"""

import time
import logging
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple, Set
from collections import OrderedDict
from datetime import datetime, timedelta

logger = logging.getLogger("workflow_builder")

class CacheEntry:
    """Cache entry for node execution results."""
    
    def __init__(self, key: str, value: Any, ttl: Optional[int] = None):
        """Initialize a cache entry.
        
        Args:
            key: The cache key
            value: The cached value
            ttl: Time to live in seconds (None for no expiration)
        """
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.ttl = ttl
        self.access_count = 0
    
    def is_expired(self) -> bool:
        """Check if the entry is expired."""
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)
    
    def access(self) -> None:
        """Mark the entry as accessed."""
        self.last_accessed = time.time()
        self.access_count += 1

class NodeCacheService:
    """Service for caching node execution results."""
    
    _instance = None
    
    def __new__(cls):
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super(NodeCacheService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the cache service."""
        # Cache configuration
        self.max_size = 1000  # Maximum number of entries
        self.default_ttl = 3600  # Default TTL in seconds (1 hour)
        
        # Cache storage
        self.cache: Dict[str, CacheEntry] = OrderedDict()
        
        # Cache statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        # Node types to cache
        self.cacheable_node_types: Set[str] = set()
        
        logger.info("Node cache service initialized")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the cache service.
        
        Args:
            config: Configuration dictionary
        """
        self.max_size = config.get("max_size", self.max_size)
        self.default_ttl = config.get("default_ttl", self.default_ttl)
        
        # Configure cacheable node types
        cacheable_types = config.get("cacheable_node_types", [])
        if cacheable_types:
            self.cacheable_node_types = set(cacheable_types)
        
        logger.info(f"Node cache configured: max_size={self.max_size}, default_ttl={self.default_ttl}")
    
    def is_node_cacheable(self, node_type: str) -> bool:
        """Check if a node type is cacheable.
        
        Args:
            node_type: The node type to check
            
        Returns:
            True if the node type is cacheable, False otherwise
        """
        # If no specific types are configured, all nodes are cacheable
        if not self.cacheable_node_types:
            return True
        
        return node_type in self.cacheable_node_types
    
    def generate_cache_key(self, node_type: str, node_id: str, inputs: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate a cache key for a node execution.
        
        Args:
            node_type: The type of the node
            node_id: The ID of the node
            inputs: The input values
            config: The node configuration
            
        Returns:
            A cache key string
        """
        # Create a dictionary with all the components
        key_dict = {
            "node_type": node_type,
            "node_id": node_id,
            "inputs": inputs,
            "config": config
        }
        
        # Convert to JSON and hash
        key_json = json.dumps(key_dict, sort_keys=True)
        return hashlib.md5(key_json.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value, or None if not found or expired
        """
        # Check if the key exists
        if key not in self.cache:
            self.misses += 1
            return None
        
        # Get the entry
        entry = self.cache[key]
        
        # Check if the entry is expired
        if entry.is_expired():
            self.evict(key)
            self.misses += 1
            return None
        
        # Update access time and count
        entry.access()
        
        # Move the entry to the end of the OrderedDict
        self.cache.move_to_end(key)
        
        # Increment hit counter
        self.hits += 1
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Time to live in seconds (None for default)
        """
        # Use default TTL if not specified
        if ttl is None:
            ttl = self.default_ttl
        
        # Check if we need to evict entries
        if len(self.cache) >= self.max_size and key not in self.cache:
            self.evict_lru()
        
        # Create a new entry
        entry = CacheEntry(key, value, ttl)
        
        # Add to cache
        self.cache[key] = entry
        
        # Move to the end of the OrderedDict
        self.cache.move_to_end(key)
    
    def evict(self, key: str) -> None:
        """Evict a specific key from the cache.
        
        Args:
            key: The cache key to evict
        """
        if key in self.cache:
            del self.cache[key]
            self.evictions += 1
    
    def evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if self.cache:
            # Get the first key (least recently used)
            key, _ = next(iter(self.cache.items()))
            self.evict(key)
    
    def clear(self) -> None:
        """Clear the entire cache."""
        self.cache.clear()
        logger.info("Node cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests) * 100 if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "evictions": self.evictions
        }
    
    def cleanup_expired(self) -> int:
        """Clean up expired entries.
        
        Returns:
            Number of entries removed
        """
        expired_keys = []
        
        # Find expired entries
        for key, entry in self.cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        # Remove expired entries
        for key in expired_keys:
            self.evict(key)
        
        return len(expired_keys)
