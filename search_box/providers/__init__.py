"""Search provider implementations."""

from .duckduckgo import DuckDuckGoProvider
from .searxng import SearxNGProvider

__all__ = ["DuckDuckGoProvider", "SearxNGProvider"]
