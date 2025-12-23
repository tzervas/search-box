"""Search Box - Multi-Provider MCP Server for Keyless Search Tools."""

from .base import SearchProvider, SearchResult
from .cache import SearchCache
from .providers import DuckDuckGoProvider, SearxNGProvider

__version__ = "0.2.0"
__all__ = [
    "SearchProvider",
    "SearchResult",
    "SearchCache",
    "DuckDuckGoProvider",
    "SearxNGProvider",
]
