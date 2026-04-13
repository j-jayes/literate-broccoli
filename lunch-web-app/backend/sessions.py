"""Session store with Azure Blob Storage persistence and SSE event bus.

Each session is stored as a single JSON blob at:
  {AZURE_STORAGE_CONTAINER_NAME}/{session_id}.json

Optimistic concurrency: add_order reads the blob ETag, mutates in memory,
then re-uploads with If-Match so concurrent writers don't silently overwrite
each other (Azure returns 412 → we retry once with a fresh read).

Fallback: if AZURE_STORAGE_CONNECTION_STRING is not set the store falls back
to the legacy /tmp/sessions.json file so local development still works.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from decimal import Decimal

from .models import LunchSession, MenuItem, Order, RestaurantMenu, SessionResponse

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
_CONTAINER_NAME = os.environ.get("AZURE_STORAGE_CONTAINER_NAME", "lunch-sessions")
_SESSIONS_FILE = os.environ.get("SESSIONS_FILE", "/tmp/sessions.json")  # legacy fallback

_USE_BLOB = bool(_CONNECTION_STRING)

# ── In-memory cache (warm reads, always consistent with blob on write) ─────────

_cache: dict[str, LunchSession] = {}

# ── SSE subscriber queues: session_id -> list of asyncio.Queue ────────────────

_event_queues: dict[str, list[asyncio.Queue]] = {}

# ── Blob helpers ──────────────────────────────────────────────────────────────

def _get_blob_client(session_id: str):
    from azure.storage.blob import BlobServiceClient
    service = BlobServiceClient.from_connection_string(_CONNECTION_STRING)
    return service.get_blob_client(container=_CONTAINER_NAME, blob=f"{session_id}.json")


def _load_session_from_blob(session_id: str) -> tuple[LunchSession, str] | tuple[None, None]:
    """Download a session blob and return (session, etag). Returns (None, None) if not found."""
    try:
        client = _get_blob_client(session_id)
        download = client.download_blob()
        etag: str = download.properties.etag
        raw = json.loads(download.readall())
        raw = _migrate_legacy(raw)
        return LunchSession.model_validate(raw), etag
    except Exception as exc:
        if "BlobNotFound" in str(exc) or "404" in str(exc):
            return None, None
        logger.warning("Failed to load session %s from blob: %s", session_id, exc)
        return None, None


def _save_session_to_blob(session: LunchSession, if_match: str | None = None) -> str:
    """Upload session JSON to blob. Returns new ETag. Raises on 412 conflict."""
    client = _get_blob_client(str(session.id))
    data = session.model_dump_json().encode()
    kwargs: dict = {"overwrite": True}
    if if_match:
        try:
            from azure.core.conditions import MatchConditions
            kwargs["etag"] = if_match
            kwargs["match_condition"] = MatchConditions.IfNotModified
        except ImportError:
            # azure-core version without MatchConditions — skip optimistic lock
            pass
    result = client.upload_blob(data, **kwargs)
    return result["etag"]


# ── Legacy file helpers (local dev fallback) ──────────────────────────────────

_legacy_loaded = False


def _migrate_legacy(raw: dict) -> dict:
    """Convert old single-restaurant format → new multi-restaurant format."""
    if "restaurants" not in raw and "restaurant_name" in raw:
        raw = dict(raw)
        raw["restaurants"] = [
            {"restaurant_name": raw.pop("restaurant_name"), "items": raw.pop("items", [])}
        ]
    return raw


def _load_legacy() -> None:
    global _legacy_loaded
    if _legacy_loaded:
        return
    _legacy_loaded = True
    try:
        if os.path.exists(_SESSIONS_FILE):
            with open(_SESSIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for session_id, raw in data.items():
                raw = _migrate_legacy(raw)
                _cache[session_id] = LunchSession.model_validate(raw)
                _event_queues[session_id] = []
            logger.info("Loaded %d sessions from %s", len(_cache), _SESSIONS_FILE)
    except Exception:
        logger.warning("Failed to load sessions from %s", _SESSIONS_FILE, exc_info=True)


def _save_legacy() -> None:
    try:
        data = {sid: json.loads(s.model_dump_json()) for sid, s in _cache.items()}
        with open(_SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        logger.warning("Failed to save sessions to %s", _SESSIONS_FILE, exc_info=True)


# ── Public API ────────────────────────────────────────────────────────────────

def create_session(
    restaurants: list[RestaurantMenu],
    description: str | None = None,
) -> LunchSession:
    session = LunchSession(restaurants=restaurants, description=description)
    sid = str(session.id)
    _cache[sid] = session
    _event_queues[sid] = []

    if _USE_BLOB:
        _save_session_to_blob(session)
        logger.info("Created session %s in blob storage", sid)
    else:
        _load_legacy()
        _save_legacy()

    return session


def get_session(session_id: str) -> LunchSession | None:
    # Serve from cache first
    if session_id in _cache:
        return _cache[session_id]

    if _USE_BLOB:
        session, _ = _load_session_from_blob(session_id)
        if session:
            _cache[session_id] = session
            if session_id not in _event_queues:
                _event_queues[session_id] = []
        return session
    else:
        _load_legacy()
        return _cache.get(session_id)


async def add_order(session_id: str, name: str, selected_items: list[str]) -> LunchSession | None:
    if _USE_BLOB:
        # Optimistic locking: read → mutate → write with If-Match
        for attempt in range(3):
            session, etag = _load_session_from_blob(session_id)
            if not session:
                return None
            session.orders[name] = Order(name=name, items=selected_items)
            try:
                _save_session_to_blob(session, if_match=etag)
                break
            except Exception as exc:
                if "412" in str(exc) or "ConditionNotMet" in str(exc):
                    logger.info("ETag conflict on attempt %d for session %s, retrying", attempt + 1, session_id)
                    if attempt == 2:
                        raise
                    await asyncio.sleep(0.1 * (attempt + 1))
                    continue
                raise
        _cache[session_id] = session
    else:
        _load_legacy()
        session = _cache.get(session_id)
        if not session:
            return None
        session.orders[name] = Order(name=name, items=selected_items)
        _save_legacy()

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
    session = _cache.get(session_id)
    if not session:
        return
    response = SessionResponse.from_session(session)
    data = response.model_dump_json()
    for queue in _event_queues.get(session_id, []):
        await queue.put(data)


def get_csv(session_id: str) -> str | None:
    session = get_session(session_id)
    if not session:
        return None

    # Build lookup maps: item_name -> (price, category, restaurant_name)
    price_map: dict[str, Decimal | None] = {}
    category_map: dict[str, str] = {}
    restaurant_map: dict[str, str] = {}
    for restaurant in session.restaurants:
        for item in restaurant.items:
            price_map[item.name] = item.price
            category_map[item.name] = item.category
            restaurant_map[item.name] = restaurant.restaurant_name

    lines = ["Name,Item,Price,Category,Restaurant"]
    for order in session.orders.values():
        for item_name in order.items:
            price = price_map.get(item_name, "")
            cat = category_map.get(item_name, "")
            rest = restaurant_map.get(item_name, "")
            lines.append(f"{order.name},{item_name},{price},{cat},{rest}")

    # Aggregated summary
    lines.append("")
    lines.append("Combined Order")
    lines.append("Item,Count,Price,Restaurant")
    from collections import Counter
    all_items: list[str] = []
    for order in session.orders.values():
        all_items.extend(order.items)
    counts = Counter(all_items)
    for item_name, count in sorted(counts.items()):
        price = price_map.get(item_name, "")
        rest = restaurant_map.get(item_name, "")
        lines.append(f"{item_name},{count},{price},{rest}")

    return "\n".join(lines)
