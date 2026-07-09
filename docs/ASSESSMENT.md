# search-box — Assessment & Gap Analysis

**Date:** 2026-07-08  
**Role:** Multi-provider **search MCP** (keyless / self-hosted oriented)  
**Note:** `main` was scaffold-only; **`dev` is cut from `develop`**, which contains the real implementation.

---

## 1. Branch reality

| Branch | Content |
|--------|---------|
| `main` | Initial scaffold (“Hello from search-box”) |
| **`develop` → now `dev`** | MCP server, providers (DuckDuckGo, SearXNG, …), cache, tests, docs |
| Gap | **main never received develop** — promote carefully |

---

## 2. Maturity (on develop/dev tree): **~2.5–3 / 5**

| Area | Notes |
|------|--------|
| MCP server module | Present |
| Providers | Partial set implemented |
| Cache | LRU/TTL work on develop |
| Tests | Present for base/cache/providers |
| Production hardening | Incomplete |
| Cabal wiring | None yet |

---

## 3. Gaps

| Gap | Sev |
|-----|-----|
| main ≠ develop | High — release confusion |
| Provider ToS / rate limits | High |
| Auth if HTTP exposed | Med |
| Eval of result quality | Med |
| Unified tool schema freeze | Med |
| CI on develop | Verify |

---

## 4. Integration (cabal)

Optional **search MCP** after promote-to-main and schema freeze. Complements webpuppet (no browser for simple search). Not a substitute for Tero corpus search.

See [ROADMAP.md](ROADMAP.md).

## Tero index

Layer-1 citation index: [docs/tero-index/](tero-index/) (`index.json`, `INDEX.md`, `MANIFEST.toml`).
