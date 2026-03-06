"""Tests for the agentic web browsing module."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.schemas import ExtractedMenuItem, MenuCategory
from src.scraper.browse import (
    BrowseDecision,
    _build_user_prompt,
    _parse_decision,
    browse_and_extract,
)

FAKE_ITEMS = [
    ExtractedMenuItem(name="Margherita", price=95, category=MenuCategory.main),
    ExtractedMenuItem(name="Cola", price=25, category=MenuCategory.drink),
]

MENU_HTML = """<html><body>
<h1>Our Menu</h1>
<p>Margherita 95 kr</p>
<p>Cola 25 kr</p>
</body></html>"""

HOMEPAGE_HTML = """<html><body>
<h1>Welcome to Pizza Place</h1>
<a href="/menu">Our Menu</a>
<a href="/about">About Us</a>
<a href="/contact">Contact</a>
</body></html>"""


class TestParseDecision:
    def test_parse_extract(self):
        raw = json.dumps({"action": "extract", "reason": "Found menu"})
        d = _parse_decision(raw)
        assert d.action == "extract"
        assert d.reason == "Found menu"

    def test_parse_navigate(self):
        raw = json.dumps({"action": "navigate", "reason": "Menu link found", "url": "https://example.com/menu"})
        d = _parse_decision(raw)
        assert d.action == "navigate"
        assert d.url == "https://example.com/menu"

    def test_parse_fail(self):
        raw = json.dumps({"action": "fail", "reason": "No menu found"})
        d = _parse_decision(raw)
        assert d.action == "fail"

    def test_parse_with_markdown_fences(self):
        raw = '```json\n{"action": "extract", "reason": "Menu page"}\n```'
        d = _parse_decision(raw)
        assert d.action == "extract"

    def test_parse_invalid_json_raises(self):
        with pytest.raises(Exception):
            _parse_decision("not json at all")


class TestBuildUserPrompt:
    def test_contains_restaurant_name(self):
        prompt = _build_user_prompt("Pizza Place", "https://example.com", "some text", [], set())
        assert "Pizza Place" in prompt
        assert "https://example.com" in prompt

    def test_contains_links(self):
        links = [{"url": "https://example.com/menu", "text": "Menu"}]
        prompt = _build_user_prompt("Test", "https://example.com", "text", links, set())
        assert "https://example.com/menu" in prompt
        assert "Menu" in prompt

    def test_shows_visited_urls(self):
        visited = {"https://example.com/old"}
        prompt = _build_user_prompt("Test", "https://example.com", "text", [], visited)
        assert "https://example.com/old" in prompt


class TestBrowseAndExtract:
    @patch("src.scraper.browse.extract_menu")
    @patch("src.scraper.browse._call_llm_for_navigation")
    @patch("src.scraper.browse.fetch_page_html", new_callable=AsyncMock)
    def test_direct_extract(self, mock_fetch, mock_llm, mock_extract):
        """Page is already the menu - extract immediately."""
        mock_fetch.return_value = MENU_HTML
        mock_llm.return_value = json.dumps({"action": "extract", "reason": "Menu found"})
        mock_extract.return_value = FAKE_ITEMS

        url, items = asyncio.run(browse_and_extract("Pizza Place", "https://example.com/menu"))
        assert url == "https://example.com/menu"
        assert len(items) == 2
        assert mock_fetch.call_count == 1

    @patch("src.scraper.browse.extract_menu")
    @patch("src.scraper.browse._call_llm_for_navigation")
    @patch("src.scraper.browse.fetch_page_html", new_callable=AsyncMock)
    def test_navigate_then_extract(self, mock_fetch, mock_llm, mock_extract):
        """Homepage -> navigate to menu -> extract."""
        mock_fetch.side_effect = [HOMEPAGE_HTML, MENU_HTML]
        mock_llm.side_effect = [
            json.dumps({"action": "navigate", "reason": "Found menu link", "url": "https://example.com/menu"}),
            json.dumps({"action": "extract", "reason": "Menu page found"}),
        ]
        mock_extract.return_value = FAKE_ITEMS

        url, items = asyncio.run(browse_and_extract("Pizza Place", "https://example.com"))
        assert url == "https://example.com/menu"
        assert len(items) == 2
        assert mock_fetch.call_count == 2

    @patch("src.scraper.browse._call_llm_for_navigation")
    @patch("src.scraper.browse.fetch_page_html", new_callable=AsyncMock)
    def test_fail_action_raises(self, mock_fetch, mock_llm):
        """LLM says it can't find a menu -> RuntimeError."""
        mock_fetch.return_value = "<html><body>Nothing here</body></html>"
        mock_llm.return_value = json.dumps({"action": "fail", "reason": "No menu on this site"})

        with pytest.raises(RuntimeError, match="No menu on this site"):
            asyncio.run(browse_and_extract("Ghost Restaurant", "https://example.com"))

    @patch("src.scraper.browse.extract_menu")
    @patch("src.scraper.browse._call_llm_for_navigation")
    @patch("src.scraper.browse.fetch_page_html", new_callable=AsyncMock)
    def test_revisit_guard(self, mock_fetch, mock_llm, mock_extract):
        """If LLM tries to revisit a URL, fall back to extracting from current page."""
        mock_fetch.return_value = MENU_HTML
        # LLM tries to navigate back to the same URL
        mock_llm.return_value = json.dumps({
            "action": "navigate",
            "reason": "Go back",
            "url": "https://example.com",
        })
        mock_extract.return_value = FAKE_ITEMS

        url, items = asyncio.run(browse_and_extract("Pizza", "https://example.com"))
        assert len(items) == 2
        # Should have extracted from the current page instead of looping
        mock_extract.assert_called_once()

    @patch("src.scraper.browse.extract_menu")
    @patch("src.scraper.browse._call_llm_for_navigation")
    @patch("src.scraper.browse.fetch_page_html", new_callable=AsyncMock)
    def test_multi_step_navigation(self, mock_fetch, mock_llm, mock_extract):
        """Homepage -> location page -> menu page."""
        location_html = """<html><body>
        <h1>Choose Location</h1>
        <a href="/stockholm/menu">Stockholm</a>
        <a href="/gothenburg/menu">Gothenburg</a>
        </body></html>"""

        mock_fetch.side_effect = [HOMEPAGE_HTML, location_html, MENU_HTML]
        mock_llm.side_effect = [
            json.dumps({"action": "navigate", "reason": "Need to pick location", "url": "https://example.com/locations"}),
            json.dumps({"action": "navigate", "reason": "Pick Stockholm", "url": "https://example.com/stockholm/menu"}),
            json.dumps({"action": "extract", "reason": "Found the menu"}),
        ]
        mock_extract.return_value = FAKE_ITEMS

        url, items = asyncio.run(browse_and_extract("Pizza Place", "https://example.com"))
        assert url == "https://example.com/stockholm/menu"
        assert mock_fetch.call_count == 3
