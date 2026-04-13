"""Unified restaurant search using Gemini with Google Search grounding.

All entry points (MCP tool, web app, browse agent) share this single module.
"""

from __future__ import annotations

import logging
import re

import httpx

from ..scraper_settings import settings

logger = logging.getLogger(__name__)

_URL_RE = re.compile(r"https?://[^\s)\]\"',]+")

_REVIEW_DOMAINS = {
    "tripadvisor", "yelp", "google.com/maps", "thefork", "facebook.com",
    "instagram.com", "twitter.com", "linkedin.com", "youtube.com",
    "wikipedia.org", "trustpilot", "happycow", "foursquare",
}

_GROUNDING_REDIRECT_PREFIX = "https://vertexaisearch.cloud.google.com/"


def _get_client():
    """Create a Gemini client."""
    from google import genai
    api_key = settings.google_api_key
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is required for restaurant search. "
            "Set it in .env or as an environment variable."
        )
    return genai.Client(api_key=api_key)


def _extract_urls_from_text(text: str) -> list[str]:
    """Extract URLs from LLM response text, skipping grounding redirects."""
    urls = _URL_RE.findall(text)
    # Strip trailing punctuation that regex may capture
    cleaned = []
    for u in urls:
        u = u.rstrip(".")
        if not u.startswith(_GROUNDING_REDIRECT_PREFIX):
            cleaned.append(u)
    return cleaned


async def _resolve_grounding_redirects(
    redirect_urls: list[str],
) -> list[str]:
    """Follow grounding redirect URLs (302) to get actual destination URLs."""
    resolved = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in redirect_urls:
            try:
                resp = await client.get(url, follow_redirects=False)
                location = resp.headers.get("location")
                if location:
                    resolved.append(location)
            except Exception:
                logger.debug("Failed to resolve redirect: %s", url)
    return resolved


def _is_review_site(url: str) -> bool:
    return any(domain in url.lower() for domain in _REVIEW_DOMAINS)


async def search_restaurant_url(
    restaurant_name: str,
    city: str = "Malmö",
) -> str:
    """Find the best menu URL for a restaurant using Gemini + Google Search.

    Returns:
        The best URL found for the restaurant's menu page.

    Raises:
        RuntimeError: If no URL can be found.
    """
    from google.genai import types

    client = _get_client()
    prompt = (
        f"Find the official website or menu page URL for the restaurant "
        f'"{restaurant_name}" in {city}, Sweden. '
        f"I need a direct URL to their lunch menu or main menu page. "
        f"Prefer the restaurant's own website over delivery platforms. "
        f"Return ONLY the URL, nothing else."
    )

    logger.info("Searching for restaurant URL: %s in %s", restaurant_name, city)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0,
        ),
    )

    # Strategy 1: Extract URL from response text
    text_urls = _extract_urls_from_text(response.text or "")
    if text_urls:
        logger.info("Found URL from response text: %s", text_urls[0])
        return text_urls[0]

    # Strategy 2: Resolve grounding chunk redirects
    gm = response.candidates[0].grounding_metadata if response.candidates else None
    if gm and gm.grounding_chunks:
        redirect_urls = [
            c.web.uri for c in gm.grounding_chunks
            if c.web and c.web.uri
        ]
        resolved = await _resolve_grounding_redirects(redirect_urls)
        # Prefer non-review sites
        for url in resolved:
            if not _is_review_site(url):
                logger.info("Found URL from grounding chunk: %s", url)
                return url
        if resolved:
            logger.info("Found URL from grounding chunk (fallback): %s", resolved[0])
            return resolved[0]

    raise RuntimeError(
        f"Could not find a URL for '{restaurant_name}' in {city}. "
        "Try providing the menu URL directly."
    )


async def web_search(query: str, max_results: int = 10) -> list[dict[str, str]]:
    """Search the web using Gemini + Google Search grounding.

    Used by the browse agent as a mid-navigation fallback when it gets stuck.

    Returns:
        List of dicts with keys: url, title, snippet.
    """
    from google.genai import types

    client = _get_client()
    prompt = (
        f"Search the web for: {query}\n"
        f"Return the top {max_results} results as a numbered list. "
        f"For each result, include the full URL and a brief description. "
        f"Format each line as: URL - description"
    )

    logger.info("Web search: %s", query)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0,
        ),
    )

    results: list[dict[str, str]] = []

    # Extract URLs from response text
    text = response.text or ""
    for line in text.splitlines():
        urls = _URL_RE.findall(line)
        for url in urls:
            url = url.rstrip(".")
            if url.startswith(_GROUNDING_REDIRECT_PREFIX):
                continue
            results.append({
                "url": url,
                "title": line.strip(),
                "body": line.strip(),
            })

    # Also resolve grounding chunk redirects for additional URLs
    gm = response.candidates[0].grounding_metadata if response.candidates else None
    if gm and gm.grounding_chunks:
        redirect_urls = [
            c.web.uri for c in gm.grounding_chunks
            if c.web and c.web.uri
        ]
        resolved = await _resolve_grounding_redirects(redirect_urls)
        seen = {r["url"] for r in results}
        for url in resolved:
            if url not in seen:
                results.append({"url": url, "title": "", "body": ""})
                seen.add(url)

    # Filter out review sites
    filtered = [r for r in results if not _is_review_site(r["url"])]
    if not filtered:
        return results[:max_results]

    return filtered[:max_results]
