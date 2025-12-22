"""Base adapter interface for search providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchResult:
    """Standardized search result format."""
    
    title: str
    url: str
    snippet: str
    source_provider: Optional[str] = None


class SearchProvider(ABC):
    """Abstract base class for all search providers."""
    
    def __init__(self, name: str):
        """
        Initialize the search provider.
        
        Args:
            name: Provider name for identification
        """
        self.name = name
    
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
