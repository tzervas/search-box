"""Caching layer for search results with TTL and LRU eviction."""

import hashlib
import time
from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock
from typing import Optional, Any


@dataclass
class CacheEntry:
    """Cache entry with value and expiration time."""
    
    value: Any
    expires_at: float


class SearchCache:
    """
    Thread-safe LRU cache with TTL for search results.
    
    Features:
    - LRU (Least Recently Used) eviction policy
    - TTL (Time To Live) for entries
    - Thread-safe operations
    - Cache statistics
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of entries in cache
            ttl_seconds: Time to live for entries in seconds (default: 1 hour)
        """
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be at least 1")
        
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def _make_key(self, provider: str, query: str, num_results: int) -> str:
        """
        Generate cache key from search parameters.
        
        Args:
            provider: Provider name
            query: Search query
            num_results: Number of results
            
        Returns:
            Cache key string
        """
        # Normalize query (lowercase, strip whitespace)
        normalized_query = query.lower().strip()
        
        # Create a composite key
        key_parts = f"{provider}:{normalized_query}:{num_results}"
        
        # Hash to create fixed-length key
        return hashlib.sha256(key_parts.encode()).hexdigest()
    
    def get(
        self, 
        provider: str, 
        query: str, 
        num_results: int
    ) -> Optional[Any]:
        """
        Retrieve value from cache if it exists and hasn't expired.
        
        Args:
            provider: Provider name
            query: Search query
            num_results: Number of results
            
        Returns:
            Cached value or None if not found/expired
        """
        key = self._make_key(provider, query, num_results)
        current_time = time.time()
        
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if current_time >= entry.expires_at:
                # Remove expired entry
                del self._cache[key]
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            
            return entry.value
    
    def set(
        self, 
        provider: str, 
        query: str, 
        num_results: int, 
        value: Any
    ) -> None:
        """
        Store value in cache.
        
        Args:
            provider: Provider name
            query: Search query
            num_results: Number of results
            value: Value to cache
        """
        key = self._make_key(provider, query, num_results)
        expires_at = time.time() + self.ttl_seconds
        
        with self._lock:
            # If key exists, update it
            if key in self._cache:
                del self._cache[key]
            
            # Add new entry
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
            
            # Evict oldest if over max size
            if len(self._cache) > self.max_size:
                # Remove oldest (first item)
                self._cache.popitem(last=False)
                self._evictions += 1
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0.0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": round(hit_rate, 2),
                "ttl_seconds": self.ttl_seconds,
            }
    
    def __len__(self) -> int:
        """Return current cache size."""
        with self._lock:
            return len(self._cache)
