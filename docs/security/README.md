# Security Documentation

## Overview

This document outlines the security considerations, practices, and limitations of the Search Box MCP server.

## Security Features

### 1. No API Keys Required

All search providers are **keyless**:
- No credentials to store or manage
- No risk of API key exposure
- No authentication token leakage

### 2. Privacy-Respecting Providers

All providers prioritize user privacy:
- **DuckDuckGo**: No user tracking, anonymous searches
- **SearxNG**: Privacy-focused meta-search, no logging

### 3. HTTPS Communication

All HTTP requests use HTTPS:
- Encrypted communication with providers
- Protection against man-in-the-middle attacks
- Certificate verification enabled by default

### 4. Input Validation

Strict parameter validation:
```python
# Query validation
if not query or not query.strip():
    raise ValueError("Query cannot be empty")

# Range validation
if num_results < 1 or num_results > 20:
    raise ValueError("num_results must be between 1 and 20")
```

### 5. Error Handling

Safe error handling without exposing sensitive data:
- Generic error messages to clients
- Detailed errors logged server-side only
- No stack traces in production responses

## Security Limitations

### 1. Public Instances

SearxNG uses public instances:
- Instances are not under our control
- May have varying security postures
- Could be monitored or logged by instance operators

**Mitigation**: Use trusted instances or self-host SearxNG

### 2. HTML Scraping

DuckDuckGo provider uses HTML scraping:
- Dependent on DuckDuckGo's site structure
- No official API contract
- Changes could break functionality

**Mitigation**: Monitor for breaking changes, have fallback providers

### 3. No Rate Limiting

No built-in rate limiting:
- Could be abused if exposed publicly
- May trigger provider rate limits

**Mitigation**: Implement rate limiting in deployment layer

### 4. User Input

Search queries come from LLM/user:
- Could contain sensitive information
- Queries sent to external providers
- No query logging, but providers may log

**Mitigation**: Educate users about query privacy

## Best Practices

### 1. Deployment

```bash
# Run behind reverse proxy
# nginx, Apache, or Caddy with rate limiting

# Example nginx config
location /mcp {
    limit_req zone=mcp burst=5;
    proxy_pass http://localhost:8000;
}
```

### 2. Network Security

```bash
# Firewall rules
# Only allow necessary outbound HTTPS
ufw allow out 443/tcp

# Restrict inbound to localhost only
ufw deny in from any to any
```

### 3. Monitoring

```python
import logging

# Log security-relevant events
logger.info(f"Search query from {client_id}: {query[:50]}...")
logger.warning(f"Rate limit exceeded for {client_id}")
logger.error(f"Provider error: {provider_name}")
```

### 4. Dependency Management

```bash
# Regularly update dependencies
pip install --upgrade -r requirements.txt

# Check for vulnerabilities
pip install safety
safety check

# Or use automated tools
pip install pip-audit
pip-audit
```

## Threat Model

### In Scope

1. **Query Privacy**: Protecting user search queries
2. **Dependency Vulnerabilities**: Known CVEs in dependencies
3. **Input Validation**: Preventing injection attacks
4. **Rate Limiting**: Preventing abuse

### Out of Scope

1. **Provider Security**: Security of DuckDuckGo/SearxNG
2. **Result Manipulation**: Altered search results from providers
3. **Network-Level Attacks**: DDoS, BGP hijacking
4. **Client Security**: Security of Claude Desktop or MCP clients

## Known Issues

### 1. No Authentication

Current implementation has no authentication:
- Any client can connect via stdio
- No user identification or authorization

**Status**: By design for local use  
**Future**: Add OAuth for remote deployments

### 2. No Query Sanitization

Queries are passed as-is to providers:
- Special characters not escaped
- Could trigger provider-specific behaviors

**Status**: Providers handle edge cases  
**Future**: Add query sanitization if needed

### 3. No Content Filtering

Results returned without filtering:
- May contain sensitive/inappropriate content
- No content moderation

**Status**: Providers handle content moderation  
**Future**: Add optional filtering layer

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. Email security contact (see repository)
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (optional)

We aim to respond within 48 hours.

## Compliance

### Data Privacy

- **GDPR**: No personal data collected or stored
- **CCPA**: No consumer data sale or tracking
- **HIPAA**: Not applicable (no health data)

### Third-Party Services

Queries sent to:
- DuckDuckGo (Privacy Policy: https://duckduckgo.com/privacy)
- SearxNG instances (varies by instance)

Users should review third-party privacy policies.

## Audit Log

| Date | Version | Change |
|------|---------|--------|
| 2024-12 | 0.1.0 | Initial security documentation |

## Security Checklist

Before deployment:

- [ ] Dependencies updated
- [ ] Vulnerability scan completed
- [ ] Rate limiting configured
- [ ] HTTPS enforced
- [ ] Logging configured
- [ ] Firewall rules set
- [ ] Monitoring enabled
- [ ] Backup strategy defined

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [MCP Security Considerations](https://modelcontextprotocol.io/security)

---

Last updated: December 2024
