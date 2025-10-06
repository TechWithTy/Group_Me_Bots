"""
Core configuration settings for the Telegram API service.
"""
from __future__ import annotations

import secrets
from typing import List, Optional, Union

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings
    from pydantic.fields import Field

from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    """Application settings."""

    # Use .env file for configuration
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    # Project
    PROJECT_NAME: str = "GroupMint Telegram API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Telegram Bot API for GroupMint e-commerce platform"
    API_V1_STR: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        """Parse CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./telegram.db"

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""

    # External APIs
    SHOPIFY_ACCESS_TOKEN: str = ""
    SHOPIFY_STORE_URL: str = ""
    WOOCOMMERCE_URL: str = ""
    WOOCOMMERCE_CONSUMER_KEY: str = ""
    WOOCOMMERCE_CONSUMER_SECRET: str = ""

    # Payment
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Redis (for caching and sessions)
    REDIS_URL: str = "redis://localhost:6379"

    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60


settings = Settings()
