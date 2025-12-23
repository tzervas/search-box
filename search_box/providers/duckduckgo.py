"""DuckDuckGo search provider implementation (keyless, anonymous)."""

import re
import urllib.parse
from typing import Optional
import httpx
from bs4 import BeautifulSoup

from ..base import SearchProvider, SearchResult


class DuckDuckGoProvider(SearchProvider):
    """
    DuckDuckGo search provider using anonymous HTML scraping.
    No API key required, respects privacy.
    """
    
    def __init__(self, name: str = "duckduckgo", cache=None):
        """Initialize DuckDuckGo provider."""
        super().__init__(name, cache)
        self.base_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def web_search(
        self, 
        query: str, 
        num_results: int = 10
    ) -> list[SearchResult]:
        """
        Perform web search via DuckDuckGo HTML interface.
        
        Args:
            query: Search query string
            num_results: Maximum number of results (1-20)
            
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
                # DuckDuckGo HTML uses POST with form data
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    data={"q": query, "b": "", "kl": "us-en"},
                )
                response.raise_for_status()
                
                return self._parse_results(response.text, num_results)
                
        except httpx.HTTPError as e:
            raise RuntimeError(f"DuckDuckGo search failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during DuckDuckGo search: {e}")
    
    def _parse_results(self, html: str, max_results: int) -> list[SearchResult]:
        """
        Parse DuckDuckGo HTML results.
        
        Args:
            html: Raw HTML response
            max_results: Maximum number of results to extract
            
        Returns:
            List of SearchResult objects
        """
        soup = BeautifulSoup(html, "lxml")
        results = []
        
        # DuckDuckGo HTML results are in divs with class 'result'
        result_divs = soup.find_all("div", class_="result", limit=max_results)
        
        for div in result_divs:
            if len(results) >= max_results:
                break
            
            # Extract title and URL from the link
            title_link = div.find("a", class_="result__a")
            if not title_link:
                continue
            
            title = title_link.get_text(strip=True)
            url = title_link.get("href", "")
            
            # Extract snippet from result__snippet
            snippet_div = div.find("a", class_="result__snippet")
            snippet = ""
            if snippet_div:
                snippet = snippet_div.get_text(strip=True)
            
            # Clean up URL (DuckDuckGo sometimes uses redirect URLs)
            url = self._clean_url(url)
            
            if title and url:
                results.append(SearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    source_provider=self.name
                ))
        
        return results
    
    def _clean_url(self, url: str) -> str:
        """
        Clean and normalize URL.
        
        Args:
            url: Raw URL from HTML
            
        Returns:
            Cleaned URL
        """
        # Remove DuckDuckGo redirect wrapper if present
        if "//duckduckgo.com/l/?" in url:
            # Extract the actual URL from redirect
            match = re.search(r"uddg=([^&]+)", url)
            if match:
                return urllib.parse.unquote(match.group(1))
        
        return url
    
    def get_provider_info(self) -> dict:
        """Get provider metadata."""
        info = super().get_provider_info()
        info.update({
            "description": "Fast general web search via DuckDuckGo (no tracking, no API key)",
            "keyless": True,
            "features": ["web_search"],
        })
        return info
