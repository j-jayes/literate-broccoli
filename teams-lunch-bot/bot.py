"""Teams Lunch Order Bot.

Handles:
1. Mentions in group chats -> scrapes restaurant menu -> sends poll card
2. Action.Execute from poll card -> tracks orders per user -> updates card
"""

from __future__ import annotations

import logging
import re
import sys
import os
from typing import Any

from botbuilder.core import CardFactory, TurnContext
from botbuilder.schema import Activity, ActivityTypes

# Add parent directory to path so we can import the existing scraper
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.menu import get_restaurant_menu
from src.models.schemas import ExtractedMenuItem
from cards import build_order_poll_card, build_order_summary_card

logger = logging.getLogger(__name__)

# In-memory order store: conversation_id -> {user_id: {name, items}}
_orders: dict[str, dict[str, dict[str, Any]]] = {}


def _strip_mention(text: str, bot_name: str) -> str:
    """Remove the @mention of the bot from the message text."""
    # Teams wraps mentions in <at>BotName</at> tags
    cleaned = re.sub(r"<at>[^<]*</at>", "", text).strip()
    return cleaned


class LunchBot:
    """Stateless bot handler - all state is in the _orders dict."""

    async def on_message(self, turn_context: TurnContext) -> None:
        """Handle incoming messages. Expected format: @LunchBot <restaurant or URL>."""
        text = turn_context.activity.text or ""
        bot_name = turn_context.activity.recipient.name or "LunchBot"
        query = _strip_mention(text, bot_name)

        if not query:
            await turn_context.send_activity(
                "Tell me a restaurant name or paste a menu URL. "
                "Example: `@LunchBot Pizzeria Napoli` or "
                "`@LunchBot https://example.com/menu`"
            )
            return

        # Determine if the input is a URL or restaurant name
        url = None
        restaurant_name = query
        if query.startswith("http://") or query.startswith("https://"):
            url = query
            # Use domain as a fallback name
            restaurant_name = url.split("//")[-1].split("/")[0]

        # Send a "working on it" message
        await turn_context.send_activity(
            f"Looking up the menu for **{restaurant_name}**... "
            "This may take a moment while I navigate the website."
        )

        try:
            # Reuse the existing scraper pipeline
            card_json = await get_restaurant_menu(restaurant_name, menu_url=url)

            # The existing card uses Action.Submit - we need to rebuild it
            # with Action.Execute for Universal Actions support in group chats.
            # Extract items from the card choices to rebuild.
            items = _extract_items_from_card(card_json)
            conversation_id = turn_context.activity.conversation.id

            # Build the poll card with Action.Execute
            poll_card = build_order_poll_card(restaurant_name, items, conversation_id)

            # Initialize order tracking for this conversation
            _orders[conversation_id] = {}

            attachment = CardFactory.adaptive_card(poll_card)
            await turn_context.send_activity(
                Activity(type=ActivityTypes.message, attachments=[attachment])
            )

        except Exception as e:
            logger.exception("Failed to get menu")
            await turn_context.send_activity(
                f"Sorry, I couldn't get the menu: {e}\n\n"
                "Try providing a direct URL to the menu page."
            )

    async def on_adaptive_card_invoke(
        self, turn_context: TurnContext, invoke_value: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle Action.Execute from the poll Adaptive Card."""
        action = invoke_value.get("action", {})
        verb = action.get("verb", "")
        data = action.get("data", {})

        if verb == "submit_order":
            return await self._handle_order_submit(turn_context, data)

        return {"statusCode": 200, "type": "application/vnd.microsoft.activity.message", "value": "Unknown action."}

    async def _handle_order_submit(
        self, turn_context: TurnContext, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process a user's order submission and return an updated card."""
        conversation_id = data.get("conversation_id", "")
        restaurant_name = data.get("restaurant_name", "Restaurant")
        selected_items = data.get("menu_selection", "")

        # menu_selection comes as comma-separated values from isMultiSelect
        if isinstance(selected_items, str):
            item_list = [s.strip() for s in selected_items.split(",") if s.strip()]
        else:
            item_list = selected_items if selected_items else []

        # Get user info
        user = turn_context.activity.from_property
        user_id = user.id if user else "unknown"
        user_name = user.name if user else "Someone"

        # Update orders
        if conversation_id not in _orders:
            _orders[conversation_id] = {}

        _orders[conversation_id][user_id] = {
            "name": user_name,
            "items": item_list,
        }

        # Build summary card
        orders = _orders[conversation_id]
        summary_card = build_order_summary_card(restaurant_name, orders)

        return {
            "statusCode": 200,
            "type": "application/vnd.microsoft.card.adaptive",
            "value": summary_card,
        }


def _extract_items_from_card(card: dict[str, Any]) -> list[dict[str, str]]:
    """Extract choice items from the existing card format."""
    items = []
    for body_item in card.get("body", []):
        if body_item.get("type") == "Input.ChoiceSet":
            for choice in body_item.get("choices", []):
                items.append({
                    "title": choice["title"],
                    "value": choice["value"],
                })
    return items
