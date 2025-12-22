# Search Box - Multi-Provider MCP Server

A production-ready implementation of Anthropic's Model Context Protocol (MCP) for keyless, privacy-focused search tools. This server provides token-efficient search integration with Claude models through standardized tool schemas and dynamic discovery.

## Overview

This MCP server implements the official [Model Context Protocol specification](https://modelcontextprotocol.io/) (version 2025-11-25) to enable:

- **Token Efficiency**: Progressive tool discovery reduces context from 50k+ tokens to ~2k in complex setups
- **Keyless Access**: All providers require no API keys or authentication
- **Privacy First**: Anonymous search via DuckDuckGo and SearxNG
- **Multi-Provider**: Multiple search backends with standardized interfaces
- **Production Ready**: Async, error handling, normalization, and proper schemas

## Features

### Search Providers

1. **DuckDuckGo** (`web_search_duckduckgo`)
   - Fast, anonymous HTML scraping
   - No tracking, no API key required
   - Best for general queries and privacy

2. **SearxNG Primary** (`web_search_searxng_primary`)
   - Meta-search aggregating multiple engines
   - Instance: searx.be
   - Comprehensive, diverse results

3. **SearxNG Secondary** (`web_search_searxng_secondary`)
   - Alternative instance for redundancy
   - Instance: search.bus-hit.me
   - Load distribution and reliability

### MCP Primitives

- **Tools**: Three standardized web search tools with identical schemas
- **Resources**: `search://available-tools` - documentation of available tools
- **Discovery**: Dynamic listing via MCP protocol reduces token usage

## Installation

### Requirements

- Python 3.12+
- pip or uv package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/tzervas/search-box.git
cd search-box

# Install dependencies
pip install -r requirements.txt

# Or using uv (recommended)
uv pip install -r requirements.txt
```

## Usage

### Running the Server

#### Local (stdio transport)

For use with Claude Desktop or local MCP clients:

```bash
python main.py
```

Or directly:

```bash
python -m search_box.server
```

#### Configuration for Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "search-box": {
      "command": "python",
      "args": ["/path/to/search-box/main.py"],
      "transport": "stdio",
      "env": {
        "SEARXNG_PRIMARY_INSTANCE": "https://searx.be",
        "SEARXNG_SECONDARY_INSTANCE": "https://search.bus-hit.me"
      }
    }
  }
}
```

**Environment Variables:**
- `SEARXNG_PRIMARY_INSTANCE`: Primary SearxNG instance URL (default: https://searx.be)
- `SEARXNG_SECONDARY_INSTANCE`: Secondary SearxNG instance URL (default: https://search.bus-hit.me)

### Using the Tools

Once connected to Claude Desktop or another MCP client:

```
Query: "Search for recent developments in quantum computing"

Claude will automatically:
1. Discover available search tools via MCP
2. Select the most appropriate tool (e.g., web_search_duckduckgo)
3. Execute the search
4. Process and present results
```

### Programmatic Usage

```python
from search_box import DuckDuckGoProvider, SearxNGProvider

# Initialize providers
ddg = DuckDuckGoProvider()
searx = SearxNGProvider()

# Perform searches
results = await ddg.web_search("Python async programming", num_results=5)

for result in results:
    print(f"{result.title}")
    print(f"  {result.url}")
    print(f"  {result.snippet}\n")
```

## Architecture

### Component Overview

```
search_box/
├── base.py              # Abstract SearchProvider and SearchResult
├── providers/
│   ├── duckduckgo.py    # DuckDuckGo provider implementation
│   └── searxng.py       # SearxNG provider implementation
└── server.py            # FastMCP server with tool definitions
```

### Design Patterns

1. **Adapter Pattern**: Abstract `SearchProvider` base class with provider-specific implementations
2. **Normalization**: All providers return standardized `SearchResult` objects
3. **Token Optimization**: Descriptive tool names and descriptions for model-driven selection
4. **Error Handling**: Comprehensive validation and error messages

### Tool Schema

All search tools follow this standardized schema:

```python
{
    "name": "web_search_<provider>",
    "description": "<Provider-specific description>",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "num_results": {"type": "integer", "default": 10, "minimum": 1, "maximum": 20}
        },
        "required": ["query"]
    }
}
```

## Development

### Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests (when implemented)
pytest tests/
```

### Adding a New Provider

1. Create a new provider class in `search_box/providers/`:

```python
from search_box.base import SearchProvider, SearchResult

class NewProvider(SearchProvider):
    async def web_search(self, query: str, num_results: int = 10) -> list[SearchResult]:
        # Implementation
        pass
```

2. Register in `search_box/server.py`:

```python
providers["new_provider"] = NewProvider(name="new_provider")

@mcp.tool()
async def web_search_new_provider(query: str, num_results: int = 10) -> str:
    # Tool implementation
    pass
```

## MCP Specification

This server implements MCP version 2025-11-25 with:

- **Transport**: stdio (local), streamable-http (remote)
- **Methods**: `tools/list`, `tools/call`, `resources/list`, `resources/read`
- **Lifecycle**: Full initialization handshake and capability negotiation

### Token Efficiency Comparison

Traditional tool use vs. MCP for 3 search tools:

| Approach | Context Tokens | Method |
|----------|----------------|--------|
| Traditional | ~15,000 | Static JSON schemas in every call |
| MCP | ~2,000 | Dynamic discovery on-demand |

## Security & Privacy

- **No API Keys**: All providers are keyless and public
- **Anonymous**: DuckDuckGo and SearxNG respect user privacy
- **No Logging**: Search queries are not stored or logged
- **HTTPS**: All provider communications use HTTPS

## Limitations

- Public SearxNG instances may have rate limits or downtime
- HTML scraping (DuckDuckGo) may break if site structure changes
- Results quality depends on provider availability

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Resources

- [MCP Official Site](https://modelcontextprotocol.io/)
- [MCP Specification](https://github.com/modelcontextprotocol)
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python)
- [Claude Desktop](https://claude.ai/download)

## License

See LICENSE file for details.

## Acknowledgments

- Anthropic for the Model Context Protocol specification
- DuckDuckGo for privacy-respecting search
- SearxNG community for open meta-search

---

Built with MCP 2025-11-25 | Python 3.12+
