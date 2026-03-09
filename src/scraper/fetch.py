"""Fetch and clean HTML/PDF content from a URL."""

from __future__ import annotations

import logging
from urllib.parse import urljoin, urlparse

import httpx
import pymupdf
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7",
}


def _is_pdf(url: str, content_type: str) -> bool:
    """Detect if a response is a PDF based on URL or Content-Type."""
    return (
        url.lower().rstrip("/").endswith(".pdf")
        or "application/pdf" in content_type.lower()
    )


def _pdf_to_text(data: bytes) -> str:
    """Extract text from PDF bytes using pymupdf."""
    doc = pymupdf.open(stream=data, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    text = "\n".join(pages)
    lines = [" ".join(line.split()) for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


async def fetch_page_html(url: str, *, timeout_s: float = 30.0) -> str:
    """Fetch a URL and return raw HTML, or extracted text if the URL is a PDF."""
    async with httpx.AsyncClient(
        timeout=timeout_s,
        follow_redirects=True,
        headers=_HTTP_HEADERS,
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if _is_pdf(url, content_type):
            logger.info("Detected PDF, extracting text: %s", url)
            return _pdf_to_text(resp.content)
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


def extract_links(
    html: str,
    base_url: str,
    *,
    allow_external: bool = False,
) -> list[dict[str, str]]:
    """Extract links from HTML, returning [{url, text}] with absolute URLs.

    Args:
        html: Raw HTML content.
        base_url: The URL the HTML was fetched from (used for resolving relative URLs).
        allow_external: If True, include cross-domain links (useful for ordering platforms).
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
        is_external = parsed.netloc != base_domain
        if is_external and not allow_external:
            continue
        # Deduplicate
        clean = parsed._replace(fragment="").geturl()
        if clean in seen:
            continue
        seen.add(clean)
        text = a.get_text(" ", strip=True)[:100]
        tag = " [EXTERNAL]" if is_external else ""
        links.append({"url": clean, "text": (text or "(no text)") + tag})

    return links


def detect_pdf_links(html: str, base_url: str) -> list[dict[str, str]]:
    """Find links that point to PDF files (common for Swedish lunch menus)."""
    soup = BeautifulSoup(html, "lxml")
    pdfs: list[dict[str, str]] = []
    seen: set[str] = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        abs_url = urljoin(base_url, href)
        if abs_url in seen:
            continue
        if abs_url.lower().endswith(".pdf") or "/pdf" in abs_url.lower():
            seen.add(abs_url)
            text = a.get_text(" ", strip=True)[:100]
            pdfs.append({"url": abs_url, "text": text or "(PDF link)"})

    return pdfs


def reduce_menu_text(text: str, *, max_chars: int = 50_000) -> str:
    """Trim text to stay within LLM context limits."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars]
