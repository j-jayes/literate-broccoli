"""Tests for Adaptive Card poll generation."""

from __future__ import annotations

from decimal import Decimal

from src.cards.poll import build_poll_card
from src.models.schemas import ExtractedMenuItem, MenuCategory


def test_build_poll_card_basic():
    items = [
        ExtractedMenuItem(name="Margherita", price=Decimal("95"), category=MenuCategory.main),
        ExtractedMenuItem(name="Pepperoni", price=Decimal("105"), category=MenuCategory.main),
        ExtractedMenuItem(name="Cola", price=Decimal("25"), category=MenuCategory.drink),
    ]
    card = build_poll_card("Test Pizza", items)

    assert card["type"] == "AdaptiveCard"
    assert card["version"] == "1.5"

    # Title
    title_block = card["body"][0]
    assert "Test Pizza" in title_block["text"]

    # Choices
    choice_set = card["body"][2]
    assert choice_set["type"] == "Input.ChoiceSet"
    assert len(choice_set["choices"]) == 3
    assert choice_set["choices"][0]["title"] == "Margherita (95 kr)"
    assert choice_set["choices"][0]["value"] == "Margherita"

    # Submit button
    assert len(card["actions"]) == 1
    assert card["actions"][0]["type"] == "Action.Submit"


def test_build_poll_card_no_price():
    items = [
        ExtractedMenuItem(name="Daily Special", category=MenuCategory.main),
    ]
    card = build_poll_card("Bistro", items)
    choices = card["body"][2]["choices"]
    assert choices[0]["title"] == "Daily Special"


def test_build_poll_card_with_description():
    items = [
        ExtractedMenuItem(
            name="Caesar Salad",
            price=Decimal("120"),
            category=MenuCategory.main,
            description="Romaine, parmesan, croutons",
        ),
    ]
    card = build_poll_card("Salad Bar", items)
    choices = card["body"][2]["choices"]
    assert "Romaine, parmesan, croutons" in choices[0]["title"]


def test_build_poll_card_empty_items():
    card = build_poll_card("Empty Restaurant", [])
    choices = card["body"][2]["choices"]
    assert choices == []
