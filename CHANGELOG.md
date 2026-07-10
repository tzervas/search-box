# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-12-22

### Added
- **Caching Layer**: LRU cache with TTL for search results
  - `SearchCache` class with thread-safe operations
  - LRU (Least Recently Used) eviction policy
  - Configurable TTL (Time To Live) for cache entries
  - Query normalization (case-insensitive, whitespace-agnostic)
  - Cache statistics and hit rate monitoring
  - `get_cache_stats` MCP tool for cache diagnostics
- **Environment Configuration** for caching:
  - `CACHE_ENABLED`: Enable/disable caching (default: true)
  - `CACHE_MAX_SIZE`: Maximum cache entries (default: 100)
  - `CACHE_TTL_SECONDS`: Cache TTL in seconds (default: 3600)
- `cached_search` method in `SearchProvider` base class
- 16 comprehensive cache tests (100% passing)

### Changed
- Updated all search tools to use `cached_search` for better performance
- Extended `SearchProvider.__init__` to accept optional `cache` parameter
- Updated provider constructors (`DuckDuckGoProvider`, `SearxNGProvider`) to support cache
- Enhanced MCP resource documentation with cache information
- Updated README with caching configuration examples

### Improved
- Performance: Cached searches can be 100-1000x faster for repeated queries
- Resource utilization: Reduced load on search providers
- Documentation: Added cache configuration and usage examples

### Testing
- Total tests: 31 (15 original + 16 cache tests)
- All tests passing with 100% success rate

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

[0.2.0]: https://github.com/tzervas/search-box/releases/tag/v0.2.0
[0.1.0]: https://github.com/tzervas/search-box/releases/tag/v0.1.0

## Semver baseline notes (appended 2026-07-10)

- Formal semver baseline v0.1.0 established per workspace plan.md (see "Local GHCR + semver" and execution continuation sections) + local GHCR preference (podman local builds/push to avoid Actions credits; applied to python dist+gh release here).
- Cites: plan.md, tero queries (local search-box index via tero.sh: changelog entry + plan refs in AGENTS/ROADMAP), global tero, workspace-private analyses.
- See AGENTS.md, README.md, docs/ROADMAP.md for full process notes (Tero-first, hygiene, append-only, guards, local build).
- No changes to prior 0.1.0/0.2.0 content (append-only).
- v0.1.0 tag + gh release created; versions aligned in pyproject/VERSION/__init__.py .

