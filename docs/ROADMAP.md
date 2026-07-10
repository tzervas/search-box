# search-box — Product Roadmap

**Status:** Living (2026-07-08)  
**North star:** Reliable multi-provider **search MCP** for agents — keyless where possible, cached, rate-limited, honest about provider limits.

Companion: [ASSESSMENT.md](ASSESSMENT.md).  
**Branch policy:** `dev` carries product work (from former `develop`); promote to `main` when Wave A exits.

---

## Waves

### Wave A — Unify branches & freeze MVP

| ID | Work |
|----|------|
| SB-A1 | Keep `dev` as integration branch (this tree) |
| SB-A2 | CI: pytest on `dev` |
| SB-A3 | README install from real package entrypoints |
| SB-A4 | Freeze MCP tool list v0.1 |
| SB-A5 | PR `dev` → `main` when green |

### Wave B — Providers & resilience

| ID | Work |
|----|------|
| SB-B1 | Provider interface + health checks |
| SB-B2 | Rate limit + backoff per provider |
| SB-B3 | SearXNG self-host first-class config |
| SB-B4 | Optional Brave/Google only with explicit API keys |
| SB-B5 | Result normalization schema |

### Wave C — Agent product

| ID | Work |
|----|------|
| SB-C1 | cabal-devmelopner client snippet |
| SB-C2 | Cache metrics + TTL tuning |
| SB-C3 | Optional security-mcp screen on query strings |
| SB-C4 | 1.0.0 after multi-provider soak |

---

## API plan

### MCP tools (target v0.1)

| Tool | Purpose | Args |
|------|---------|------|
| `search` | Run query | `query`, `providers?[]`, `limit?` |
| `search_list_providers` | Inventory | — |
| `search_health` | Provider health | — |

### Result envelope

```json
{
  "query": "...",
  "results": [
    {
      "title": "...",
      "url": "https://...",
      "snippet": "...",
      "provider": "duckduckgo",
      "rank": 1
    }
  ],
  "errors": [{ "provider": "searxng", "error": "timeout" }]
}
```

### Config

```toml
# search-box.toml
default_providers = ["duckduckgo", "searxng"]
cache_ttl_seconds = 600
cache_max_entries = 1000

[searxng]
base_url = "http://127.0.0.1:8080"
```

Keys (if any) via env: `BRAVE_API_KEY`, `GOOGLE_CSE_*` — never tool args.

### Python package entry

```text
search-box          # CLI
search-box-mcp      # stdio MCP server
```

---

## PR plan

1. Docs assessment + roadmap on `dev`  
2. CI + README truth  
3. Tool schema freeze + tests  
4. Promote `dev` → `main`  
5. Rate limits + SearXNG polish  
6. cabal integration notes  

---

## Non-goals

- Scraping behind logins by default  
- Replacing Tero corpus search  
- Unbounded multi-provider fanout without budgets  

## Semver baseline (appended 2026-07-10)

Per plan.md (Local GHCR + semver section) + user: semver + releases for packages writ large. Local builds (no Actions). GHCR podman preference for containers.

- Baseline v0.1.0 for search-box (pyproject + VERSION + __init__ + this).
- See README.md for Semver + Releases details, cites to Tero searches (e.g. plan refs in AGENTS), git survey (no prior tags).
- python -m build + hygiene + tag + gh release executed (dists).
- tero regen + check.sh green pre-tag.
- Cites: plan.md, tero (roadmap--pr-plan, agents--hygiene-tero-land-status-2026-07-09 via /root/git/scripts/tero.sh search-box), analyses.

Next bumps: hygiene gate, update-tero.sh, append docs (append-only).

