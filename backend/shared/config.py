"""
shared/config.py

Single source of truth for all configuration.
Everything is read from environment variables (via .env in development).

Usage:
    from shared.config import settings

    db_url = settings.database_url
    debug  = settings.debug
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    app_env: str = Field(default="development")
    app_debug: bool = Field(default=True)
    app_port: int = Field(default=8000)

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/sih26108"
    )

    # ------------------------------------------------------------------
    # Document storage
    # ------------------------------------------------------------------
    upload_dir: str = Field(default="./uploads")
    analysis_database_path: str = Field(default="./data/sih26108.db")

    # ------------------------------------------------------------------
    # LLM / AI
    # ------------------------------------------------------------------
    openai_api_key: str = Field(default="")
    google_api_key: str = Field(default="")        # Gemini
    # Default Gemini model. Override via GEMINI_MODEL if Google changes model
    # availability — verify the new name against `client.models.list()` first.
    gemini_model: str = Field(default="gemini-3.6-flash")
    aiml_service_url: str = Field(default="")      # if ML team runs as HTTP service
    aiml_timeout_seconds: float = Field(default=30.0)
    semantic_retrieval_enabled: bool = Field(default=False)

    # ------------------------------------------------------------------
    # Bhashini (low priority — wire in later)
    # ------------------------------------------------------------------
    bhashini_api_key: str = Field(default="")
    bhashini_user_id: str = Field(default="")

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def aiml_is_http_service(self) -> bool:
        """True if AI/ML team runs as a separate HTTP service."""
        return bool(self.aiml_service_url)


@lru_cache
def get_settings() -> Settings:
    """
    Return the singleton Settings instance.
    Cached after first call — safe to import anywhere.
    """
    return Settings()


# Convenience alias — most code just does `from shared.config import settings`
settings: Settings = get_settings()
