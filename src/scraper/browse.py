"""Agentic web browser for restaurant menu discovery.

Uses an LLM to navigate restaurant websites step-by-step:
- Analyze each page to decide if it contains a menu
- Follow links to find menu pages, select locations, etc.
- Extract menu items once the right page is found
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from pydantic import BaseModel

from src.config import settings
from src.scraper.extract import extract_menu
from src.scraper.fetch import (
    extract_links,
    fetch_page_html,
    html_to_text,
    reduce_menu_text,
)

logger = logging.getLogger(__name__)

MAX_STEPS = 5
PAGE_TEXT_PREVIEW = 4000  # chars of page text to show the LLM for navigation decisions


class BrowseDecision(BaseModel):
    """LLM's decision about what to do with the current page."""
    action: str  # "extract", "navigate", or "fail"
    reason: str
    url: Optional[str] = None  # required when action == "navigate"


BROWSE_SYSTEM_PROMPT = """\
You are a web browsing agent helping find a restaurant's menu page with food items and prices.

You will be given:
- The restaurant name we're looking for
- The current page URL
- A text preview of the current page content
- A list of links found on the page
- URLs already visited (don't revisit these)

Your job is to decide what to do next. Respond with JSON:

If this page contains a menu with food items (dishes, meals, etc.) and ideally prices:
{"action": "extract", "reason": "This page contains the menu with items and prices"}

If this page does NOT have the menu but you see a promising link, navigate to it:
{"action": "navigate", "reason": "The menu link looks like it leads to the actual menu", "url": "https://..."}

If you truly cannot find any path to a menu:
{"action": "fail", "reason": "Explanation of why no menu could be found"}

Guidelines:
- Look for links containing words like "meny", "menu", "lunch", "mat", "food", "matsedel"
- If there are multiple locations/restaurants, pick one that seems most relevant or most central
- If there's a weekly lunch menu ("veckans lunch", "lunchmeny", "dagens"), prefer that over the regular menu
- If the page has menu items but NO prices, look for links to a specific location, "order online" ("beställ"), or a lunch-specific page that might have prices before deciding to extract
- NEVER navigate to a URL that was already visited
- Prefer the simplest path to a menu WITH prices
- If you've navigated several pages and the best you can find is items without prices, extract what you have
- Only respond with valid JSON, nothing else"""


def _build_user_prompt(
    restaurant_name: str,
    current_url: str,
    page_text: str,
    links: list[dict[str, str]],
    visited: set[str],
) -> str:
    """Build the user message for the navigation LLM."""
    # Truncate page text for the navigation decision
    preview = page_text[:PAGE_TEXT_PREVIEW]
    if len(page_text) > PAGE_TEXT_PREVIEW:
        preview += "\n... (truncated)"

    links_text = "\n".join(
        f"  - {link['url']}  \"{link['text']}\""
        for link in links[:50]  # cap at 50 links
    )
    if not links_text:
        links_text = "  (no links found)"

    visited_text = "\n".join(f"  - {u}" for u in visited) if visited else "  (none)"

    return f"""\
Restaurant: {restaurant_name}
Current URL: {current_url}

PAGE TEXT:
{preview}

LINKS ON THIS PAGE:
{links_text}

ALREADY VISITED:
{visited_text}

What should we do? Respond with JSON only."""


def _parse_decision(raw: str) -> BrowseDecision:
    """Parse the LLM's JSON response into a BrowseDecision."""
    text = raw.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    data = json.loads(text)
    return BrowseDecision.model_validate(data)


def _call_llm_for_navigation(user_prompt: str) -> str:
    """Call the LLM to get a navigation decision. Uses the same fallback chain."""
    providers: list[tuple[str, callable]] = []

    if settings.azure_openai_endpoint and settings.azure_openai_api_key:
        providers.append(("Azure OpenAI", _call_azure_openai))
    if settings.openai_api_key:
        providers.append(("OpenAI", _call_openai))
    if settings.google_api_key:
        providers.append(("Gemini", _call_gemini))

    if not providers:
        raise RuntimeError("No LLM provider configured for navigation.")

    last_error: Exception | None = None
    for name, call_fn in providers:
        try:
            logger.info("Trying %s for navigation decision...", name)
            return call_fn(user_prompt)
        except Exception as e:
            logger.warning("Provider %s failed for navigation: %s", name, e)
            last_error = e
            continue

    raise RuntimeError(f"All LLM providers failed for navigation. Last error: {last_error}")


def _call_azure_openai(user_prompt: str) -> str:
    from openai import AzureOpenAI
    client = AzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
    )
    resp = client.chat.completions.create(
        model=settings.azure_openai_deployment,
        messages=[
            {"role": "system", "content": BROWSE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=300,
    )
    return resp.choices[0].message.content


def _call_openai(user_prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": BROWSE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=300,
    )
    return resp.choices[0].message.content


def _call_gemini(user_prompt: str) -> str:
    from google import genai
    client = genai.Client(api_key=settings.google_api_key)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=f"{BROWSE_SYSTEM_PROMPT}\n\n{user_prompt}",
    )
    return response.text


async def browse_and_extract(
    restaurant_name: str,
    start_url: str,
) -> tuple[str, list]:
    """Navigate a restaurant website to find the menu and extract items.

    Args:
        restaurant_name: Name of the restaurant.
        start_url: URL to start browsing from (homepage or menu page).

    Returns:
        Tuple of (final_url, list of ExtractedMenuItem).

    Raises:
        RuntimeError: If menu cannot be found after MAX_STEPS.
    """
    current_url = start_url
    visited: set[str] = set()

    for step in range(MAX_STEPS):
        logger.info("Step %d/%d: Fetching %s", step + 1, MAX_STEPS, current_url)
        visited.add(current_url)

        # Fetch and parse the page
        html = await fetch_page_html(current_url)
        text = html_to_text(html)
        links = extract_links(html, current_url)
        logger.info("Got %d chars of text and %d links", len(text), len(links))

        # Ask the LLM what to do
        user_prompt = _build_user_prompt(
            restaurant_name, current_url, text, links, visited
        )
        raw_response = _call_llm_for_navigation(user_prompt)
        decision = _parse_decision(raw_response)
        logger.info("Decision: %s - %s", decision.action, decision.reason)

        if decision.action == "extract":
            # This page has the menu - extract items
            reduced = reduce_menu_text(text)
            items = extract_menu(current_url, reduced)
            logger.info("Extracted %d menu items from %s", len(items), current_url)
            return current_url, items

        elif decision.action == "navigate":
            if not decision.url:
                raise RuntimeError("LLM decided to navigate but provided no URL")
            if decision.url in visited:
                logger.warning("LLM tried to revisit %s, trying to extract from current page", decision.url)
                reduced = reduce_menu_text(text)
                items = extract_menu(current_url, reduced)
                return current_url, items
            current_url = decision.url

        elif decision.action == "fail":
            raise RuntimeError(
                f"Could not find menu: {decision.reason}"
            )
        else:
            raise RuntimeError(f"Unknown action from LLM: {decision.action}")

    # Exhausted steps - try extracting from the last page as a fallback
    logger.warning("Exhausted %d steps, attempting extraction from last page", MAX_STEPS)
    html = await fetch_page_html(current_url)
    text = html_to_text(html)
    reduced = reduce_menu_text(text)
    items = extract_menu(current_url, reduced)
    return current_url, items
