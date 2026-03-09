"""In-memory session store and SSE event bus."""

from __future__ import annotations

import asyncio
import json
from uuid import UUID

from .models import LunchSession, MenuItem, Order

# Session store: session_id -> LunchSession
_sessions: dict[str, LunchSession] = {}

# SSE subscriber queues: session_id -> list of asyncio.Queue
_event_queues: dict[str, list[asyncio.Queue]] = {}


def create_session(restaurant_name: str, items: list[MenuItem], description: str | None = None) -> LunchSession:
    session = LunchSession(restaurant_name=restaurant_name, items=items, description=description)
    _sessions[str(session.id)] = session
    _event_queues[str(session.id)] = []
    return session


def get_session(session_id: str) -> LunchSession | None:
    return _sessions.get(session_id)


async def add_order(session_id: str, name: str, selected_items: list[str]) -> LunchSession | None:
    session = _sessions.get(session_id)
    if not session:
        return None
    session.orders[name] = Order(name=name, items=selected_items)
    await _notify_subscribers(session_id)
    return session


def subscribe(session_id: str) -> asyncio.Queue:
    queue: asyncio.Queue = asyncio.Queue()
    if session_id not in _event_queues:
        _event_queues[session_id] = []
    _event_queues[session_id].append(queue)
    return queue


def unsubscribe(session_id: str, queue: asyncio.Queue) -> None:
    if session_id in _event_queues:
        try:
            _event_queues[session_id].remove(queue)
        except ValueError:
            pass


async def _notify_subscribers(session_id: str) -> None:
    session = _sessions.get(session_id)
    if not session:
        return
    data = session.model_dump_json()
    for queue in _event_queues.get(session_id, []):
        await queue.put(data)


def get_csv(session_id: str) -> str | None:
    session = _sessions.get(session_id)
    if not session:
        return None

    # Build price lookup
    price_map: dict[str, Decimal | None] = {}
    category_map: dict[str, str] = {}
    for item in session.items:
        price_map[item.name] = item.price
        category_map[item.name] = item.category

    lines = ["Name,Item,Price,Category"]
    for order in session.orders.values():
        for item_name in order.items:
            price = price_map.get(item_name, "")
            cat = category_map.get(item_name, "")
            lines.append(f"{order.name},{item_name},{price},{cat}")

    # Aggregated summary
    lines.append("")
    lines.append("Combined Order")
    lines.append("Item,Count,Price")
    from collections import Counter
    all_items: list[str] = []
    for order in session.orders.values():
        all_items.extend(order.items)
    counts = Counter(all_items)
    for item_name, count in sorted(counts.items()):
        price = price_map.get(item_name, "")
        lines.append(f"{item_name},{count},{price}")

    return "\n".join(lines)
