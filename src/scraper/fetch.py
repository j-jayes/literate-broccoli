"""Fetch and clean HTML content from a URL."""

from __future__ import annotations

import logging
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LunchMenuBot/1.0)"}


async def fetch_page_html(url: str, *, timeout_s: float = 30.0) -> str:
    """Fetch a URL and return raw HTML."""
    async with httpx.AsyncClient(
        timeout=timeout_s,
        follow_redirects=True,
        headers=_HTTP_HEADERS,
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text


async def fetch_page_text(url: str, *, timeout_s: float = 30.0) -> str:
    """Fetch a URL and return cleaned text content."""
    html = await fetch_page_html(url, timeout_s=timeout_s)
    return html_to_text(html)


def html_to_text(html: str) -> str:
    """Strip HTML tags and return clean text."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    lines = [" ".join(line.split()) for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def extract_links(html: str, base_url: str) -> list[dict[str, str]]:
    """Extract links from HTML, returning [{url, text}] with absolute URLs.

    Filters out external domains, anchors, and non-HTTP links.
    """
    soup = BeautifulSoup(html, "lxml")
    base_domain = urlparse(base_url).netloc
    seen: set[str] = set()
    links: list[dict[str, str]] = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        abs_url = urljoin(base_url, href)
        parsed = urlparse(abs_url)
        if parsed.scheme not in ("http", "https"):
            continue
        # Only keep same-domain links
        if parsed.netloc != base_domain:
            continue
        # Deduplicate
        clean = parsed._replace(fragment="").geturl()
        if clean in seen:
            continue
        seen.add(clean)
        text = a.get_text(" ", strip=True)[:100]
        links.append({"url": clean, "text": text or "(no text)"})

    return links


def reduce_menu_text(text: str, *, max_chars: int = 50_000) -> str:
    """Trim text to stay within LLM context limits."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars]
