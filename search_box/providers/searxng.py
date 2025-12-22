"""SearxNG search provider implementation (keyless, public instances)."""

import httpx
from typing import Optional

from ..base import SearchProvider, SearchResult


class SearxNGProvider(SearchProvider):
    """
    SearxNG search provider using public instances with JSON API.
    No API key required, privacy-focused meta-search.
    """
    
    # Public SearxNG instances (can be configured)
    DEFAULT_INSTANCES = [
        "https://searx.be",
        "https://search.bus-hit.me",
        "https://searx.tiekoetter.com",
    ]
    
    def __init__(
        self, 
        name: str = "searxng",
        instance_url: Optional[str] = None
    ):
        """
        Initialize SearxNG provider.
        
        Args:
            name: Provider name for identification
            instance_url: Custom SearxNG instance URL (optional)
        """
        super().__init__(name)
        self.instance_url = instance_url or self.DEFAULT_INSTANCES[0]
        self.search_endpoint = f"{self.instance_url}/search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def web_search(
        self, 
        query: str, 
        num_results: int = 10,
        category: Optional[str] = None
    ) -> list[SearchResult]:
        """
        Perform web search via SearxNG JSON API.
        
        Args:
            query: Search query string
            num_results: Maximum number of results (1-20)
            category: Optional category filter (e.g., 'general', 'images', 'news')
            
        Returns:
            List of SearchResult objects
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If search fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if num_results < 1 or num_results > 20:
            raise ValueError("num_results must be between 1 and 20")
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                params = {
                    "q": query,
                    "format": "json",
                    "pageno": 1,
                }
                
                if category:
                    params["categories"] = category
                
                response = await client.get(
                    self.search_endpoint,
                    headers=self.headers,
                    params=params,
                )
                response.raise_for_status()
                
                return self._parse_results(response.json(), num_results)
                
        except httpx.HTTPError as e:
            raise RuntimeError(f"SearxNG search failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during SearxNG search: {e}")
    
    def _parse_results(self, data: dict, max_results: int) -> list[SearchResult]:
        """
        Parse SearxNG JSON results.
        
        Args:
            data: JSON response data
            max_results: Maximum number of results to extract
            
        Returns:
            List of SearchResult objects
        """
        results = []
        
        # SearxNG returns results in 'results' key
        raw_results = data.get("results", [])
        
        for item in raw_results[:max_results]:
            title = item.get("title", "")
            url = item.get("url", "")
            snippet = item.get("content", "")
            
            # Skip invalid results
            if not title or not url:
                continue
            
            results.append(SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                source_provider=self.name
            ))
        
        return results
    
    def get_provider_info(self) -> dict:
        """Get provider metadata."""
        info = super().get_provider_info()
        info.update({
            "description": "Privacy-focused meta-search via SearxNG (aggregates multiple engines, no API key)",
            "keyless": True,
            "features": ["web_search"],
            "instance": self.instance_url,
        })
        return info
