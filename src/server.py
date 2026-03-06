"""MCP server entry point for the lunch menu poll tool."""

from __future__ import annotations

import logging

from fastmcp import FastMCP

from src.config import settings
from src.tools.menu import get_restaurant_menu

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

mcp = FastMCP(settings.mcp_server_name)


@mcp.tool
async def get_menu_poll(restaurant_name: str, menu_url: str = "") -> dict:
    """Fetch a restaurant's menu and return an Adaptive Card poll for MS Teams.

    Given a restaurant name and menu URL, this tool will:
    1. Fetch the menu page
    2. Use AI to extract structured menu items (name, price, category)
    3. Return an Adaptive Card with a poll where team members can pick their lunch

    If no menu_url is provided and Bing Search is configured, it will search for the menu automatically.

    Args:
        restaurant_name: Name of the restaurant, e.g. "Rekas Burgers"
        menu_url: Direct URL to the restaurant's menu page, e.g. "https://rekas.se/meny/"
    """
    return await get_restaurant_menu(restaurant_name, menu_url=menu_url or None)


# ASGI app for production deployment (uvicorn src.server:app)
app = mcp.http_app()

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
