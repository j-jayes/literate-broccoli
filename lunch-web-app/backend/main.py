"""FastAPI entry point for the Lunch Web App."""

from __future__ import annotations

import os
import sys

# Add repo root to sys.path so we can import the existing scraper from src/
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import CORS_ORIGINS
from .routers import auth, events, scrape, sessions

app = FastAPI(title="Lunch Order App", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth.router, prefix="/api")
app.include_router(scrape.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(events.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Serve React frontend in production (built files in frontend/dist)
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.is_dir():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="assets")

    # Catch-all: serve index.html for client-side routing
    from fastapi.responses import FileResponse

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = _frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_frontend_dist / "index.html"))
