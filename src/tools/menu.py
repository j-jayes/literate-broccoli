"""MCP tool: get_restaurant_menu.

Orchestrates: URL fetch -> LLM extraction -> Adaptive Card.
Optionally uses Bing search if a URL is not provided and BING_SEARCH_API_KEY is set.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from src.cards.poll import build_poll_card
from src.config import settings
from src.scraper.extract import extract_menu
from src.scraper.fetch import fetch_page_text, reduce_menu_text

logger = logging.getLogger(__name__)


async def get_restaurant_menu(
    restaurant_name: str,
    menu_url: Optional[str] = None,
) -> dict[str, Any]:
    """Fetch a restaurant menu and return an Adaptive Card poll.

    Args:
        restaurant_name: The name of the restaurant (e.g. "Pizzeria Napoli").
        menu_url: Direct URL to the menu page. If not provided, Bing Search
                  is used (requires BING_SEARCH_API_KEY).

    Returns:
        An Adaptive Card JSON object with menu items as poll choices.
    """
    logger.info("Getting menu for: %s", restaurant_name)

    # 1. Resolve the menu URL
    if menu_url:
        url = menu_url
    elif settings.bing_search_api_key:
        from src.scraper.search import search_menu_url
        url = await search_menu_url(restaurant_name)
    else:
        raise RuntimeError(
            "Please provide a menu_url, or set BING_SEARCH_API_KEY to enable web search."
        )
    logger.info("Menu URL: %s", url)

    # 2. Fetch and clean the page
    text = await fetch_page_text(url)
    text = reduce_menu_text(text)
    logger.info("Fetched %d chars of text", len(text))

    # 3. Extract menu items via LLM
    items = extract_menu(url, text)
    if not items:
        raise RuntimeError(
            f"Could not extract any menu items from {url}. "
            "The page may not contain a readable menu."
        )
    logger.info("Extracted %d menu items", len(items))

    # 4. Build the Adaptive Card poll
    card = build_poll_card(restaurant_name, items)
    return card
