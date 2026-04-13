# Lunch Menu Poll

This repo currently focuses on two active parts:

1. **Lunch Web App** — a FastAPI + React app for scraping menus and running office lunch polls.
2. **Presentation** — Reveal.js slides documenting the architecture and workflow.

The scraping implementation now lives directly in `lunch-web-app/backend`.

## Lunch Web App (`lunch-web-app/`)

A standalone web app (FastAPI backend + React/Fluent UI frontend) deployed on Azure Container Apps.

- **Admin flow:** authenticate → paste a restaurant URL → agentic scraper extracts the menu → review and create a poll session
- **Poll flow:** share the session link → team members pick their orders → live SSE updates → download a CSV summary

Deployed at: `https://lunch-web-app.happyrock-baafa260.swedencentral.azurecontainerapps.io/`

### Scraper configuration

Set these in `.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Recommended | Gemini key used for search/fallback during scraping |
| `AZURE_OPENAI_ENDPOINT` | Optional | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Optional | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Optional | Azure deployment name |
| `OPENAI_API_KEY` | Optional | OpenAI fallback key |

### Quick check

```bash
pip install -r requirements.txt
pip install -r lunch-web-app/requirements.txt
python -m compileall -q lunch-web-app/backend scripts
```

## Presentation (`docs/`)

Reveal.js slides covering the project architecture and LLM fallback strategy. Published via GitHub Pages.

## Project structure

```
scripts/                    # Automation scripts (scrape compare, code generation)
lunch-web-app/              # Standalone web app
  automation/               # Menu refresh config and hash state
    restaurants.yml         # Restaurant scrape registry
    menu_hashes.json        # Last-known-good menu hashes
  backend/                  # FastAPI (auth, scrape, sessions, SSE)
    scraper/                # Agentic scraper implementation
    scraper_settings.py     # LLM/scraper settings
    scraper_schemas.py      # Extracted menu schemas
  frontend/                 # React + Fluent UI SPA
  Dockerfile                # Multi-stage build
docs/                       # Reveal.js presentation slides
.github/checklists/         # Archived planning docs and checklists
```

## TODO

- Add comprehensive tests for lunch-web-app backend and frontend (unit + API + integration).

## Repo Reorganization Plan (Best Practice)

If starting from scratch, this repo would be cleaner with an explicit app-first monorepo layout and stricter boundaries.

1. Adopt a top-level `apps/` + `packages/` structure.
  - `apps/lunch-web-app` for deployable web app code.
  - `apps/teams-lunch-bot` for Teams bot runtime.
  - `apps/mcp-server` only if MCP runtime remains a first-class deployable.
  - `packages/scraper-core` for reusable scraping logic currently in `lunch-web-app/backend/scraper`.
  - `packages/menu-models` for shared Pydantic schemas and menu normalization.

2. Move automation into app-owned directories.
  - Keep scheduled refresh assets under `apps/lunch-web-app/automation/`.
  - Keep generated outputs and templates clearly separated from hand-edited source.

3. Split CI workflows by concern.
  - `ci.yml` for fast lint/type/smoke checks.
  - `menu-refresh.yml` for scheduled expensive LLM scraping.
  - `deploy.yml` for image build and deployment promotion.

4. Standardize environment and secret management.
  - `.env.example` at repo root plus app-specific `.env.example` files.
  - Document one-to-one mapping between env vars and GitHub Actions secrets.
  - Prefer GitHub Environments for prod/stage scoped secrets.

5. Re-introduce tests in a modern structure.
  - `apps/lunch-web-app/tests/backend` and `apps/lunch-web-app/tests/frontend`.
  - Add scraper deterministic tests around hash/normalization and fixture-based extraction.
  - Keep live website scraping out of default CI and run it only in scheduled jobs.

6. Reduce ambiguity around active runtimes.
  - Mark each app as `active`, `maintenance`, or `archived` in README.
  - Move historical artifacts and exploratory code into an `archive/` folder when no longer deployed.

## Development history

The project went through several phases:

1. **Initial scaffolding** (Feb 2026) — over-engineered microservices architecture with 4 services, PostgreSQL, Redis, Bicep templates
2. **Rework to MCP server** (Mar 2026) — simplified to a single FastMCP server with agentic scraping and LLM fallback chain
3. **Web app** (Mar 2026) — built a standalone FastAPI + React app with live polling, deployed on Azure Container Apps
4. **Teams bot** (Mar 2026) — added a dedicated Teams bot integration
5. **Presentation** (Mar 2026) — created Reveal.js slides, published via GitHub Pages

Previous planning docs are archived in [.github/checklists/](.github/checklists/).
