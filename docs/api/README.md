# Search Box API Documentation

## Base Classes

### SearchProvider

Abstract base class for all search providers.

```python
from search_box.base import SearchProvider, SearchResult

class CustomProvider(SearchProvider):
    async def web_search(self, query: str, num_results: int = 10) -> list[SearchResult]:
        # Implementation
        pass
```

#### Methods

##### `__init__(name: str)`
Initialize the provider with a unique name.

##### `web_search(query: str, num_results: int = 10) -> list[SearchResult]` (abstract)
Perform a web search and return normalized results.

**Parameters:**
- `query` (str): Search query string
- `num_results` (int): Maximum number of results (1-20, default: 10)

**Returns:**
- List of `SearchResult` objects

**Raises:**
- `ValueError`: If parameters are invalid
- `RuntimeError`: If search fails

##### `get_provider_info() -> dict`
Get provider metadata.

**Returns:**
- Dictionary with provider information (name, type, features, etc.)

### SearchResult

Dataclass representing a standardized search result.

```python
@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source_provider: Optional[str] = None
```

**Fields:**
- `title`: Result title
- `url`: Result URL
- `snippet`: Result description/snippet
- `source_provider`: Name of the provider that generated this result (optional)

## Providers

### DuckDuckGoProvider

Provider for DuckDuckGo search using anonymous HTML scraping.

```python
from search_box.providers import DuckDuckGoProvider

provider = DuckDuckGoProvider(name="duckduckgo")
results = await provider.web_search("Python programming", num_results=5)
```

**Features:**
- No API key required
- Anonymous/privacy-respecting
- Fast general-purpose search
- HTML scraping based

**Limitations:**
- May break if DuckDuckGo changes HTML structure
- Limited to text search
- No advanced search operators

### SearxNGProvider

Provider for SearxNG meta-search using public instances.

```python
from search_box.providers import SearxNGProvider

provider = SearxNGProvider(
    name="searxng",
    instance_url="https://searx.be"
)
results = await provider.web_search("Python programming", num_results=5)
```

**Constructor Parameters:**
- `name` (str): Provider name for identification
- `instance_url` (Optional[str]): Custom SearxNG instance URL (defaults to public instances)

**Features:**
- No API key required
- Aggregates results from multiple search engines
- Privacy-focused
- JSON API based
- Supports categories (general, images, news, etc.)

**Limitations:**
- Public instances may have rate limits
- Instance availability varies
- Response time depends on aggregated engines

## MCP Server

### Running the Server

```python
from search_box.server import main

main()  # Runs with stdio transport
```

### Available Tools

#### web_search_duckduckgo(query: str, num_results: int = 10) -> str

Fast general web search via DuckDuckGo.

#### web_search_searxng_primary(query: str, num_results: int = 10) -> str

Meta-search via SearxNG primary instance (searx.be).

#### web_search_searxng_secondary(query: str, num_results: int = 10) -> str

Meta-search via SearxNG secondary instance (search.bus-hit.me).

### Available Resources

#### search://available-tools

Returns markdown documentation of available search tools and their features.

## Usage Examples

### Programmatic Usage

```python
import asyncio
from search_box import DuckDuckGoProvider, SearxNGProvider

async def search_example():
    # Initialize providers
    ddg = DuckDuckGoProvider()
    searx = SearxNGProvider()
    
    # Perform searches
    ddg_results = await ddg.web_search("Python async", num_results=5)
    searx_results = await searx.web_search("Python async", num_results=5)
    
    # Process results
    print("DuckDuckGo Results:")
    for result in ddg_results:
        print(f"- {result.title}")
        print(f"  {result.url}")
        print(f"  {result.snippet}\n")
    
    print("\nSearxNG Results:")
    for result in searx_results:
        print(f"- {result.title}")
        print(f"  {result.url}")
        print(f"  {result.snippet}\n")

asyncio.run(search_example())
```

## Token Efficiency

When using the MCP server with Claude:

- **Dynamic Discovery**: Tools are only loaded when needed
- **Standardized Schemas**: Reduce redundancy in tool definitions
- **Parallel Execution**: MCP supports parallel tool calls natively
- **Caching**: MCP clients can cache tool definitions

**Token Usage Comparison:**

| Method | Tokens | Description |
|--------|--------|-------------|
| Traditional (3 tools) | ~15,000 | Static schemas in every API call |
| MCP (3 tools) | ~2,000 | Dynamic discovery on-demand |

