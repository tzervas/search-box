"""Tests for caching functionality."""

import time
import pytest
from search_box.cache import SearchCache, CacheEntry
from search_box.base import SearchResult


def test_cache_initialization():
    """Test cache initialization with default values."""
    cache = SearchCache()
    assert cache.max_size == 100
    assert cache.ttl_seconds == 3600
    assert len(cache) == 0


def test_cache_initialization_custom():
    """Test cache initialization with custom values."""
    cache = SearchCache(max_size=50, ttl_seconds=1800)
    assert cache.max_size == 50
    assert cache.ttl_seconds == 1800


def test_cache_initialization_invalid():
    """Test cache initialization with invalid values."""
    with pytest.raises(ValueError):
        SearchCache(max_size=0)
    
    with pytest.raises(ValueError):
        SearchCache(max_size=-1)
    
    with pytest.raises(ValueError):
        SearchCache(ttl_seconds=0)
    
    with pytest.raises(ValueError):
        SearchCache(ttl_seconds=-1)


def test_cache_set_and_get():
    """Test basic cache set and get operations."""
    cache = SearchCache()
    
    results = [
        SearchResult(
            title="Test Result",
            url="https://example.com",
            snippet="Test snippet",
            source_provider="test"
        )
    ]
    
    cache.set("test_provider", "test query", 10, results)
    retrieved = cache.get("test_provider", "test query", 10)
    
    assert retrieved is not None
    assert len(retrieved) == 1
    assert retrieved[0].title == "Test Result"


def test_cache_miss():
    """Test cache miss returns None."""
    cache = SearchCache()
    
    result = cache.get("test_provider", "nonexistent query", 10)
    assert result is None


def test_cache_query_normalization():
    """Test that queries are normalized (case-insensitive, whitespace)."""
    cache = SearchCache()
    
    results = [
        SearchResult(
            title="Test Result",
            url="https://example.com",
            snippet="Test snippet"
        )
    ]
    
    # Set with one format
    cache.set("test_provider", "Test Query", 10, results)
    
    # Get with different case/whitespace
    retrieved1 = cache.get("test_provider", "test query", 10)
    retrieved2 = cache.get("test_provider", " TEST QUERY ", 10)
    
    assert retrieved1 is not None
    assert retrieved2 is not None
    assert retrieved1[0].title == "Test Result"
    assert retrieved2[0].title == "Test Result"


def test_cache_different_num_results():
    """Test that different num_results create different cache keys."""
    cache = SearchCache()
    
    results_10 = [SearchResult(title="10 results", url="http://a.com", snippet="a")]
    results_5 = [SearchResult(title="5 results", url="http://b.com", snippet="b")]
    
    cache.set("test_provider", "test query", 10, results_10)
    cache.set("test_provider", "test query", 5, results_5)
    
    retrieved_10 = cache.get("test_provider", "test query", 10)
    retrieved_5 = cache.get("test_provider", "test query", 5)
    
    assert retrieved_10[0].title == "10 results"
    assert retrieved_5[0].title == "5 results"


def test_cache_different_providers():
    """Test that different providers create different cache keys."""
    cache = SearchCache()
    
    results_a = [SearchResult(title="Provider A", url="http://a.com", snippet="a")]
    results_b = [SearchResult(title="Provider B", url="http://b.com", snippet="b")]
    
    cache.set("provider_a", "test query", 10, results_a)
    cache.set("provider_b", "test query", 10, results_b)
    
    retrieved_a = cache.get("provider_a", "test query", 10)
    retrieved_b = cache.get("provider_b", "test query", 10)
    
    assert retrieved_a[0].title == "Provider A"
    assert retrieved_b[0].title == "Provider B"


def test_cache_lru_eviction():
    """Test LRU eviction when cache is full."""
    cache = SearchCache(max_size=3)
    
    # Fill cache
    cache.set("provider", "query1", 10, ["result1"])
    cache.set("provider", "query2", 10, ["result2"])
    cache.set("provider", "query3", 10, ["result3"])
    
    assert len(cache) == 3
    
    # Add one more - should evict oldest (query1)
    cache.set("provider", "query4", 10, ["result4"])
    
    assert len(cache) == 3
    assert cache.get("provider", "query1", 10) is None  # Evicted
    assert cache.get("provider", "query2", 10) is not None
    assert cache.get("provider", "query3", 10) is not None
    assert cache.get("provider", "query4", 10) is not None


