"""Fetch and clean HTML content from a URL."""

from __future__ import annotations

import logging

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def fetch_page_text(url: str, *, timeout_s: float = 30.0) -> str:
    """Fetch a URL and return cleaned text content."""
    async with httpx.AsyncClient(
        timeout=timeout_s,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0 (compatible; LunchMenuBot/1.0)"},
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        html = resp.text

    return html_to_text(html)


def html_to_text(html: str) -> str:
    """Strip HTML tags and return clean text."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    lines = [" ".join(line.split()) for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def reduce_menu_text(text: str, *, max_chars: int = 50_000) -> str:
    """Trim text to stay within LLM context limits."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars]
