"""Web app configuration."""

from __future__ import annotations

import os

# App password for simple auth gate
APP_PASSWORD = os.environ["APP_PASSWORD"]

# CORS origins (comma-separated in env, defaults to Vite dev server)
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if o.strip()
]
