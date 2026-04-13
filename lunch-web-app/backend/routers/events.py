"""SSE events router - live order updates."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from .. import sessions as store
from ..models import SessionResponse

router = APIRouter(tags=["events"])


@router.get("/sessions/{session_id}/events")
async def session_events(session_id: str):
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    queue = store.subscribe(session_id)

    async def event_stream():
        try:
            # Send initial state
            yield f"data: {SessionResponse.from_session(session).model_dump_json()}\n\n"
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            store.unsubscribe(session_id, queue)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
