"""Build the poll Adaptive Card with Action.Execute for group chat ordering."""

from __future__ import annotations

from typing import Any


def build_order_poll_card(
    restaurant_name: str,
    items: list[dict[str, str]],
    conversation_id: str,
) -> dict[str, Any]:
    """Create an Adaptive Card poll where users can multi-select menu items.

    Uses Action.Execute (Universal Actions) so the bot receives invoke
    activities and can update the card in-place with order summaries.

    Args:
        restaurant_name: Display name of the restaurant.
        items: List of dicts with 'title' and 'value' keys.
        conversation_id: Teams conversation ID for order tracking.
    """
    choices = [{"title": item["title"], "value": item["value"]} for item in items]

    card: dict[str, Any] = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "body": [
            {
                "type": "TextBlock",
                "text": f"Lunch Order: {restaurant_name}",
                "weight": "Bolder",
                "size": "Large",
                "wrap": True,
                "style": "heading",
            },
            {
                "type": "TextBlock",
                "text": "Select what you'd like to order, then hit Submit.",
                "wrap": True,
                "spacing": "Small",
            },
            {
                "type": "Input.ChoiceSet",
                "id": "menu_selection",
                "label": "Menu items",
                "style": "expanded",
                "isMultiSelect": True,
                "choices": choices,
            },
        ],
        "actions": [
            {
                "type": "Action.Execute",
                "title": "Submit Order",
                "verb": "submit_order",
                "data": {
                    "conversation_id": conversation_id,
                    "restaurant_name": restaurant_name,
                },
            }
        ],
    }
    return card
