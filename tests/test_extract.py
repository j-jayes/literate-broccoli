"""Tests for LLM menu extraction with mocked providers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.models.schemas import ExtractedMenu, ExtractedMenuItem, MenuCategory
from src.scraper.extract import (
    AzureOpenAIExtractor,
    GeminiExtractor,
    OpenAIExtractor,
    extract_menu,
)

FAKE_ITEMS = [
    ExtractedMenuItem(name="Margherita", price=95, category=MenuCategory.main),
    ExtractedMenuItem(name="Cola", price=25, category=MenuCategory.drink),
]

FAKE_MENU = ExtractedMenu(items=FAKE_ITEMS)


def _mock_openai_completion():
    """Create a mock completion object matching OpenAI's structured output."""
    msg = MagicMock()
    msg.parsed = FAKE_MENU
    choice = MagicMock()
    choice.message = msg
    completion = MagicMock()
    completion.choices = [choice]
    return completion


class TestAzureOpenAIExtractor:
    @patch("src.scraper.extract.settings")
    def test_extract_calls_azure(self, mock_settings):
        mock_settings.azure_openai_endpoint = "https://test.openai.azure.com/"
        mock_settings.azure_openai_api_key = "test-key"
        mock_settings.azure_openai_api_version = "2024-10-21"
        mock_settings.azure_openai_deployment = "gpt-4o"

        with patch("src.scraper.extract.AzureOpenAIExtractor.extract") as mock_extract:
            mock_extract.return_value = FAKE_ITEMS
            extractor = AzureOpenAIExtractor()
            items = extractor.extract("https://example.com", "Pizza 95kr")
            assert len(items) == 2
            assert items[0].name == "Margherita"


class TestOpenAIExtractor:
    @patch("src.scraper.extract.settings")
    def test_extract_calls_openai(self, mock_settings):
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4o-mini"

        with patch("src.scraper.extract.OpenAIExtractor.extract") as mock_extract:
            mock_extract.return_value = FAKE_ITEMS
            extractor = OpenAIExtractor()
            items = extractor.extract("https://example.com", "Pizza 95kr")
            assert len(items) == 2


class TestFallbackChain:
    @patch("src.scraper.extract._get_extractors")
    def test_fallback_on_failure(self, mock_get):
        """First provider fails, second succeeds."""
        failing = MagicMock()
        failing.extract.side_effect = RuntimeError("rate limited")
        succeeding = MagicMock()
        succeeding.extract.return_value = FAKE_ITEMS

        mock_get.return_value = [("Azure", failing), ("OpenAI", succeeding)]
        items = extract_menu("https://example.com", "some text")
        assert len(items) == 2
        assert failing.extract.called
        assert succeeding.extract.called

    @patch("src.scraper.extract._get_extractors")
    def test_all_fail_raises(self, mock_get):
        """All providers fail -> raises RuntimeError."""
        failing = MagicMock()
        failing.extract.side_effect = RuntimeError("fail")
        mock_get.return_value = [("Azure", failing)]

        with pytest.raises(RuntimeError, match="All LLM providers failed"):
            extract_menu("https://example.com", "text")

    @patch("src.scraper.extract._get_extractors")
    def test_no_providers_raises(self, mock_get):
        mock_get.return_value = []
        with pytest.raises(RuntimeError, match="No LLM provider configured"):
            extract_menu("https://example.com", "text")
