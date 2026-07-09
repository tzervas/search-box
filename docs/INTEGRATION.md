# Integration Guide

## Overview

This guide explains how to integrate the Search Box MCP server with various clients and applications.

## Claude Desktop Integration

### Prerequisites

- Claude Desktop installed
- Python 3.12+ installed
- Search Box repository cloned

### Configuration

1. Locate your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the Search Box server:

```json
{
  "mcpServers": {
    "search-box": {
      "command": "python",
      "args": ["/absolute/path/to/search-box/main.py"],
      "transport": "stdio"
    }
  }
}
```

3. Replace `/absolute/path/to/search-box/` with your actual path.

4. Restart Claude Desktop.

### Verification

1. Open Claude Desktop
2. Look for the MCP indicator (usually a plugin icon)
3. You should see "search-box" connected
4. Try asking: "Search for recent Python developments"
5. Claude should automatically use one of the search tools

### Troubleshooting

**Issue**: Server not connecting
- Check the path in config is absolute and correct
- Verify Python is in system PATH
- Check Claude Desktop logs

**Issue**: Tools not appearing
- Restart Claude Desktop
- Check server logs for errors
- Verify all dependencies are installed

## Custom MCP Client Integration

### Using Python SDK

```python
import asyncio
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client

async def use_search_tools():
    """Example: Using Search Box from a custom MCP client."""
    
    # Connect to server via stdio
    async with stdio_client(
        command="python",
        args=["main.py"],
        cwd="/path/to/search-box"
    ) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools]}")
            
            # Call a search tool
            result = await session.call_tool(
                name="web_search_duckduckgo",
                arguments={
                    "query": "Python async programming",
                    "num_results": 5
                }
            )
            
            # Process results
            print(result.content)

asyncio.run(use_search_tools())
```

### Using HTTP Transport

For remote deployments, modify `search_box/server.py`:

```python
# Change transport to streamable-http
def main():
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

Then configure client:

```json
{
  "mcpServers": {
    "search-box": {
      "url": "http://localhost:8000",
      "transport": "streamable-http"
    }
  }
}
```

## API Integration

### Direct Provider Usage

For non-MCP applications:

```python
import asyncio
from search_box import DuckDuckGoProvider, SearxNGProvider

async def integrate_search():
    """Integrate search into your application."""
    
    # Initialize provider
    provider = DuckDuckGoProvider()
    
    # Perform search
    results = await provider.web_search(
        query="user's search query",
        num_results=10
    )
    
    # Use results in your application
    for result in results:
        # Process: result.title, result.url, result.snippet
        pass

# In your async application
asyncio.run(integrate_search())
```

### Flask/FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from search_box import DuckDuckGoProvider

app = FastAPI()
provider = DuckDuckGoProvider()

class SearchRequest(BaseModel):
    query: str
    num_results: int = 10

@app.post("/search")
async def search(request: SearchRequest):
    """Search endpoint."""
    try:
        results = await provider.web_search(
            query=request.query,
            num_results=request.num_results
        )
        
        return {
            "results": [
                {
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet
                }
                for r in results
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Docker Integration

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY search_box/ ./search_box/
COPY main.py .

# Run server
CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  search-box:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t search-box .

# Run container
docker run -p 8000:8000 search-box

# With docker-compose
docker-compose up -d
```

## Environment Variables

Configure via environment variables:

```bash
# Provider settings
export SEARXNG_INSTANCE="https://searx.be"
export DUCKDUCKGO_TIMEOUT="30"

# Server settings
export MCP_SERVER_PORT="8000"
export MCP_SERVER_HOST="0.0.0.0"

# Logging
export LOG_LEVEL="INFO"
```

Update server to use:

```python
import os

# In server.py
searxng_instance = os.getenv("SEARXNG_INSTANCE", "https://searx.be")
provider = SearxNGProvider(instance_url=searxng_instance)
```

## Production Deployment

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name search-box.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Rate limiting
        limit_req zone=search_limit burst=10 nodelay;
    }
}
```

### Systemd Service

```ini
[Unit]
Description=Search Box MCP Server
After=network.target

[Service]
Type=simple
User=searchbox
WorkingDirectory=/opt/search-box
ExecStart=/usr/bin/python3 main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Monitoring

### Health Check Endpoint

Add to `server.py`:

```python
@mcp.resource("health://status")
def health_check() -> str:
    """Health check endpoint."""
    return "OK"
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('search-box.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics

```python
from prometheus_client import Counter, Histogram

search_requests = Counter('search_requests_total', 'Total search requests')
search_duration = Histogram('search_duration_seconds', 'Search duration')

# In tool function
@search_duration.time()
async def web_search_duckduckgo(query: str, num_results: int = 10) -> str:
    search_requests.inc()
    # ... existing code
```

## Security Considerations

### Production Checklist

- [ ] Enable HTTPS/TLS
- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Set up monitoring/alerting
- [ ] Configure firewall rules
- [ ] Enable logging
- [ ] Regular security updates
- [ ] Backup configuration

### Authentication

For HTTP transport, add API key:

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")

# Add dependency to endpoint
@app.post("/search", dependencies=[Depends(verify_api_key)])
async def search(...):
    pass
```

## Best Practices

1. **Use Connection Pooling**: Reuse HTTP clients across requests
2. **Implement Caching**: Cache frequent queries
3. **Add Retry Logic**: Handle transient failures
4. **Monitor Performance**: Track latency and errors
5. **Rotate Providers**: Load balance across instances
6. **Version APIs**: Maintain backward compatibility
7. **Document Changes**: Keep changelog updated

## Examples Repository

See `/examples/` directory for more integration examples:
- Claude Desktop configuration
- Custom client implementation
- API integration
- Docker deployment
- Monitoring setup

## Support

For integration issues:
1. Check logs for error messages
2. Review documentation
3. Search existing issues
4. Open new issue with details

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Claude Desktop Documentation](https://claude.ai/docs)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
