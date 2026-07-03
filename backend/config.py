"""
Enterprise AI Customer Intelligence Platform — Application Configuration.

Centralizes all environment-based settings using pydantic-settings.
Configuration is loaded from environment variables with .env file fallback.

Usage:
    from backend.config import settings

    print(settings.DATABASE_URL)
    print(settings.APP_ENV)

Design Decisions:
    - Pydantic Settings validates types at startup (fail-fast).
    - Computed DATABASE_URL avoids duplication and drift between parts.
    - Frozen model prevents runtime mutation of configuration.
    - .env file is optional; environment variables always take precedence.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    Attributes are grouped by service. All values have sensible development
    defaults so the application can start locally with minimal setup.

    Environment variables override .env values (standard 12-factor behavior).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        frozen=True,
    )

    # ---- Application -------------------------------------------------------
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ---- PostgreSQL ---------------------------------------------------------
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "customer_intelligence"
    DATABASE_USER: str = "platform_user"
    DATABASE_PASSWORD: str = "CHANGE_ME"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        """Build SQLAlchemy-compatible async database URL from parts."""
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Synchronous URL for Alembic migrations (asyncpg cannot be used)."""
        return (
            f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    # ---- Redis --------------------------------------------------------------
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "CHANGE_ME"
    REDIS_DB: int = 0
    REDIS_CACHE_TTL_SECONDS: int = 300  # 5 minutes default

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_URL(self) -> str:
        """Build Redis connection URL from parts."""
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ---- RabbitMQ -----------------------------------------------------------
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "platform_user"
    RABBITMQ_PASSWORD: str = "CHANGE_ME"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def RABBITMQ_URL(self) -> str:
        """Build AMQP connection URL from parts."""
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"
        )

    # ---- Celery -------------------------------------------------------------
    @computed_field  # type: ignore[prop-decorator]
    @property
    def CELERY_BROKER_URL(self) -> str:
        """Celery uses RabbitMQ as its message broker."""
        return self.RABBITMQ_URL

    @computed_field  # type: ignore[prop-decorator]
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        """Celery stores task results in Redis DB 1 (separate from cache DB 0)."""
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/1"

    # ---- Security -----------------------------------------------------------
    JWT_SECRET: str = "CHANGE_ME_USE_A_LONG_RANDOM_STRING"

    # ---- OpenAI -------------------------------------------------------------
    OPENAI_API_KEY: str = "sk-CHANGE_ME"

    # ---- Data Paths ---------------------------------------------------------
    DATA_RAW_PATH: str = "data/raw"
    DATA_PROCESSED_PATH: str = "data/processed"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Factory function for dependency injection.

    Uses lru_cache so the Settings object is created exactly once,
    parsed and validated on first call, then reused for the process lifetime.
    """
    return Settings()


# Module-level convenience instance for simple imports.
settings = get_settings()
