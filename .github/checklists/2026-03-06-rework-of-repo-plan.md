# Rework: MCP Server for Restaurant Menu Polling

## Context
The codebase was over-engineered with 4 microservices, Parquet storage, SQL models, etc. for what is fundamentally a simple workflow: someone says a restaurant name in Teams -> the system finds the menu -> presents it as a poll. We're rebuilding as a clean MCP server using FastMCP that Copilot Studio can connect to directly.

## Architecture

```
User in Teams -> Copilot Studio Agent -> MCP Server (this repo)
                                           |-- Tool: get_restaurant_menu(name)
                                           |   |-- Bing Search for menu URL
                                           |   |-- Scrape/fetch the page
                                           |   |-- LLM extracts structured menu items
                                           |-- Returns: Adaptive Card JSON for poll
```

## MCP Tools to Expose

### 1. `get_restaurant_menu(restaurant_name: str) -> AdaptiveCardPoll`
- Searches Bing for "{restaurant_name} menu"
- Fetches the menu page HTML
- Uses LLM (Azure OpenAI primary, OpenAI/Gemini fallback) to extract structured menu items
- Returns an Adaptive Card JSON with flat-list poll format for Teams

**Input:** Restaurant name (string)
**Output:** Adaptive Card JSON with menu items as poll choices

## LLM Provider Fallback Strategy
1. Try Azure OpenAI first
2. If quota limit hit (429), fall back to OpenAI
3. If that fails, fall back to Google Gemini 2.5 Flash
4. Log which provider was used

## Key Dependencies
- `fastmcp` - MCP server framework
- `httpx` - HTTP client
- `beautifulsoup4` - HTML parsing
- `openai` - Azure OpenAI and OpenAI
- `google-genai` - Gemini fallback
- `pydantic` / `pydantic-settings` - Data models and config

## Verification
1. Run `python -m src.server` - server starts without errors
2. Run tests: `pytest tests/`
3. Test with MCP Inspector or fastmcp dev tools
4. Connect to Copilot Studio and test end-to-end
