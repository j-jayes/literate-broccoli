# Lunch Menu Poll - MCP Server

An MCP (Model Context Protocol) server that finds restaurant menus and generates Adaptive Card polls for Microsoft Teams. Designed to work with Copilot Studio agents.

## How it works

1. A user in Teams tells the Copilot Studio agent a restaurant name
2. The agent calls this MCP server's `get_menu_poll` tool
3. The server searches Bing for the restaurant's menu, scrapes the page, and uses AI to extract menu items
4. Returns an Adaptive Card poll that team members can use to pick their lunch

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys (Azure OpenAI, Bing Search, etc.)

# Run the MCP server
python -m src.server

# Run tests
pytest tests/ -v
```

## Configuration

Set these in `.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key (used for search + LLM fallback) |
| `AZURE_OPENAI_ENDPOINT` | Recommended | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Recommended | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Recommended | Model deployment name (default: gpt-4o) |
| `OPENAI_API_KEY` | Fallback | OpenAI API key (used if Azure fails) |

The LLM provider fallback chain: Azure OpenAI -> OpenAI -> Google Gemini.

## MCP Tool

### `get_menu_poll(restaurant_name: str) -> dict`

Searches for a restaurant's menu and returns an Adaptive Card poll.

**Input:** Restaurant name (e.g. "Pizzeria Napoli Lund")
**Output:** Adaptive Card JSON with menu items as radio-button choices

## Connecting to Copilot Studio

1. Run this MCP server (or deploy it to Azure App Service)
2. In Copilot Studio, go to your agent's **Tools** page
3. Select **Add a tool** > **New tool** > **Model Context Protocol**
4. Enter the server URL and configure authentication
5. The `get_menu_poll` tool will be available to your agent

## Project structure

```
src/
  server.py          # MCP server entry point (FastMCP)
  config.py          # Environment-based settings
  models/
    schemas.py       # Pydantic models for menu items
  scraper/
    search.py        # Bing Search API integration
    fetch.py         # HTML fetching and cleaning
    extract.py       # LLM menu extraction with fallback chain
  cards/
    poll.py          # Adaptive Card poll builder
  tools/
    menu.py          # Main tool orchestration
tests/
  test_extract.py    # LLM extraction tests (mocked)
  test_poll_card.py  # Adaptive Card generation tests
  test_server.py     # Server integration tests
```

## Development history

Previous planning docs are archived in [.github/checklists/](.github/checklists/).
