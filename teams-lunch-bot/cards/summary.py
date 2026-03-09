"""Build the order summary Adaptive Card shown after users submit."""

from __future__ import annotations

from typing import Any


def build_order_summary_card(
    restaurant_name: str,
    orders: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Create an Adaptive Card summarizing all orders.

    Args:
        restaurant_name: Display name of the restaurant.
        orders: Dict of user_id -> {name: str, items: list[str]}.
    """
    body: list[dict[str, Any]] = [
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
            "text": f"{len(orders)} {'person has' if len(orders) == 1 else 'people have'} ordered",
            "wrap": True,
            "spacing": "Small",
            "isSubtle": True,
        },
    ]

    # Add each person's order
    for user_id, order in orders.items():
        name = order["name"]
        items = order["items"]
        items_text = ", ".join(items) if items else "Nothing selected"

        body.append({
            "type": "ColumnSet",
            "spacing": "Small",
            "columns": [
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"**{name}:**",
                            "wrap": True,
                        }
                    ],
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": items_text,
                            "wrap": True,
                        }
                    ],
                },
            ],
        })

    # Aggregate counts for the combined order
    item_counts: dict[str, int] = {}
    for order in orders.values():
        for item in order["items"]:
            item_counts[item] = item_counts.get(item, 0) + 1

    if item_counts:
        body.append({
            "type": "TextBlock",
            "text": "Combined Order",
            "weight": "Bolder",
            "size": "Medium",
            "spacing": "Large",
            "wrap": True,
        })
        for item_name, count in sorted(item_counts.items()):
            body.append({
                "type": "TextBlock",
                "text": f"- {item_name} x{count}",
                "wrap": True,
                "spacing": "None",
            })

    card: dict[str, Any] = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "body": body,
    }
    return card
