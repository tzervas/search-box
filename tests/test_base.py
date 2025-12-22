"""Tests for base classes."""

import pytest
from search_box.base import SearchResult, SearchProvider


def test_search_result_creation():
    """Test SearchResult dataclass creation."""
    result = SearchResult(
        title="Test Title",
        url="https://example.com",
        snippet="Test snippet",
        source_provider="test"
    )
    
    assert result.title == "Test Title"
    assert result.url == "https://example.com"
    assert result.snippet == "Test snippet"
    assert result.source_provider == "test"


def test_search_result_without_provider():
    """Test SearchResult without source_provider."""
    result = SearchResult(
        title="Test Title",
        url="https://example.com",
        snippet="Test snippet"
    )
    
    assert result.source_provider is None


def test_search_provider_abstract():
    """Test that SearchProvider cannot be instantiated."""
    with pytest.raises(TypeError):
        SearchProvider("test")


class MockProvider(SearchProvider):
    """Mock provider for testing."""
    
    async def web_search(self, query: str, num_results: int = 10):
        return [
            SearchResult(
                title="Mock Result",
                url="https://mock.com",
                snippet="Mock snippet",
                source_provider=self.name
            )
        ]


@pytest.mark.asyncio
async def test_mock_provider():
    """Test mock provider implementation."""
    provider = MockProvider("mock")
    results = await provider.web_search("test")
    
    assert len(results) == 1
    assert results[0].title == "Mock Result"
    assert results[0].source_provider == "mock"


def test_provider_info():
    """Test provider info method."""
    provider = MockProvider("mock")
    info = provider.get_provider_info()
    
    assert info["name"] == "mock"
    assert info["type"] == "MockProvider"
