"""
Multi-Provider MCP Server for Keyless Search Tools.

This server implements Anthropic's Model Context Protocol (MCP) to provide
token-efficient, standardized search tool integration with Claude models.

Features:
- Multiple keyless search providers (DuckDuckGo, SearxNG)
- Standardized tool schemas for optimal model discovery
- Dynamic tool listing and execution via MCP
- Token/context optimization through progressive discovery
- Result caching with LRU eviction and TTL
"""

import os
from mcp.server.fastmcp import FastMCP
from search_box.providers import DuckDuckGoProvider, SearxNGProvider
from search_box.base import SearchResult
from search_box.cache import SearchCache

# Initialize FastMCP server
mcp = FastMCP("search-box-mcp")

# Get SearxNG instance URLs from environment or use defaults
SEARXNG_PRIMARY = os.getenv("SEARXNG_PRIMARY_INSTANCE", "https://searx.be")
SEARXNG_SECONDARY = os.getenv("SEARXNG_SECONDARY_INSTANCE", "https://search.bus-hit.me")

# Get cache configuration from environment or use defaults
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "100"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

# Initialize shared cache if enabled
shared_cache = SearchCache(max_size=CACHE_MAX_SIZE, ttl_seconds=CACHE_TTL_SECONDS) if CACHE_ENABLED else None

# Initialize providers with cache
providers = {
    "duckduckgo": DuckDuckGoProvider(name="duckduckgo", cache=shared_cache),
    "searxng_primary": SearxNGProvider(name="searxng_primary", instance_url=SEARXNG_PRIMARY, cache=shared_cache),
    "searxng_secondary": SearxNGProvider(name="searxng_secondary", instance_url=SEARXNG_SECONDARY, cache=shared_cache),
}


def _format_search_results(results: list[SearchResult]) -> str:
    """
    Format search results as readable text for model consumption.
    
    Args:
        results: List of SearchResult objects
        
    Returns:
        Formatted string with all results
    """
    if not results:
        return "No results found."
    
    output = []
    for i, result in enumerate(results, 1):
        output.append(f"{i}. {result.title}")
        output.append(f"   URL: {result.url}")
        if result.snippet:
            output.append(f"   {result.snippet}")
        output.append("")  # Empty line for spacing
    
    return "\n".join(output)


@mcp.tool()
async def web_search_duckduckgo(query: str, num_results: int = 10) -> str:
    """
    Fast general web search via DuckDuckGo (no tracking, no API key required).
    
    This tool provides quick, privacy-respecting web search results using DuckDuckGo's
    anonymous HTML interface. Best for general queries and when privacy is important.
    Results are cached to improve performance.
    
    Args:
        query: Search query string (required)
        num_results: Maximum number of results to return, between 1 and 20 (default: 10)
        
    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    provider = providers["duckduckgo"]
    results = await provider.cached_search(query, num_results)
    return _format_search_results(results)


@mcp.tool()
async def web_search_searxng_primary(query: str, num_results: int = 10) -> str:
    """
    Privacy-focused meta-search via SearxNG (aggregates multiple engines, no API key required).
    
    This tool uses SearxNG to aggregate results from multiple search engines while
    maintaining privacy. Provides diverse results from various sources.
    Results are cached to improve performance.
    Primary instance: searx.be
    
    Args:
        query: Search query string (required)
        num_results: Maximum number of results to return, between 1 and 20 (default: 10)
        
    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    provider = providers["searxng_primary"]
    results = await provider.cached_search(query, num_results)
    return _format_search_results(results)


