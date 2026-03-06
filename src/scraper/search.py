"""Bing Search API integration to find restaurant menu URLs."""

from __future__ import annotations

import logging

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


async def search_menu_url(restaurant_name: str) -> str:
    """Search Bing for the restaurant menu and return the best URL."""
    api_key = settings.bing_search_api_key
    if not api_key:
        raise RuntimeError(
            "BING_SEARCH_API_KEY is required. "
            "Set it in .env or as an environment variable."
        )

    query = f"{restaurant_name} lunch menu"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "count": "5", "mkt": "sv-SE"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            settings.bing_search_endpoint,
            headers=headers,
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()

    pages = data.get("webPages", {}).get("value", [])
    if not pages:
        raise RuntimeError(
            f"No search results found for '{restaurant_name}'. "
            "Try a more specific name or provide the menu URL directly."
        )

    # Prefer results whose URL or snippet hints at a menu
    menu_keywords = {"menu", "meny", "lunch", "matsedel"}
    for page in pages:
        url_lower = page["url"].lower()
        name_lower = page.get("name", "").lower()
        if any(kw in url_lower or kw in name_lower for kw in menu_keywords):
            logger.info("Found menu URL: %s", page["url"])
            return page["url"]

    # Fall back to the first result
    logger.info("Using first search result: %s", pages[0]["url"])
    return pages[0]["url"]
