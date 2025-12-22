#!/usr/bin/env python3
"""
Example script demonstrating Search Box usage.

This script shows how to use the search providers programmatically.
Note: Network access required for actual searches.
"""

import asyncio
from search_box import DuckDuckGoProvider, SearxNGProvider


async def example_basic_search():
    """Example: Basic search with DuckDuckGo."""
    print("=" * 60)
    print("Example 1: Basic DuckDuckGo Search")
    print("=" * 60)
    
    provider = DuckDuckGoProvider()
    
    try:
        results = await provider.web_search("Python async programming", num_results=3)
        
        print(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Snippet: {result.snippet[:100]}...")
            print()
    except Exception as e:
        print(f"Error: {e}")


async def example_multi_provider():
    """Example: Compare results from multiple providers."""
    print("\n" + "=" * 60)
    print("Example 2: Multi-Provider Comparison")
    print("=" * 60)
    
    query = "Model Context Protocol"
    
    providers = {
        "DuckDuckGo": DuckDuckGoProvider(),
        "SearxNG": SearxNGProvider(instance_url="https://searx.be"),
    }
    
    for name, provider in providers.items():
        print(f"\n{name} Results:")
        print("-" * 40)
        
        try:
            results = await provider.web_search(query, num_results=2)
            
            if results:
                for result in results:
                    print(f"• {result.title}")
                    print(f"  {result.url}")
            else:
                print("No results found")
        except Exception as e:
            print(f"Error: {e}")


async def example_error_handling():
    """Example: Proper error handling."""
    print("\n" + "=" * 60)
    print("Example 3: Error Handling")
    print("=" * 60)
    
    provider = DuckDuckGoProvider()
    
    # Test empty query
    print("\nTesting empty query:")
    try:
        await provider.web_search("", num_results=5)
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Test invalid num_results
    print("\nTesting invalid num_results:")
    try:
        await provider.web_search("test", num_results=100)
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")
    
    print("\n✓ Error handling works correctly")


async def example_provider_info():
    """Example: Get provider information."""
    print("\n" + "=" * 60)
    print("Example 4: Provider Information")
    print("=" * 60)
    
    providers = [
        DuckDuckGoProvider(),
        SearxNGProvider(),
    ]
    
    for provider in providers:
        info = provider.get_provider_info()
        print(f"\nProvider: {info['name']}")
        print(f"Type: {info['type']}")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Keyless: {info.get('keyless', 'N/A')}")
        print(f"Features: {', '.join(info.get('features', []))}")


async def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Search Box - Usage Examples" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Note: Examples 1 and 2 require network access
    # They will fail in offline environments
    
    # Example 1: Basic search
    # await example_basic_search()
    
    # Example 2: Multi-provider comparison
    # await example_multi_provider()
    
    # Example 3: Error handling (no network required)
    await example_error_handling()
    
    # Example 4: Provider info (no network required)
    await example_provider_info()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nNote: Network-dependent examples are commented out.")
    print("Uncomment them to run with internet access.")
    print("\nTo use the MCP server with Claude Desktop:")
    print("  python main.py")


if __name__ == "__main__":
    asyncio.run(main())