def test_cache_lru_access_order():
    """Test that accessing an entry makes it most recently used."""
    cache = SearchCache(max_size=3)
    
    # Fill cache
    cache.set("provider", "query1", 10, ["result1"])
    cache.set("provider", "query2", 10, ["result2"])
    cache.set("provider", "query3", 10, ["result3"])
    
    # Access query1 to make it most recently used
    cache.get("provider", "query1", 10)
    
    # Add query4 - should evict query2 (oldest unused)
    cache.set("provider", "query4", 10, ["result4"])
    
    assert cache.get("provider", "query1", 10) is not None  # Still there
    assert cache.get("provider", "query2", 10) is None      # Evicted
    assert cache.get("provider", "query3", 10) is not None
    assert cache.get("provider", "query4", 10) is not None


def test_cache_ttl_expiration():
    """Test that entries expire after TTL."""
    cache = SearchCache(ttl_seconds=1)  # 1 second TTL
    
    results = [SearchResult(title="Test", url="http://test.com", snippet="test")]
    cache.set("provider", "query", 10, results)
    
    # Should be available immediately
    assert cache.get("provider", "query", 10) is not None
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Should be expired now
    assert cache.get("provider", "query", 10) is None


def test_cache_clear():
    """Test clearing the cache."""
    cache = SearchCache()
    
    cache.set("provider", "query1", 10, ["result1"])
    cache.set("provider", "query2", 10, ["result2"])
    
    assert len(cache) == 2
    
    cache.clear()
    
    assert len(cache) == 0
    assert cache.get("provider", "query1", 10) is None
    assert cache.get("provider", "query2", 10) is None


def test_cache_statistics():
    """Test cache statistics tracking."""
    cache = SearchCache(max_size=2)
    
    # Initial stats
    stats = cache.get_stats()
    assert stats["size"] == 0
    assert stats["hits"] == 0
    assert stats["misses"] == 0
    assert stats["evictions"] == 0
    assert stats["hit_rate"] == 0.0
    
    # Add entries and test
    cache.set("provider", "query1", 10, ["result1"])
    cache.set("provider", "query2", 10, ["result2"])
    
    # Hit
    cache.get("provider", "query1", 10)
    
    # Miss
    cache.get("provider", "query3", 10)
    
    # Eviction
    cache.set("provider", "query4", 10, ["result4"])
    
    stats = cache.get_stats()
    assert stats["size"] == 2
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["evictions"] == 1
    assert stats["hit_rate"] == 50.0


def test_cache_update_existing_key():
    """Test updating an existing cache key."""
    cache = SearchCache()
    
    # Set initial value
    cache.set("provider", "query", 10, ["result1"])
    
    # Update with new value
    cache.set("provider", "query", 10, ["result2"])
    
    # Should have the new value
    result = cache.get("provider", "query", 10)
    assert result == ["result2"]
    
    # Cache size should still be 1 (not duplicated)
    assert len(cache) == 1


@pytest.mark.asyncio
async def test_cache_with_search_provider():
    """Test cache integration with SearchProvider."""
    from search_box.base import SearchProvider, SearchResult
    
    class MockProvider(SearchProvider):
        def __init__(self, name: str = "mock", cache=None):
            super().__init__(name, cache)
            self.call_count = 0
        
        async def web_search(self, query: str, num_results: int = 10):
            self.call_count += 1
            return [
                SearchResult(
                    title=f"Result {self.call_count}",
                    url="http://test.com",
                    snippet="test",
                    source_provider=self.name
                )
            ]
    
    # Test without cache
    provider = MockProvider()
    result1 = await provider.cached_search("test", 10)
    result2 = await provider.cached_search("test", 10)
    
    assert provider.call_count == 2  # Called twice
    assert result1[0].title == "Result 1"
    assert result2[0].title == "Result 2"
    
    # Test with cache
    cache = SearchCache()
    provider_cached = MockProvider(cache=cache)
    
    result1 = await provider_cached.cached_search("test", 10)
    result2 = await provider_cached.cached_search("test", 10)
    
    assert provider_cached.call_count == 1  # Called only once
    assert result1[0].title == "Result 1"
    assert result2[0].title == "Result 1"  # Same result from cache


@pytest.mark.asyncio
async def test_cached_search_without_cache():
    """Test that cached_search works without cache (direct search)."""
    from search_box.base import SearchProvider, SearchResult
    
    class MockProvider(SearchProvider):
        async def web_search(self, query: str, num_results: int = 10):
            return [
                SearchResult(
                    title="Direct Result",
                    url="http://test.com",
                    snippet="test"
                )
            ]
    
    provider = MockProvider("mock")
    result = await provider.cached_search("test", 10)
    
    assert result[0].title == "Direct Result"