@mcp.tool()
async def web_search_searxng_secondary(query: str, num_results: int = 10) -> str:
    """
    Privacy-focused meta-search via SearxNG (alternative instance for reliability).
    
    This tool uses an alternative SearxNG instance for redundancy and load distribution.
    Use when the primary instance is unavailable or for diverse results.
    Results are cached to improve performance.
    Secondary instance: search.bus-hit.me
    
    Args:
        query: Search query string (required)
        num_results: Maximum number of results to return, between 1 and 20 (default: 10)
        
    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    provider = providers["searxng_secondary"]
    results = await provider.cached_search(query, num_results)
    return _format_search_results(results)


@mcp.tool()
async def get_cache_stats() -> str:
    """
    Get statistics about the search result cache.
    
    Returns cache performance metrics including hit rate, size, and evictions.
    Useful for monitoring cache effectiveness and performance optimization.
    
    Returns:
        Formatted cache statistics
    """
    if shared_cache is None:
        return "Cache is disabled. Enable by setting CACHE_ENABLED=true environment variable."
    
    stats = shared_cache.get_stats()
    
    output = [
        "# Cache Statistics",
        "",
        f"**Status**: Enabled",
        f"**Current Size**: {stats['size']} / {stats['max_size']} entries",
        f"**TTL**: {stats['ttl_seconds']} seconds",
        "",
        "## Performance Metrics",
        f"- Cache Hits: {stats['hits']}",
        f"- Cache Misses: {stats['misses']}",
        f"- Hit Rate: {stats['hit_rate']}%",
        f"- Evictions: {stats['evictions']}",
        "",
        "## Interpretation",
    ]
    
    # Add interpretation based on hit rate
    if stats['hit_rate'] >= 75:
        output.append("✅ Excellent cache performance - Most queries are being served from cache.")
    elif stats['hit_rate'] >= 50:
        output.append("✓ Good cache performance - Cache is providing value.")
    elif stats['hit_rate'] >= 25:
        output.append("⚠ Moderate cache performance - Consider increasing cache size or TTL.")
    else:
        output.append("⚠ Low cache performance - Cache may need tuning or queries are highly diverse.")
    
    return "\n".join(output)


@mcp.resource("search://available-tools")
def get_available_tools() -> str:
    """
    Resource providing information about available search tools and providers.
    
    Returns:
        Markdown documentation of available search tools
    """
    cache_status = "Enabled" if shared_cache else "Disabled"
    cache_info = ""
    if shared_cache:
        cache_info = f"""
## Caching

**Status**: {cache_status}
- **Max Size**: {CACHE_MAX_SIZE} entries
- **TTL**: {CACHE_TTL_SECONDS} seconds ({CACHE_TTL_SECONDS // 60} minutes)
- **Policy**: LRU (Least Recently Used) eviction

Caching improves performance by storing search results temporarily. Use the 
`get_cache_stats` tool to view cache performance metrics.

### Configuration

Set these environment variables to configure caching:
- `CACHE_ENABLED`: Enable/disable cache (default: true)
- `CACHE_MAX_SIZE`: Maximum cache entries (default: 100)
- `CACHE_TTL_SECONDS`: Time to live in seconds (default: 3600)
"""
    
    return f"""# Available Search Tools

This MCP server provides multiple keyless search tools optimized for token efficiency and privacy.
{cache_info}

## Web Search Tools

### 1. web_search_duckduckgo
- **Provider**: DuckDuckGo
- **Type**: Anonymous HTML scraping
- **Features**: Fast, no tracking, no API key required
- **Best for**: General queries, privacy-focused searches
- **Latency**: Low
- **Caching**: {cache_status}

### 2. web_search_searxng_primary
- **Provider**: SearxNG (searx.be)
- **Type**: Meta-search engine
- **Features**: Aggregates multiple engines, privacy-focused, no API key
- **Best for**: Comprehensive results, diverse sources
- **Latency**: Medium
- **Caching**: {cache_status}

### 3. web_search_searxng_secondary
- **Provider**: SearxNG (search.bus-hit.me)
- **Type**: Meta-search engine (alternative instance)
- **Features**: Backup instance, load distribution
- **Best for**: Redundancy, when primary is unavailable
- **Latency**: Medium
- **Caching**: {cache_status}

### 4. get_cache_stats
- **Type**: Diagnostic tool
- **Features**: View cache performance metrics
- **Returns**: Hit rate, size, evictions, and recommendations

## Standard Parameters

All web search tools support these parameters:
- `query` (required): Search query string
- `num_results` (optional): Number of results (1-20, default: 10)

## Output Format

Results are formatted as:
```
1. [Title]
   URL: [URL]
   [Snippet/Description]

2. [Title]
   ...
```

## Token Efficiency

This MCP server leverages Model Context Protocol's dynamic discovery:
- Tools are only loaded when queried (not in every API call)
- Standardized schemas reduce context overhead
- Parallel execution supported natively by MCP
- Result caching reduces redundant API calls
"""


def main():
    """Run the MCP server."""
    # Run with stdio transport for local connections
    # Use streamable-http transport for remote connections
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
