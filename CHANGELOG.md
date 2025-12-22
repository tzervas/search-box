# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-22

### Added
- Initial implementation of Multi-Provider MCP Server
- Base adapter architecture with `SearchProvider` abstract class
- `SearchResult` dataclass for standardized results
- DuckDuckGo provider with anonymous HTML scraping
- SearxNG provider with public instance support
- FastMCP server implementation with stdio transport
- Three standardized search tools:
  - `web_search_duckduckgo`
  - `web_search_searxng_primary`
  - `web_search_searxng_secondary`
- MCP resource: `search://available-tools`
- Comprehensive test suite with mocked HTTP responses
- Complete documentation:
  - Main README with usage examples
  - API documentation
  - Development guide
  - Security documentation
- Project configuration for Python 3.12+
- Dependencies: mcp, httpx, beautifulsoup4, lxml
- pytest-based testing infrastructure

### Features
- Token-efficient search via MCP progressive discovery
- Keyless providers (no API keys required)
- Privacy-focused search (DuckDuckGo, SearxNG)
- Async/await support for all operations
- Comprehensive error handling and validation
- Result normalization across providers
- Full MCP 2025-11-25 specification compliance

### Documentation
- Installation and setup instructions
- Usage examples (CLI and programmatic)
- Architecture overview
- Contributing guidelines
- Security considerations
- API reference

### Testing
- Unit tests for base classes
- Provider tests with mocked HTTP
- Validation tests for input parameters
- Error handling tests
- 15 tests, 100% passing

[0.1.0]: https://github.com/tzervas/search-box/releases/tag/v0.1.0
