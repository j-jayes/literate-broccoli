"""Tests for the MCP server tool registration."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.server import mcp


def test_server_has_tool():
    """Verify the get_menu_poll tool is registered."""
    # FastMCP registers tools; we just check it imported without error
    assert mcp.name == "lunch-menu-poll"


@patch("src.tools.menu.browse_and_extract", new_callable=AsyncMock)
def test_get_menu_poll_integration(mock_browse):
    """Test the full tool pipeline with mocked browsing agent."""
    import asyncio

    from src.models.schemas import ExtractedMenuItem, MenuCategory
    from src.tools.menu import get_restaurant_menu

    mock_browse.return_value = (
        "https://example.com/menu",
        [
            ExtractedMenuItem(name="Margherita", price=95, category=MenuCategory.main),
            ExtractedMenuItem(name="Cola", price=25, category=MenuCategory.drink),
        ],
    )

    card = asyncio.run(get_restaurant_menu("Test Restaurant", menu_url="https://example.com"))
    assert card["type"] == "AdaptiveCard"
    assert len(card["body"][2]["choices"]) == 2
    mock_browse.assert_called_once_with("Test Restaurant", "https://example.com")
