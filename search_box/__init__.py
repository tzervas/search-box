"""Search Box - Multi-Provider MCP Server for Keyless Search Tools."""

from .base import SearchProvider, SearchResult
from .providers import DuckDuckGoProvider, SearxNGProvider

__version__ = "0.1.0"
__all__ = [
    "SearchProvider",
    "SearchResult",
    "DuckDuckGoProvider",
    "SearxNGProvider",
]
