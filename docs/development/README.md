# Development Guide

## Setup

### Prerequisites

- Python 3.12+
- pip or uv package manager
- Git

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/tzervas/search-box.git
cd search-box

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installation
python -c "import search_box; print('Success')"
```

## Project Structure

```
search-box/
├── search_box/           # Main package
│   ├── __init__.py      # Package initialization
│   ├── base.py          # Abstract base classes
│   ├── server.py        # MCP server implementation
│   └── providers/       # Provider implementations
│       ├── __init__.py
│       ├── duckduckgo.py
│       └── searxng.py
├── tests/               # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_base.py
│   └── test_providers.py
├── docs/                # Documentation
├── main.py              # Entry point
├── pyproject.toml       # Project configuration
└── requirements.txt     # Dependencies
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_providers.py

# Run specific test
pytest tests/test_providers.py::test_duckduckgo_provider_success

# Run with coverage
pytest --cov=search_box --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Adding a New Provider

### 1. Create Provider Class

Create a new file in `search_box/providers/`:

```python
# search_box/providers/newprovider.py

from ..base import SearchProvider, SearchResult

class NewProvider(SearchProvider):
    """Provider for New Search Engine."""
    
    def __init__(self, name: str = "newprovider"):
        super().__init__(name)
        self.api_url = "https://api.newprovider.com/search"
    
    async def web_search(
        self, 
        query: str, 
        num_results: int = 10
    ) -> list[SearchResult]:
        """Implement search logic."""
        # Validation
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if num_results < 1 or num_results > 20:
            raise ValueError("num_results must be between 1 and 20")
        
        # HTTP request and parsing
        # ...
        
        return results
    
    def get_provider_info(self) -> dict:
        """Provider metadata."""
        info = super().get_provider_info()
        info.update({
            "description": "Description of the new provider",
            "keyless": True,
            "features": ["web_search"],
        })
        return info
```

### 2. Register in __init__.py

```python
# search_box/providers/__init__.py

from .newprovider import NewProvider

__all__ = [..., "NewProvider"]
```

### 3. Add to MCP Server

```python
# search_box/server.py

from search_box.providers import NewProvider

providers = {
    # ...
    "newprovider": NewProvider(),
}

@mcp.tool()
async def web_search_newprovider(query: str, num_results: int = 10) -> str:
    """Tool description."""
    provider = providers["newprovider"]
    results = await provider.web_search(query, num_results)
    return _format_search_results(results)
```

### 4. Write Tests

```python
# tests/test_newprovider.py

import pytest
from pytest_httpx import HTTPXMock
from search_box.providers import NewProvider

@pytest.mark.asyncio
async def test_newprovider_success(httpx_mock: HTTPXMock):
    # Mock responses
    httpx_mock.add_response(
        url="https://api.newprovider.com/search",
        json={"results": [...]},
        status_code=200
    )
    
    # Test
    provider = NewProvider()
    results = await provider.web_search("test", num_results=5)
    
    # Assertions
    assert len(results) > 0
```

## Code Style

### Formatting

- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black default)
- Use type hints for all function parameters and returns
- Follow PEP 8 style guide

### Docstrings

Use Google-style docstrings:

```python
def function(arg1: str, arg2: int = 10) -> list[str]:
    """
    Brief description.
    
    Longer description if needed.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When validation fails
    """
    pass
```

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Interactive Testing

```python
import asyncio
from search_box import DuckDuckGoProvider

async def debug_search():
    provider = DuckDuckGoProvider()
    results = await provider.web_search("test query", num_results=3)
    
    for result in results:
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet}\n")

asyncio.run(debug_search())
```

## Common Tasks

### Update Dependencies

```bash
# Update to latest compatible versions
pip install --upgrade -r requirements.txt

# Freeze current versions
pip freeze > requirements.txt
```

### Build Package

```bash
# Install build tools
pip install build

# Build distributions
python -m build

# Check build
ls dist/
```

### Run MCP Server Locally

```bash
# With stdio transport
python main.py

# Or module syntax
python -m search_box.server
```

## Best Practices

1. **Always write tests** for new features
2. **Use async/await** for I/O operations
3. **Handle errors gracefully** with proper error messages
4. **Validate inputs** before processing
5. **Document public APIs** with docstrings
6. **Keep providers independent** - no cross-dependencies
7. **Normalize results** to standard format
8. **Use type hints** for better IDE support

## Troubleshooting

### Import Errors

```bash
# Ensure package is in Python path
export PYTHONPATH=/path/to/search-box:$PYTHONPATH

# Or install in development mode
pip install -e .
```

### Test Failures

```bash
# Run tests with more verbose output
pytest -vv --tb=long

# Run single test for debugging
pytest tests/test_providers.py::test_name -s
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and add tests
4. Run tests: `pytest`
5. Commit changes: `git commit -m "Add my feature"`
6. Push to branch: `git push origin feature/my-feature`
7. Create Pull Request

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Python Async Guide](https://docs.python.org/3/library/asyncio.html)
- [Pytest Documentation](https://docs.pytest.org/)
