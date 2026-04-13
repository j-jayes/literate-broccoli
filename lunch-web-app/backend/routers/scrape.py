"""Scrape router - calls the existing agentic scraper, and serves cached menus."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from ..cached_menus import CACHED_RESTAURANTS
from ..models import (
    CachedRestaurantsResponse,
    MenuItem,
    RestaurantMenu,
    ScrapeRequest,
    ScrapeResponse,
)
from .auth import require_auth

router = APIRouter(tags=["scrape"])
logger = logging.getLogger(__name__)


@router.get("/cached-restaurants", response_model=CachedRestaurantsResponse)
async def get_cached_restaurants(_token: str = Depends(require_auth)):
    """Return the pre-scraped menus for Holy Greens and Dockside Burgers."""
    restaurants = [
        RestaurantMenu(restaurant_name=r["restaurant_name"], items=r["items"])
        for r in CACHED_RESTAURANTS
    ]
    return CachedRestaurantsResponse(restaurants=restaurants)


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_menu(body: ScrapeRequest, _token: str = Depends(require_auth)):
    """Scrape a restaurant menu using the agentic browser."""
    from src.scraper.browse import browse_and_extract
    from src.scraper.search_restaurants import search_restaurant_url

    # Resolve starting URL: direct URL > Gemini + Google Search
    if body.menu_url:
        start_url = body.menu_url
    else:
        try:
            start_url = await search_restaurant_url(body.restaurant_name)
        except Exception as e:
            logger.exception("Restaurant search failed")
            raise HTTPException(
                status_code=502,
                detail=f"Could not find restaurant website: {e}",
            )

    logger.info("Scraping %s from %s", body.restaurant_name, start_url)

    try:
        final_url, items = await browse_and_extract(body.restaurant_name, start_url)
    except Exception as e:
        logger.exception("Scraping failed")
        raise HTTPException(status_code=502, detail=f"Scraping failed: {e}")

    if not items:
        raise HTTPException(
            status_code=404,
            detail=f"No menu items found at {final_url}",
        )

    menu_items = [
        MenuItem(
            name=item.name,
            price=item.price,
            category=item.category.value,
            description=item.description,
            subcategory=item.subcategory,
        )
        for item in items
    ]
    return ScrapeResponse(items=menu_items)
