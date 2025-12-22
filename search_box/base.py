"""Base adapter interface for search providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from .cache import SearchCache


@dataclass
class SearchResult:
    """Standardized search result format."""
    
    title: str
    url: str
    snippet: str
    source_provider: Optional[str] = None


class SearchProvider(ABC):
    """Abstract base class for all search providers."""
    
    def __init__(self, name: str, cache: Optional[SearchCache] = None):
        """
        Initialize the search provider.
        
        Args:
            name: Provider name for identification
            cache: Optional SearchCache instance for result caching
        """
        self.name = name
        self.cache = cache
    
    @abstractmethod
    async def web_search(
        self, 
        query: str, 
        num_results: int = 10
    ) -> list[SearchResult]:
        """
        Perform a web search and return normalized results.
        
        Args:
            query: Search query string
            num_results: Maximum number of results to return (1-20)
            
        Returns:
            List of SearchResult objects
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If search fails
        """
        pass
    
    async def cached_search(
        self,
        query: str,
        num_results: int = 10
    ) -> list[SearchResult]:
        """
        Perform a web search with caching support.
        
        If cache is enabled and result exists in cache, return cached result.
        Otherwise, perform search and cache the result.
        
        Args:
            query: Search query string
            num_results: Maximum number of results to return (1-20)
            
        Returns:
            List of SearchResult objects
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If search fails
        """
        # If cache is not enabled, perform direct search
        if self.cache is None:
            return await self.web_search(query, num_results)
        
        # Try to get from cache
        cached_result = self.cache.get(self.name, query, num_results)
        if cached_result is not None:
            return cached_result
        
        # Cache miss - perform search
        results = await self.web_search(query, num_results)
        
        # Store in cache
        self.cache.set(self.name, query, num_results, results)
        
        return results
    
    def get_provider_info(self) -> dict:
        """
        Get provider metadata.
        
        Returns:
            Dictionary with provider information
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
        }
