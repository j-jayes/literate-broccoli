# Lunch Menu Poll

A suite of tools for finding restaurant menus and running lunch polls at the office. Started as an over-engineered microservices project, reworked into three focused components:

1. **MCP Server** — an MCP (Model Context Protocol) server that Copilot Studio agents can call to find menus and generate Adaptive Card polls for Microsoft Teams
2. **Lunch Web App** — a standalone FastAPI + React web app where teams can scrape a menu, create a poll session, and collect orders with live updates
3. **Teams Bot** — a Teams bot that integrates the lunch ordering flow directly into Microsoft Teams
4. **Presentation** — Reveal.js slides documenting the project (published via GitHub Pages)

## MCP Server (`src/`)

### How it works

1. A user in Teams tells the Copilot Studio agent a restaurant name
2. The agent calls this MCP server's `get_menu_poll` tool
3. The server uses an agentic scraper to navigate restaurant websites step-by-step, using an LLM to find and extract menu items
4. Returns an Adaptive Card poll that team members can use to pick their lunch

### LLM provider fallback chain

Azure OpenAI → OpenAI → Google Gemini

### Quick start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

python -m src.server   # Run the MCP server
pytest tests/ -v       # Run tests
```

### Configuration

Set these in `.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key (used for search + LLM fallback) |
| `AZURE_OPENAI_ENDPOINT` | Recommended | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Recommended | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Recommended | Model deployment name (default: gpt-4o) |
| `OPENAI_API_KEY` | Fallback | OpenAI API key (used if Azure fails) |

### Connecting to Copilot Studio

1. Run this MCP server (or deploy it to Azure App Service)
2. In Copilot Studio, go to your agent's **Tools** page
3. Select **Add a tool** > **New tool** > **Model Context Protocol**
4. Enter the server URL and configure authentication
5. The `get_menu_poll` tool will be available to your agent

## Lunch Web App (`lunch-web-app/`)

A standalone web app (FastAPI backend + React/Fluent UI frontend) deployed on Azure Container Apps.

- **Admin flow:** authenticate → paste a restaurant URL → agentic scraper extracts the menu → review and create a poll session
- **Poll flow:** share the session link → team members pick their orders → live SSE updates → download a CSV summary

Deployed at: `https://lunch-web-app.happyrock-baafa260.swedencentral.azurecontainerapps.io/`

## Teams Bot (`teams-lunch-bot/`)

A Teams bot integration with Adaptive Card-based ordering, deployable to Azure App Service.

## Presentation (`docs/`)

Reveal.js slides covering the project architecture and LLM fallback strategy. Published via GitHub Pages.

## Project structure

```
src/                        # MCP server
  server.py                 # FastMCP entry point
  config.py                 # Environment-based settings
  models/schemas.py         # Pydantic models for menu items
  scraper/
    browse.py               # Agentic web browser for menu discovery
    search_restaurants.py   # Restaurant search
    fetch.py                # HTML fetching and cleaning
    extract.py              # LLM menu extraction with fallback chain
  cards/poll.py             # Adaptive Card poll builder
  tools/menu.py             # Main tool orchestration
tests/                      # MCP server tests
lunch-web-app/              # Standalone web app
  backend/                  # FastAPI (auth, scrape, sessions, SSE)
  frontend/                 # React + Fluent UI SPA
  Dockerfile                # Multi-stage build
teams-lunch-bot/            # Teams bot
  app.py / bot.py           # Bot framework entry points
  cards/                    # Adaptive Card templates
  teams_app_manifest/       # Teams app manifest
docs/                       # Reveal.js presentation slides
.github/checklists/         # Archived planning docs and checklists
```

## Development history

The project went through several phases:

1. **Initial scaffolding** (Feb 2026) — over-engineered microservices architecture with 4 services, PostgreSQL, Redis, Bicep templates
2. **Rework to MCP server** (Mar 2026) — simplified to a single FastMCP server with agentic scraping and LLM fallback chain
3. **Web app** (Mar 2026) — built a standalone FastAPI + React app with live polling, deployed on Azure Container Apps
4. **Teams bot** (Mar 2026) — added a dedicated Teams bot integration
5. **Presentation** (Mar 2026) — created Reveal.js slides, published via GitHub Pages

Previous planning docs are archived in [.github/checklists/](.github/checklists/).
