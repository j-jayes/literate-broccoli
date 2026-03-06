"""Build an Adaptive Card poll from extracted menu items."""

from __future__ import annotations

from typing import Any

from src.models.schemas import ExtractedMenuItem


def build_poll_card(
    restaurant_name: str,
    items: list[ExtractedMenuItem],
) -> dict[str, Any]:
    """Create an Adaptive Card JSON for a Teams poll.

    Returns a flat-list poll where each menu item is a selectable choice.
    Users pick the item they want for lunch.
    """
    choices = []
    for item in items:
        label = item.name
        if item.price is not None:
            label += f" ({item.price} kr)"
        if item.description:
            label += f" - {item.description}"
        choices.append({
            "title": label,
            "value": item.name,
        })

    card: dict[str, Any] = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "body": [
            {
                "type": "TextBlock",
                "text": f"Lunch Poll: {restaurant_name}",
                "weight": "Bolder",
                "size": "Large",
                "wrap": True,
            },
            {
                "type": "TextBlock",
                "text": "What would you like to order?",
                "wrap": True,
            },
            {
                "type": "Input.ChoiceSet",
                "id": "lunch_choice",
                "label": "Pick your lunch",
                "style": "expanded",
                "isRequired": True,
                "choices": choices,
            },
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit",
            }
        ],
    }
    return card
