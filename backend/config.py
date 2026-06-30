"""
Enterprise AI Customer Intelligence Platform — Backend Configuration

Centralizes all environment-based settings using pydantic-settings.
Import `settings` from this module wherever configuration is needed.

Usage:
    from backend.config import settings
    print(settings.DATABASE_URL)
"""

from __future__ import annotations


# Configuration will be implemented in Sprint 1 using pydantic-settings.
# This placeholder ensures the backend package is importable and the
# config module exists for future imports.
#
# Example (Sprint 1):
#
#   from pydantic_settings import BaseSettings
#
#   class Settings(BaseSettings):
#       DATABASE_URL: str
#       REDIS_URL: str
#       ...
#       class Config:
#           env_file = ".env"
#
#   settings = Settings()
