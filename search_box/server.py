"""
Multi-Provider MCP Server for Keyless Search Tools.

This server implements Anthropic's Model Context Protocol (MCP) to provide
token-efficient, standardized search tool integration with Claude models.

Features:
- Multiple keyless search providers (DuckDuckGo, SearxNG)
- Standardized tool schemas for optimal model discovery
- Dynamic tool listing and execution via MCP
- Token/context optimization through progressive discovery
"""

from mcp.server.fastmcp import FastMCP
from search_box.providers import DuckDuckGoProvider, SearxNGProvider
from search_box.base import SearchResult

# Initialize FastMCP server
mcp = FastMCP("search-box-mcp")

# Initialize providers
providers = {
    "duckduckgo": DuckDuckGoProvider(name="duckduckgo"),
    "searxng_primary": SearxNGProvider(name="searxng_primary", instance_url="https://searx.be"),
    "searxng_secondary": SearxNGProvider(name="searxng_secondary", instance_url="https://search.bus-hit.me"),
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
    
    Args:
        query: Search query string (required)
        num_results: Maximum number of results to return, between 1 and 20 (default: 10)
        
    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    provider = providers["duckduckgo"]
    results = await provider.web_search(query, num_results)
    return _format_search_results(results)


@mcp.tool()
async def web_search_searxng_primary(query: str, num_results: int = 10) -> str:
    """
    Privacy-focused meta-search via SearxNG (aggregates multiple engines, no API key required).
    
    This tool uses SearxNG to aggregate results from multiple search engines while
    maintaining privacy. Provides diverse results from various sources.
    Primary instance: searx.be
    
    Args:
        query: Search query string (required)
        num_results: Maximum number of results to return, between 1 and 20 (default: 10)
        
    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    provider = providers["searxng_primary"]
    results = await provider.web_search(query, num_results)
    return _format_search_results(results)


@mcp.tool()
async def web_search_searxng_secondary(query: str, num_results: int = 10) -> str:
    """
    Privacy-focused meta-search via SearxNG (alternative instance for reliability).
    
    This tool uses an alternative SearxNG instance for redundancy and load distribution.
    Use when the primary instance is unavailable or for diverse results.
    Secondary instance: search.bus-hit.me
    
    Args:
        query: Search query string (required)
        num_results: Maximum number of results to return, between 1 and 20 (default: 10)
        
    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    provider = providers["searxng_secondary"]
    results = await provider.web_search(query, num_results)
    return _format_search_results(results)


@mcp.resource("search://available-tools")
def get_available_tools() -> str:
    """
    Resource providing information about available search tools and providers.
    
    Returns:
        Markdown documentation of available search tools
    """
    return """# Available Search Tools

This MCP server provides multiple keyless search tools optimized for token efficiency and privacy.

## Web Search Tools

### 1. web_search_duckduckgo
- **Provider**: DuckDuckGo
- **Type**: Anonymous HTML scraping
- **Features**: Fast, no tracking, no API key required
- **Best for**: General queries, privacy-focused searches
- **Latency**: Low

### 2. web_search_searxng_primary
- **Provider**: SearxNG (searx.be)
- **Type**: Meta-search engine
- **Features**: Aggregates multiple engines, privacy-focused, no API key
- **Best for**: Comprehensive results, diverse sources
- **Latency**: Medium

### 3. web_search_searxng_secondary
- **Provider**: SearxNG (search.bus-hit.me)
- **Type**: Meta-search engine (alternative instance)
- **Features**: Backup instance, load distribution
- **Best for**: Redundancy, when primary is unavailable
- **Latency**: Medium

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
"""


def main():
    """Run the MCP server."""
    # Run with stdio transport for local connections
    # Use streamable-http transport for remote connections
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
