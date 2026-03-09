"""Simple password-based auth router."""

from __future__ import annotations

import secrets

from fastapi import APIRouter, Cookie, HTTPException, Response

from ..config import APP_PASSWORD
from ..models import AuthRequest

router = APIRouter(tags=["auth"])

# Server-side token store (in-memory)
_valid_tokens: set[str] = set()


def require_auth(auth_token: str | None = Cookie(default=None)) -> str:
    """Dependency that checks the auth cookie."""
    if not auth_token or auth_token not in _valid_tokens:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return auth_token


@router.post("/auth")
async def login(body: AuthRequest, response: Response):
    if body.password != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Wrong password")
    token = secrets.token_hex(16)
    _valid_tokens.add(token)
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400,  # 24 hours
    )
    return {"ok": True}


@router.get("/auth/check")
async def check_auth(auth_token: str | None = Cookie(default=None)):
    if auth_token and auth_token in _valid_tokens:
        return {"authenticated": True}
    raise HTTPException(status_code=401, detail="Not authenticated")
