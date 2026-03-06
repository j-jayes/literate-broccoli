"""MCP tool: get_restaurant_menu.

Orchestrates: URL resolution -> agentic browsing -> LLM extraction -> Adaptive Card.
The browsing agent navigates restaurant websites step-by-step to find the menu page,
handling SPAs, location selection, and multi-page menus automatically.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from src.cards.poll import build_poll_card
from src.config import settings
from src.scraper.browse import browse_and_extract

logger = logging.getLogger(__name__)


async def get_restaurant_menu(
    restaurant_name: str,
    menu_url: Optional[str] = None,
) -> dict[str, Any]:
    """Fetch a restaurant menu and return an Adaptive Card poll.

    The tool uses an agentic browsing approach: starting from the given URL
    (or a search result), it navigates the website step-by-step using LLM
    reasoning to find the actual menu page with prices.

    Args:
        restaurant_name: The name of the restaurant (e.g. "Pizzeria Napoli").
        menu_url: Starting URL (homepage or menu page). If not provided,
                  Bing Search is used (requires BING_SEARCH_API_KEY).

    Returns:
        An Adaptive Card JSON object with menu items as poll choices.
    """
    logger.info("Getting menu for: %s", restaurant_name)

    # 1. Resolve starting URL
    if menu_url:
        start_url = menu_url
    elif settings.bing_search_api_key:
        from src.scraper.search import search_menu_url
        start_url = await search_menu_url(restaurant_name)
    else:
        raise RuntimeError(
            "Please provide a menu_url, or set BING_SEARCH_API_KEY to enable web search."
        )
    logger.info("Starting URL: %s", start_url)

    # 2. Browse the website and extract menu items
    final_url, items = await browse_and_extract(restaurant_name, start_url)
    if not items:
        raise RuntimeError(
            f"Could not extract any menu items from {final_url}. "
            "The page may not contain a readable menu."
        )
    logger.info("Extracted %d menu items from %s", len(items), final_url)

    # 3. Build the Adaptive Card poll
    card = build_poll_card(restaurant_name, items)
    return card
