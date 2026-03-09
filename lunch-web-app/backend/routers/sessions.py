"""Sessions router - CRUD for lunch sessions, orders, and CSV download."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from .. import sessions as store
from ..models import CreateSessionRequest, SessionResponse, SubmitOrderRequest
from .auth import require_auth

router = APIRouter(tags=["sessions"])


@router.post("/sessions", response_model=SessionResponse)
async def create_session(body: CreateSessionRequest, _token: str = Depends(require_auth)):
    session = store.create_session(body.restaurant_name, body.items, body.description)
    return session


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/sessions/{session_id}/orders", response_model=SessionResponse)
async def submit_order(session_id: str, body: SubmitOrderRequest):
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    valid_names = {item.name for item in session.items}
    invalid = [i for i in body.selected_items if i not in valid_names]
    if invalid:
        raise HTTPException(status_code=422, detail=f"Invalid menu items: {invalid}")
    session = await store.add_order(session_id, body.name, body.selected_items)
    return session


@router.get("/sessions/{session_id}/csv")
async def download_csv(session_id: str):
    csv = store.get_csv(session_id)
    if csv is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return PlainTextResponse(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=lunch-order-{session_id[:8]}.csv"},
    )
