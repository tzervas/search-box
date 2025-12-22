#!/usr/bin/env python3
"""
CLI tool for testing Search Box providers.

Usage:
    python cli.py search "your query" [--provider duckduckgo|searxng] [--num-results 5]
    python cli.py providers
"""

import argparse
import asyncio
import sys
from search_box import DuckDuckGoProvider, SearxNGProvider


async def search_command(args):
    """Execute search command."""
    # Initialize provider
    if args.provider == "duckduckgo":
        provider = DuckDuckGoProvider()
    elif args.provider == "searxng":
        provider = SearxNGProvider()
    else:
        print(f"Unknown provider: {args.provider}")
        return 1
    
    try:
        print(f"Searching with {provider.name}...")
        results = await provider.web_search(args.query, num_results=args.num_results)
        
        if not results:
            print("No results found.")
            return 0
        
        print(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   URL: {result.url}")
            if result.snippet:
                print(f"   {result.snippet}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def providers_command(args):
    """List available providers."""
    providers = [
        DuckDuckGoProvider(),
        SearxNGProvider(),
    ]
    
    print("Available Providers:\n")
    for provider in providers:
        info = provider.get_provider_info()
        print(f"• {info['name']}")
        print(f"  Description: {info.get('description', 'N/A')}")
        print(f"  Keyless: {info.get('keyless', False)}")
        print(f"  Features: {', '.join(info.get('features', []))}")
        print()
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search Box CLI - Test search providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py search "Python MCP" --provider duckduckgo --num-results 5
  python cli.py providers
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Perform a search")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--provider",
        choices=["duckduckgo", "searxng"],
        default="duckduckgo",
        help="Search provider to use (default: duckduckgo)"
    )
    search_parser.add_argument(
        "--num-results",
        type=int,
        default=5,
        help="Number of results to return (default: 5)"
    )
    
    # Providers command
    subparsers.add_parser("providers", help="List available providers")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "search":
        return asyncio.run(search_command(args))
    elif args.command == "providers":
        return providers_command(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
