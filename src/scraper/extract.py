"""LLM-based menu extraction with provider fallback chain.

Order: Azure OpenAI -> OpenAI -> Google Gemini.
Falls back on rate limit (429) or missing credentials.
"""

from __future__ import annotations

import logging
from typing import Protocol

from src.config import settings
from src.models.schemas import ExtractedMenu, ExtractedMenuItem

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Extract menu items from the provided restaurant page text. "
    "Return only real purchasable items. "
    "category must be one of: main, side, drink, dessert, other. "
    "If the price is not present, return price=null. "
    "If the price is present, return it as a number without currency symbols. "
    "Prices may appear as '125:-', '125 kr', '125 SEK', or just '125'. "
    "IMPORTANT: When a category header (e.g. 'Dips', 'Milkshakes', 'Sauces') "
    "is followed by a list of flavours or varieties, create a SEPARATE item for "
    "each individual flavour/variety (e.g. 'Dips - Garlic Mayo', 'Dips - BBQ Sauce'). "
    "Do NOT group them under a single item."
)


class MenuExtractor(Protocol):
    def extract(self, url: str, text: str) -> list[ExtractedMenuItem]: ...


class AzureOpenAIExtractor:
    def extract(self, url: str, text: str) -> list[ExtractedMenuItem]:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
        completion = client.beta.chat.completions.parse(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"URL: {url}\n\nPAGE_TEXT:\n{text}"},
            ],
            response_format=ExtractedMenu,
        )
        parsed: ExtractedMenu = completion.choices[0].message.parsed
        logger.info("Azure OpenAI extracted %d items", len(parsed.items))
        return parsed.items


class OpenAIExtractor:
    def extract(self, url: str, text: str) -> list[ExtractedMenuItem]:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        completion = client.beta.chat.completions.parse(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"URL: {url}\n\nPAGE_TEXT:\n{text}"},
            ],
            response_format=ExtractedMenu,
        )
        parsed: ExtractedMenu = completion.choices[0].message.parsed
        logger.info("OpenAI extracted %d items", len(parsed.items))
        return parsed.items


class GeminiExtractor:
    def extract(self, url: str, text: str) -> list[ExtractedMenuItem]:
        from google import genai

        client = genai.Client(api_key=settings.google_api_key)
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"URL: {url}\n\nPAGE_TEXT:\n{text}\n\n"
            "Respond with JSON matching this schema: "
            '{"items": [{"name": str, "price": number|null, '
            '"category": "main"|"side"|"drink"|"dessert"|"other", '
            '"description": str|null}]}'
        )
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
        )
        import json
        raw = response.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
        data = json.loads(raw)
        menu = ExtractedMenu.model_validate(data)
        logger.info("Gemini extracted %d items", len(menu.items))
        return menu.items


def _get_extractors() -> list[tuple[str, MenuExtractor]]:
    """Build ordered list of available extractors based on configured credentials."""
    extractors: list[tuple[str, MenuExtractor]] = []
    if settings.azure_openai_endpoint and settings.azure_openai_api_key:
        extractors.append(("Azure OpenAI", AzureOpenAIExtractor()))
    if settings.openai_api_key:
        extractors.append(("OpenAI", OpenAIExtractor()))
    if settings.google_api_key:
        extractors.append(("Gemini", GeminiExtractor()))
    return extractors


def extract_menu(url: str, text: str) -> list[ExtractedMenuItem]:
    """Extract menu items using the fallback chain.

    Tries each configured provider in order. Falls back on rate limit
    errors (429) or other failures.
    """
    extractors = _get_extractors()
    if not extractors:
        raise RuntimeError(
            "No LLM provider configured. Set credentials for at least one of: "
            "Azure OpenAI, OpenAI, or Google Gemini in .env"
        )

    last_error: Exception | None = None
    for name, extractor in extractors:
        try:
            logger.info("Trying %s for menu extraction...", name)
            return extractor.extract(url, text)
        except Exception as e:
            logger.warning("Provider %s failed: %s", name, e)
            last_error = e
            continue

    raise RuntimeError(
        f"All LLM providers failed. Last error: {last_error}"
    )
