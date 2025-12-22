"""Tests for search providers."""

import pytest
import httpx
from pytest_httpx import HTTPXMock

from search_box.providers.duckduckgo import DuckDuckGoProvider
from search_box.providers.searxng import SearxNGProvider
from search_box.base import SearchResult


# Sample DuckDuckGo HTML response
DUCKDUCKGO_HTML = """
<html>
<body>
<div class="result">
    <a class="result__a" href="https://example.com/python">Python Programming</a>
    <a class="result__snippet">Learn Python programming from scratch</a>
</div>
<div class="result">
    <a class="result__a" href="https://example.com/tutorial">Python Tutorial</a>
    <a class="result__snippet">Complete Python tutorial for beginners</a>
</div>
</body>
</html>
"""

# Sample SearxNG JSON response
SEARXNG_JSON = {
    "results": [
        {
            "title": "Python Programming",
            "url": "https://example.com/python",
            "content": "Learn Python programming from scratch"
        },
        {
            "title": "Python Tutorial",
            "url": "https://example.com/tutorial",
            "content": "Complete Python tutorial for beginners"
        }
    ]
}


@pytest.mark.asyncio
async def test_duckduckgo_provider_success(httpx_mock: HTTPXMock):
    """Test DuckDuckGo provider with successful response."""
    httpx_mock.add_response(
        method="POST",
        url="https://html.duckduckgo.com/html/",
        text=DUCKDUCKGO_HTML,
        status_code=200
    )
    
    provider = DuckDuckGoProvider()
    results = await provider.web_search("Python programming", num_results=5)
    
    assert len(results) == 2
    assert isinstance(results[0], SearchResult)
    assert results[0].title == "Python Programming"
    assert results[0].url == "https://example.com/python"
    assert "Learn Python" in results[0].snippet
    assert results[0].source_provider == "duckduckgo"


@pytest.mark.asyncio
async def test_duckduckgo_provider_empty_query():
    """Test DuckDuckGo provider with empty query."""
    provider = DuckDuckGoProvider()
    
    with pytest.raises(ValueError, match="Query cannot be empty"):
        await provider.web_search("", num_results=5)


@pytest.mark.asyncio
async def test_duckduckgo_provider_invalid_num_results():
    """Test DuckDuckGo provider with invalid num_results."""
    provider = DuckDuckGoProvider()
    
    with pytest.raises(ValueError, match="num_results must be between 1 and 20"):
        await provider.web_search("test", num_results=0)
    
    with pytest.raises(ValueError, match="num_results must be between 1 and 20"):
        await provider.web_search("test", num_results=21)


@pytest.mark.asyncio
async def test_duckduckgo_provider_http_error(httpx_mock: HTTPXMock):
    """Test DuckDuckGo provider with HTTP error."""
    httpx_mock.add_response(
        method="POST",
        url="https://html.duckduckgo.com/html/",
        status_code=500
    )
    
    provider = DuckDuckGoProvider()
    
    with pytest.raises(RuntimeError, match="DuckDuckGo search failed"):
        await provider.web_search("test", num_results=5)


@pytest.mark.asyncio
async def test_searxng_provider_success(httpx_mock: HTTPXMock):
    """Test SearxNG provider with successful response."""
    httpx_mock.add_response(
        method="GET",
        url="https://searx.be/search?q=Python+programming&format=json&pageno=1",
        json=SEARXNG_JSON,
        status_code=200
    )
    
    provider = SearxNGProvider(instance_url="https://searx.be")
    results = await provider.web_search("Python programming", num_results=5)
    
    assert len(results) == 2
    assert isinstance(results[0], SearchResult)
    assert results[0].title == "Python Programming"
    assert results[0].url == "https://example.com/python"
    assert "Learn Python" in results[0].snippet
    assert results[0].source_provider == "searxng"


@pytest.mark.asyncio
async def test_searxng_provider_empty_query():
    """Test SearxNG provider with empty query."""
    provider = SearxNGProvider()
    
    with pytest.raises(ValueError, match="Query cannot be empty"):
        await provider.web_search("", num_results=5)


@pytest.mark.asyncio
async def test_searxng_provider_invalid_num_results():
    """Test SearxNG provider with invalid num_results."""
    provider = SearxNGProvider()
    
    with pytest.raises(ValueError, match="num_results must be between 1 and 20"):
        await provider.web_search("test", num_results=0)
    
    with pytest.raises(ValueError, match="num_results must be between 1 and 20"):
        await provider.web_search("test", num_results=21)


@pytest.mark.asyncio
async def test_searxng_provider_http_error(httpx_mock: HTTPXMock):
    """Test SearxNG provider with HTTP error."""
    httpx_mock.add_response(
        method="GET",
        url="https://searx.be/search?q=test&format=json&pageno=1",
        status_code=500
    )
    
    provider = SearxNGProvider(instance_url="https://searx.be")
    
    with pytest.raises(RuntimeError, match="SearxNG search failed"):
        await provider.web_search("test", num_results=5)


def test_duckduckgo_provider_info():
    """Test DuckDuckGo provider info."""
    provider = DuckDuckGoProvider()
    info = provider.get_provider_info()
    
    assert info["name"] == "duckduckgo"
    assert info["keyless"] is True
    assert "web_search" in info["features"]


def test_searxng_provider_info():
    """Test SearxNG provider info."""
    provider = SearxNGProvider(instance_url="https://searx.be")
    info = provider.get_provider_info()
    
    assert info["name"] == "searxng"
    assert info["keyless"] is True
    assert "web_search" in info["features"]
    assert info["instance"] == "https://searx.be"
