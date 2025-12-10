"""Configuration management for Supplier Hub backend.

Handles environment variables, settings, and app configuration.
"""

import os
from typing import Optional
from enum import Enum


class Environment(str, Enum):
    """Application environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings:
    """Application settings.
    
    Loaded from environment variables with sensible defaults.
    Follows 12-factor app principles.
    """

    # Environment
    ENVIRONMENT: Environment = Environment(
        os.getenv("ENVIRONMENT", "development")
    )
    DEBUG: bool = ENVIRONMENT == Environment.DEVELOPMENT

    # API Configuration
    API_TITLE: str = "Supplier Hub API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "RESTful API for supplier management and search"

    # Server
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 8000))
    RELOAD: bool = DEBUG

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    if os.getenv("CORS_ORIGINS"):
        CORS_ORIGINS.extend(os.getenv("CORS_ORIGINS", "").split(","))

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000
    MIN_PAGE_SIZE: int = 1

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Features
    ENABLE_SEARCH: bool = True
    ENABLE_FILTERS: bool = True
    ENABLE_FAVORITES: bool = True
    ENABLE_NOTES: bool = True

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production."""
        return cls.ENVIRONMENT == Environment.PRODUCTION

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development."""
        return cls.ENVIRONMENT == Environment.DEVELOPMENT


settings = Settings()