
# AGENTS.md — search-box

**Use Tero + cabal-devmelopner for work here.**

## Tero (Layer-1 corpus index)

Repo has `docs/tero-index/index.json` (generated/ refreshed via tero-mcp/scripts/generate_lite_index.py).

**Rule:** Use tero queries before large greps or assumptions.
- Grok: tero__text_search / query_by_id (token "local-dev")
- Direct: tero-mcp-lite --index docs/tero-index/index.json
- cabal-devmelopner: auto-detects local index when run from within this tree (or set TERO_INDEX_PATH).

Example:
```bash
cd /root/git/search-box
# agent with context:
uv run --project ../cabal-devmelopner cabal-devmelopner "task description here" --use-tero
```

Citations point at file:line — open them.

## Working with cabal-devmelopner agent tool

This project is prepared for integration:
- Tero index committed on chore/tero-index-cabal-ready (and PRable to dev)
- Local auto index support in cabal
- This AGENTS.md

**PR flow (protect main/dev):**
- Create/checkout feature or chore branch
- Make changes (agent will often use working branch)
- PR the branch → `dev` (then dev → main when ready)

## Local checks

Look for:
- scripts/check.sh
- Cargo.toml / pyproject.toml + standard commands (cargo test, uv run pytest, ruff, etc.)

Run checks before considering work complete.

## Further reading

- README.md
- docs/ROADMAP.md or ROADMAP.md (if present)
- docs/ASSESSMENT.md or similar for intent/gaps
- ../cabal-devmelopner/docs/* for agent architecture
- ../tero-mcp for how indexes are built and served

Leave mycelium isolated; all coordination here targets the other repos + cabal.

## Hygiene + tero land status (2026-07-09)
- Task: Land chore/tero + hygiene for search-box (per plan.md priority 1).
- Tero-first: used `/root/git/scripts/tero.sh search-box ...` (identify, text_search, etc) before edits/assumptions.
- Read plan.md + models (ROADMAP, ASSESSMENT, LOCAL_CHECKS, update-tero.sh, check.sh, etc).
- Checkout dev; merge --no-ff chore/tero-index-cabal-ready; push.
- ./scripts/check.sh : 31 tests passed, green.
- update-tero.sh search-box; committed tero refresh (MANIFEST + prior).
- Merged to main --no-ff; propagated (dev <-> main --no-ff, pushed).
- Appended this status (append-only).
- Verified: branches synced (origin/dev, origin/main current), checks green, tero queries resolve (see docs/tero-index).
- Citations from tero used to open AGENTS:24, ROADMAP:1 etc.
- Note: now tero index + check/AGENTS/LOCAL_CHECKS on main/dev (was only on chore).


## Secrets, .env and git-secrets protection (2026-07-10, tooling 1.0 wave)
**WHAT**:
- .gitignore now contains standard block for `.env`, `.env.local`, `.env.*.local`, `*.env`, `*.key`, `secrets/` (templates explicitly allowed with `!`).
- git-secrets protection activated: `git secrets --install -f` (hooks in .git/hooks including pre-commit/prepare-commit-msg), `--register-aws`, custom adds for `XAI_API_KEY` + variants + `ANTHROPIC_API_KEY` + `OPENAI_API_KEY` + sk- patterns.
- `.gitallowed` created with safe exceptions for key *names* in docs/comments/examples (real secret *values* will still be caught).
- `git secrets --scan` now clean across tree.
**WHY**: cabal-devmelopner and agents actively consume `XAI_API_KEY` (and will for Claude/ADK post-stability). Leaking keys in git history is a critical supply chain / compliance risk. Complements security-mcp scans. Enforces 1.0 "hardened" criteria at the source (pre-commit + hygiene).
**WHY NOT**: Relying on .gitignore alone is insufficient (doesn't scan code/comments for accidental pastes of values); git-secrets chosen as lightweight, established (awslabs), no heavy deps. Allowed patterns only for identifiers (not values).
**After fresh clone / in new worktree (mandatory)**:
```
git secrets --install
git secrets --register-aws
git secrets --add 'XAI_API_KEY'
git secrets --add 'ANTHROPIC_API_KEY'
git secrets --add 'OPENAI_API_KEY'
# then verify
git secrets --scan
```
Enhance `scripts/check.sh` with `git secrets --scan || exit 1`.
Cites: tooling-wave-1.0-readiness doc (this task), user request post dev-support tranche, tero hygiene sections, cabal XAI provider code + AGENTS.
All changes: Google-style WHAT/WHY/WHY-NOT, append-only, branch/worktree guarded, tero-first audit.
