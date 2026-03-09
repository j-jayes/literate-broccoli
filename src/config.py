"""Configuration for the MCP menu server."""

from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Azure OpenAI (primary)
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-10-21"

    # OpenAI (fallback)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    # Google Gemini (search + LLM fallback)
    google_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"

    # Server
    mcp_server_name: str = "lunch-menu-poll"
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


settings = Settings()
